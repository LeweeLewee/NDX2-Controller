"""Bounded in-memory cache for artwork URLs returned by native TIDAL metadata."""
from collections import OrderedDict
import re
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


def preview_source_url(url):
    """Keep returned identity; fetch a bounded rendition only for canonical TIDAL covers."""
    validate_artwork_url(url)
    match = re.fullmatch(r'(https://resources\.tidal\.com/images/[0-9a-f]{8}/[0-9a-f]{4}/[0-9a-f]{4}/[0-9a-f]{4}/[0-9a-f]{12}/)([0-9]{1,4})x([0-9]{1,4})\.jpg', url)
    if match and max(int(match[2]), int(match[3])) > 1024:
        return match[1] + '320x320.jpg'
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
        with self.opener.open(urllib.request.Request(preview_source_url(url), headers={'Accept': 'image/jpeg'}), timeout=8) as response:
            data = response.read(MAX_IMAGE_BYTES + 1)
        if len(data) > MAX_IMAGE_BYTES or not data.startswith(b'\xff\xd8\xff'):
            raise ValueError('Artwork is oversized or not JPEG')
        self.images[url] = data
        while len(self.images) > self.capacity:
            self.images.popitem(last=False)
        return data
