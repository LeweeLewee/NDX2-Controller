"""Bounded bridge-only JPEG normalization. No controller-supplied URLs."""
from collections import OrderedDict
import base64
import hashlib
import io
import re
import time

SIDE = 80
MAX_SIDE = 320
CHUNK_PIXELS = SIDE * SIDE
TTL = 60
MAX_SOURCE_BYTES = 1024 * 1024
MAX_SOURCE_SIDE = 1024
REFERENCE = re.compile(r'/artwork/[0-9a-f]{64}\.jpg')


def normalize(raw, side=SIDE, offset=0, *, with_digest=False):
    if type(side) is not int or not 1 <= side <= MAX_SIDE:
        raise ValueError("Artwork side")
    if type(offset) is not int or not 0 <= offset < side * side or offset % CHUNK_PIXELS:
        raise ValueError("Artwork offset")
    # Pillow stays on the bridge. Check headers before allocating decoded pixels.
    from PIL import Image
    if len(raw) > MAX_SOURCE_BYTES:
        raise ValueError('Artwork size')
    with Image.open(io.BytesIO(raw)) as image:
        if image.format != 'JPEG' or not (0 < image.width <= MAX_SOURCE_SIDE and 0 < image.height <= MAX_SOURCE_SIDE):
            raise ValueError('Artwork dimensions or format')
        image.load()  # truncated/corrupt images must fail
        small = image.convert('RGB').resize((side, side), Image.Resampling.LANCZOS)
        pixels = bytearray()
        rgb = small.tobytes()
        digest = hashlib.sha256(rgb).hexdigest()
        rgb = rgb[offset * 3:(offset + CHUNK_PIXELS) * 3]
        for r, g, b in zip(rgb[0::3], rgb[1::3], rgb[2::3]):
            value = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
            pixels.extend(value.to_bytes(2, 'big'))
        return (pixels.hex(), digest) if with_digest else pixels.hex()


MAX_JPEG_BYTES = 23040  # base64 <= 30720; leave room inside the 32-KiB envelope.


def normalize_jpeg(raw, side):
    from PIL import Image
    if len(raw) > MAX_SOURCE_BYTES or type(side) is not int or not 1 <= side <= MAX_SIDE:
        raise ValueError('Artwork size')
    with Image.open(io.BytesIO(raw)) as image:
        if image.format != 'JPEG' or not (0 < image.width <= MAX_SOURCE_SIDE and 0 < image.height <= MAX_SOURCE_SIDE):
            raise ValueError('Artwork dimensions or format')
        image.load()
        small = image.convert('RGB').resize((side, side), Image.Resampling.LANCZOS)
        for quality in (80, 65, 50, 35, 20):
            output = io.BytesIO()
            small.save(output, format='JPEG', quality=quality, optimize=True)
            encoded = output.getvalue()
            if len(encoded) <= MAX_JPEG_BYTES:
                return encoded, hashlib.sha256(encoded).hexdigest()
    raise ValueError('Artwork exceeds compressed response budget')


