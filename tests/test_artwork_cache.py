import io
import pathlib
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / 'tools'))
from artwork_cache import ArtworkCache, MAX_IMAGE_BYTES, preview_source_url


class Opener:
    def __init__(self, data=b'\xff\xd8\xfftest'):
        self.data, self.calls = data, 0
    def open(self, request, timeout):
        self.calls += 1
        self.url = request.full_url
        return io.BytesIO(self.data)


class ArtworkTests(unittest.TestCase):
    def test_no_arbitrary_hosts_or_credentials(self):
        opener = Opener()
        cache = ArtworkCache(opener)
        for url in ('http://resources.tidal.com/images/a.jpg', 'https://resources.tidal.com.evil/images/a.jpg', 'https://user@resources.tidal.com/images/a.jpg', 'https://resources.tidal.com/images/a.jpg?token=secret', 'https://192.168.1.1/images/a.jpg'):
            with self.assertRaises(ValueError):
                cache.get(url)
        self.assertEqual(opener.calls, 0)

    def test_lru_cache_avoids_download_and_evicts(self):
        opener = Opener()
        cache = ArtworkCache(opener, capacity=1)
        first, second = ('https://resources.tidal.com/images/'+n+'.jpg' for n in ('a','b'))
        cache.get(first);cache.get(first)
        self.assertEqual(opener.calls, 1)
        cache.get(second);cache.get(first)
        self.assertEqual(opener.calls, 3)
        self.assertEqual(len(cache.images), 1)

    def test_rejects_oversize_and_nonjpeg(self):
        for data in (b'<html>not an image', b'\xff\xd8\xff'+b'x'*MAX_IMAGE_BYTES):
            cache = ArtworkCache(Opener(data))
            with self.assertRaises(ValueError):
                cache.get('https://resources.tidal.com/images/a.jpg')
            self.assertEqual(len(cache.images), 0)

    def test_native_large_cover_uses_bounded_rendition_with_original_cache_identity(self):
        prefix = 'https://resources.tidal.com/images/12345678/1234/1234/1234/123456789abc/'
        returned = prefix + '1280x1280.jpg'
        opener = Opener()
        cache = ArtworkCache(opener)
        cache.get(returned)
        self.assertEqual(opener.url, prefix + '320x320.jpg')
        self.assertIn(returned, cache.images)
        cache.get(returned)
        self.assertEqual(opener.calls, 1)
        for suffix in ('80x80.jpg', '320x320.jpg', '640x640.jpg'):
            self.assertEqual(preview_source_url(prefix + suffix), prefix + suffix)
        other = 'https://resources.tidal.com/images/unknown/1280x1280.jpg'
        self.assertEqual(preview_source_url(other), other)
        for url in (returned + '?token=x', returned.replace('resources.tidal.com', 'evil.invalid')):
            with self.assertRaises(ValueError): preview_source_url(url)
