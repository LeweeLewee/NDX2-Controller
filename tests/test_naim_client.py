import io
import json
import pathlib
import sys
import unittest
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / 'tools'))
from naim_client import NaimClient, playback_state


class FakeOpener:
    def __init__(self, payload=b'{}'):
        self.payload = payload
        self.requests = []

    def open(self, request, timeout):
        self.requests.append(request)
        return io.BytesIO(self.payload)


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.opener = FakeOpener()
        self.client = NaimClient('192.168.1.2', self.opener)

    def test_native_only_and_no_parameter_injection(self):
        for ref in ('https://audio.example/track.flac', 'inputs/upnp/1', 'inputs/tidal/tracks/1?cmd=logout', '../system', 'inputs/tidal/tracks/1/../../system'):
            with self.assertRaises(ValueError):
                self.client.play(ref)
        self.assertEqual(self.opener.requests, [])

    def test_native_queue_workflow(self):
        self.client.play('inputs/tidal/albums/123')
        self.client.play('inputs/tidal/tracks/456', 'next')
        self.client.move('inputs/playqueue/2', 'inputs/playqueue/1')
        self.client.remove('inputs/playqueue/2')
        self.client.select('inputs/playqueue/1')
        requests = self.opener.requests
        self.assertEqual([r.get_method() for r in requests], ['GET', 'GET', 'GET', 'DELETE', 'PUT'])
        self.assertIn('cmd=playNext', requests[1].full_url)
        params = urllib.parse.parse_qs(urllib.parse.urlsplit(requests[2].full_url).query)
        self.assertEqual(params['where'], ['inputs/playqueue/1'])
        self.assertTrue(all(r.data is None for r in requests))

    def test_live_state_mapping_and_unknown(self):
        for code, state in ((1, 'stopped'), ('2', 'playing'), ('3', 'paused'), ('99', 'unknown'), (None, 'unknown')):
            self.assertEqual(playback_state({'transportState': code}), state)

    def test_page_bounds_and_seek_units(self):
        for offset, limit in ((-1, 20), (0, 0), (0, 51), (True, 20)):
            with self.assertRaises(ValueError):
                self.client.browse(offset=offset, limit=limit)
        self.client.transport('seek', 123000)
        self.assertIn('position=123000', self.opener.requests[-1].full_url)
        with self.assertRaises(ValueError):
            self.client.transport('seek', -1)

    def test_bad_response_does_not_trigger_retry(self):
        for payload in (b'[]', b'not JSON', b'x' * (1024 * 1024 + 1)):
            opener = FakeOpener(payload)
            with self.assertRaises(ValueError):
                NaimClient('192.168.1.2', opener).play('inputs/tidal/tracks/1')
            self.assertEqual(len(opener.requests), 1)

    def test_public_address_rejected(self):
        for address in ('8.8.8.8', '127.0.0.1', 'example.com'):
            with self.assertRaises(ValueError):
                NaimClient(address)


if __name__ == '__main__':
    unittest.main()
