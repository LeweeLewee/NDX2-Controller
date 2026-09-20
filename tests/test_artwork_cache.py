import io
import pathlib
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / 'tools'))
from artwork_cache import ArtworkCache, MAX_IMAGE_BYTES


class Opener:
    def __init__(self, data=b'\xff\xd8\xfftest'):
        self.data, self.calls = data, 0
    def open(self, request, timeout):
        self.calls += 1
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
