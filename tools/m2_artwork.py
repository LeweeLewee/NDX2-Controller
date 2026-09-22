"""Bounded bridge-only JPEG normalization. No controller-supplied URLs."""
from collections import OrderedDict
import io
import re
import time

SIDE = 80
TTL = 60
MAX_SOURCE_BYTES = 1024 * 1024
MAX_SOURCE_SIDE = 1024
REFERENCE = re.compile(r'/artwork/[0-9a-f]{64}\.jpg')


def normalize(raw):
    # Pillow stays on the bridge. Check headers before allocating decoded pixels.
    from PIL import Image
    if len(raw) > MAX_SOURCE_BYTES:
        raise ValueError('Artwork size')
    with Image.open(io.BytesIO(raw)) as image:
        if image.format != 'JPEG' or not (0 < image.width <= MAX_SOURCE_SIDE and 0 < image.height <= MAX_SOURCE_SIDE):
            raise ValueError('Artwork dimensions or format')
        image.load()  # truncated/corrupt images must fail
        small = image.convert('RGB').resize((SIDE, SIDE), Image.Resampling.LANCZOS)
        pixels = bytearray()
        rgb = small.tobytes()
        for r, g, b in zip(rgb[0::3], rgb[1::3], rgb[2::3]):
            value = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
            pixels.extend(value.to_bytes(2, 'big'))
        return pixels.hex()


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
            if expiry <= now or key not in self.registered:
                del self.cache[key]

    def get(self, reference):
        self.prune()
        if reference not in self.registered or reference not in self.service.artwork_refs:
            return {'available': False}
        now = self.clock()
        if reference not in self.cache:
            # Do not let the older source cache extend this cache's lifetime.
            url = self.service.artwork_refs[reference]
            self.service.artwork.images.pop(url, None)
            try:
                pixels = normalize(self.service.image(reference))
            except Exception:
                pixels = None
            finally:
                self.service.artwork.images.pop(url, None)
            self.cache[reference] = (now + TTL, pixels)
            while len(self.cache) > 4:
                self.cache.popitem(last=False)
        expiry, pixels = self.cache[reference]
        self.cache.move_to_end(reference)
        valid = max(0, int((min(expiry, self.registered[reference]) - self.clock()) * 1000))
        if pixels is None or valid == 0:
            return {'available': False}
        return {'available': True, 'reference': reference, 'width': SIDE, 'height': SIDE,
                'format': 'rgb565be-hex', 'pixels': pixels, 'valid_for_ms': valid}


def fixture_jpeg(alternate=False):
    """Synthetic geometric test image, generated locally without network access."""
    from PIL import Image, ImageDraw
    image = Image.new('RGB', (240, 240), (44, 62, 78) if alternate else (57, 75, 55))
    draw = ImageDraw.Draw(image)
    draw.ellipse((30, 30, 210, 210), fill=(191, 152, 100) if alternate else (186, 204, 157))
    draw.ellipse((70, 70, 170, 170), fill=(44, 62, 78) if alternate else (57, 75, 55))
    draw.rectangle((0, 190, 239, 210), fill=(130, 151, 165) if alternate else (124, 147, 111))
    output = io.BytesIO(); image.save(output, format='JPEG'); return output.getvalue()