class ArtworkDelivery:
    def __init__(self, service, clock=time.monotonic):
        self.service, self.clock = service, clock
        self.registered = OrderedDict()
        self.cache = OrderedDict()

    def register(self, reference):
        self.prune()
        if not isinstance(reference, str) or not REFERENCE.fullmatch(reference):
            return
        if reference not in self.service.artwork_refs:
            return
        self.registered[reference] = self.clock() + TTL
        self.registered.move_to_end(reference)
        while len(self.registered) > 32:
            self.registered.popitem(last=False)

    def prune(self):
        now = self.clock()
        for key, expiry in list(self.registered.items()):
            if expiry <= now:
                del self.registered[key]
        for key, (expiry, _) in list(self.cache.items()):
            if expiry <= now or key[0] not in self.registered:
                del self.cache[key]

    def get_jpeg(self, reference, side=MAX_SIDE):
        self.prune()
        if reference not in self.registered or reference not in self.service.artwork_refs:
            return {'available': False}
        now = self.clock()
        key = (reference, side, 'jpeg')
        # Early revalidation performs a new source read; it never extends old bytes locally.
        if key in self.cache and self.cache[key][0] - now <= 10 and self.cache[key][1] is not None:
            del self.cache[key]
        if key not in self.cache:
            url = self.service.artwork_refs[reference]
            self.service.artwork.images.pop(url, None)
            try:
                image = normalize_jpeg(self.service.image(reference), side)
            except Exception:
                image = None
            finally:
                self.service.artwork.images.pop(url, None)
            self.cache[key] = (now + TTL, image)
            while len(self.cache) > 4:
                self.cache.popitem(last=False)
        expiry, image = self.cache[key]
        self.cache.move_to_end(key)
        valid = max(0, int((min(expiry, self.registered[reference]) - self.clock()) * 1000))
        if image is None or valid == 0:
            return {'available': False}
        encoded, digest = image
        return {'available': True, 'reference': reference, 'width': side, 'height': side,
                'format': 'jpeg-base64', 'image': base64.b64encode(encoded).decode('ascii'),
                'image_id': digest, 'valid_for_ms': valid}

    def get(self, reference, side=SIDE, offset=0):
        self.prune()
        if reference not in self.registered or reference not in self.service.artwork_refs:
            return {'available': False}
        now = self.clock()
        key = (reference, side, offset)
        if key not in self.cache:
            # Do not let the older source cache extend this cache's lifetime.
            url = self.service.artwork_refs[reference]
            self.service.artwork.images.pop(url, None)
            try:
                pixels = normalize(self.service.image(reference), side, offset, with_digest=True)
            except Exception:
                pixels = None
            finally:
                self.service.artwork.images.pop(url, None)
            self.cache[key] = (now + TTL, pixels)
            while len(self.cache) > 4:
                self.cache.popitem(last=False)
        expiry, pixels = self.cache[key]
        self.cache.move_to_end(key)
        valid = max(0, int((min(expiry, self.registered[reference]) - self.clock()) * 1000))
        if pixels is None or valid == 0:
            return {'available': False}
        pixels, digest = pixels
        result = {'available': True, 'reference': reference, 'width': side, 'height': side,
                  'format': 'rgb565be-hex', 'pixels': pixels, 'valid_for_ms': valid}
        if side != SIDE or offset:
            result.update(offset=offset, total_pixels=side * side, image_id=digest,
                          next_offset=offset + CHUNK_PIXELS if offset + CHUNK_PIXELS < side * side else None)
        return result


def fixture_jpeg(alternate=False):
    """Synthetic geometric test image, generated locally without network access."""
    from PIL import Image, ImageDraw
    image = Image.new('RGB', (240, 240), (44, 62, 78) if alternate else (57, 75, 55))
    draw = ImageDraw.Draw(image)
    draw.ellipse((30, 30, 210, 210), fill=(191, 152, 100) if alternate else (186, 204, 157))
    draw.ellipse((70, 70, 170, 170), fill=(44, 62, 78) if alternate else (57, 75, 55))
    draw.rectangle((0, 190, 239, 210), fill=(130, 151, 165) if alternate else (124, 147, 111))
    output = io.BytesIO(); image.save(output, format='JPEG'); return output.getvalue()


def fixture_portrait():
    """Original abstract portrait study for the fictional artist; no external image."""
    from PIL import Image, ImageDraw
    image = Image.new('RGB', (320, 320), (35, 44, 36))
    draw = ImageDraw.Draw(image)
    draw.rectangle((24, 0, 68, 319), fill=(88, 100, 70))
    draw.rectangle((236, 0, 270, 319), fill=(72, 83, 64))
    draw.ellipse((122, 50, 194, 126), fill=(157, 168, 135))
    draw.polygon([(112, 148), (200, 148), (224, 320), (88, 320)], fill=(102, 119, 88))
    output = io.BytesIO(); image.save(output, format='JPEG'); return output.getvalue()
