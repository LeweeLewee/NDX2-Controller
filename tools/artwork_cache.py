"""Bounded in-memory cache for artwork URLs returned by native TIDAL metadata."""
from collections import OrderedDict
import urllib.parse
import urllib.request
from naim_native_probe import NoRedirect

MAX_IMAGE_BYTES = 1024 * 1024


def validate_artwork_url(url):
    if not isinstance(url, str):
        raise ValueError('Expected a returned TIDAL JPEG artwork URL')
    parts = urllib.parse.urlsplit(url)
    if (parts.scheme != 'https' or parts.netloc != 'resources.tidal.com'
            or parts.query or parts.fragment or not parts.path.startswith('/images/')
            or not parts.path.endswith('.jpg')):
        raise ValueError('Expected a returned TIDAL JPEG artwork URL')
    return url


class ArtworkCache:
    def __init__(self, opener=None, capacity=8):
        if type(capacity) is not int or not 1 <= capacity <= 16:
            raise ValueError('Cache capacity must be 1..16 images')
        self.opener = opener or urllib.request.build_opener(NoRedirect())
        self.capacity = capacity
        self.images = OrderedDict()

    def get(self, url):
        validate_artwork_url(url)
        if url in self.images:
            self.images.move_to_end(url)
            return self.images[url]
        with self.opener.open(urllib.request.Request(url, headers={'Accept': 'image/jpeg'}), timeout=8) as response:
            data = response.read(MAX_IMAGE_BYTES + 1)
        if len(data) > MAX_IMAGE_BYTES or not data.startswith(b'\xff\xd8\xff'):
            raise ValueError('Artwork is oversized or not JPEG')
        self.images[url] = data
        while len(self.images) > self.capacity:
            self.images.popitem(last=False)
        return data
