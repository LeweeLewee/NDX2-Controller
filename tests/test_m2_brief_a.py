"""Offline Still Water bridge contract and authenticated transport coverage."""
from contextlib import closing
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
import ssl
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / 'tools'))
from m2_artwork import CHUNK_PIXELS, TTL, fixture_jpeg
from m2_bridge import Contract, FixtureService, server, MAX_RESPONSE
from m2_certificates import create
from m2_client import Client
from m2_security import Pairing, Vault


class BriefATests(unittest.TestCase):
    def setUp(self):
        self.now = 100.0
        self.service = FixtureService()
        self.vault = type('MemoryVault', (), {'data': {'commands': {}}})()
        self.contract = Contract(self.service, self.vault, lambda: self.now)
        self.reference = next(iter(self.service.fixture_images))

    def request(self, action, **args):
        reply = self.contract.handle('paired-display', dict(version=1, request_id='r' * 32,
                                                            action=action, args=args))
        self.assertLessEqual(len(json.dumps(reply).encode()), MAX_RESPONSE)
        return reply

    def report(self, level, charging=False, client_id='display-one'):
        return self.request('battery_report', level=level, charging=charging, client_id=client_id)

    def charge(self):
        return self.request('charge?')['data']

    def test_charge_window_boundaries_from_last_report(self):
        self.assertEqual(self.charge(), {'charge': 'no', 'reason': 'none'})
        for level in (0, 34, 35, 50, 74, 75, 100):
            for charging in (False, True):
                self.assertEqual(self.report(level, charging)['data'], {'accepted': True})
                expected = 'yes' if level < 35 or (level < 75 and charging) else 'no'
                self.assertEqual(self.charge(), {'charge': expected, 'reason': 'window'})
        self.assertEqual(self.service.naim.calls, [])
        self.assertEqual(self.vault.data['commands'], {})
        self.assertEqual(self.contract.fresh, {})

    def test_receipt_expiry_replacement_restart_and_read_does_not_refresh(self):
        self.report(20)
        self.now += 3599.999
        self.assertEqual(self.charge(), {'charge': 'yes', 'reason': 'window'})
        self.now = 3700.0
        self.assertEqual(self.charge(), {'charge': 'no', 'reason': 'stale'})
        self.report(80, True, 'other-display')
        self.assertEqual(self.charge(), {'charge': 'no', 'reason': 'window'})
        self.assertEqual(self.contract.last_battery_report,
                         dict(level=80, charging=True, client_id='other-display', received_at=self.now))
        self.contract = Contract(self.service, self.vault, lambda: self.now)
        self.assertEqual(self.charge(), {'charge': 'no', 'reason': 'none'})

    def test_fresh_no_becomes_stale_and_invalid_reports_cannot_restore_freshness(self):
        self.now += 7200
        self.assertEqual(self.charge(), {'charge': 'no', 'reason': 'none'})
        self.report(80, True)
        self.now += 3599.999
        self.assertEqual(self.charge(), {'charge': 'no', 'reason': 'window'})
        self.now += 0.001
        self.assertEqual(self.charge(), {'charge': 'no', 'reason': 'stale'})
        self.assertEqual(self.report(-1)['outcome'], 'rejected')
        self.now += 60
        self.assertEqual(self.charge(), {'charge': 'no', 'reason': 'stale'})
        self.report(50, False)
        self.assertEqual(self.charge(), {'charge': 'no', 'reason': 'window'})
        self.report(34)
        self.assertEqual(self.charge(), {'charge': 'yes', 'reason': 'window'})
        self.assertEqual(self.service.naim.calls, [])

    def test_invalid_reports_never_replace_or_refresh_last_report(self):
        self.report(20)
        old = dict(self.contract.last_battery_report)
        for args in ({}, {'level': 20}, *[dict(level=x, charging=False, client_id='display')
                     for x in (-1, 101, True, 2.5, '20', None, float('nan'))],
                     *[dict(level=20, charging=x, client_id='display') for x in (0, 'yes', None)],
                     *[dict(level=20, charging=False, client_id=x) for x in ('', 'a'*65, 'a b', None)],
                     dict(level=20, charging=False, client_id='display', received_at=0)):
            with self.subTest(args=args):
                self.now += 1
                self.assertEqual(self.request('battery_report', **args)['outcome'], 'rejected')
                self.assertEqual(self.contract.last_battery_report, old)
        self.assertEqual(self.request('charge?', client_id='display')['outcome'], 'rejected')

    def test_large_artwork_reassembly_matches_normalisation_and_cache_budget(self):
        from PIL import Image
        self.request('snapshot')
        chunks = []
        ids = set()
        for offset in range(0, 320 * 320, CHUNK_PIXELS):
            data = self.request('artwork', reference=self.reference, side=320, pixel_offset=offset)['data']
            self.assertTrue(data['available'])
            self.assertEqual((data['width'], data['height'], data['offset']), (320, 320, offset))
            self.assertEqual(data['total_pixels'], 102400)
            self.assertEqual(data['next_offset'], offset + CHUNK_PIXELS if offset < 96000 else None)
            self.assertLessEqual(len(data['pixels']), 25600)
            chunks.append(bytes.fromhex(data['pixels']))
            ids.add(data['image_id'])
            self.assertLessEqual(len(self.contract.artwork.cache), 4)
            self.assertLessEqual(sum(len(v[1][0]) for v in self.contract.artwork.cache.values() if v[1]), 102400)
        with Image.open(io.BytesIO(self.service.fixture_images[self.reference])) as source:
            rgb = source.convert('RGB').resize((320, 320), Image.Resampling.LANCZOS).tobytes()
        expected = b''.join((((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)).to_bytes(2, 'big')
                            for r, g, b in zip(rgb[::3], rgb[1::3], rgb[2::3]))
        self.assertEqual(b''.join(chunks), expected)
        self.assertEqual(ids, {hashlib.sha256(rgb).hexdigest()})
        legacy = self.request('artwork', reference=self.reference)['data']
        self.assertEqual(len(legacy['pixels']), 25600)
        self.assertNotIn('next_offset', legacy)
        self.assertEqual(self.service.artwork.images, {})
        self.assertEqual(self.service.naim.calls, [])

    def test_artwork_registration_expiry_corruption_and_changed_image(self):
        self.assertFalse(self.request('artwork', reference=self.reference, side=320)['data']['available'])
        self.request('snapshot')
        first = self.request('artwork', reference=self.reference, side=320)['data']
        self.service.fixture_images[self.reference] = fixture_jpeg(True)
        second = self.request('artwork', reference=self.reference, side=320, pixel_offset=6400)['data']
        self.assertNotEqual(first['image_id'], second['image_id'])
        self.now += TTL
        with patch.object(self.service, 'image', side_effect=AssertionError('must not fetch')):
            for reference in (self.reference, 'https://example.invalid', '/artwork/' + '0'*64 + '.jpg'):
                self.assertFalse(self.request('artwork', reference=reference, side=320)['data']['available'])
        self.request('snapshot')
        with patch.object(self.service, 'image', return_value=b'corrupt') as fetch:
            for _ in range(2):
                self.assertFalse(self.request('artwork', reference=self.reference, side=320)['data']['available'])
            self.assertEqual(fetch.call_count, 1)

    def test_artwork_argument_bounds_and_partial_last_chunk(self):
        self.request('snapshot')
        for args in ({'side': 0}, {'side': 321}, {'side': True}, {'side': 2.5},
                     {'side': '320'}, {'side': 320, 'pixel_offset': 102400},
                     {'pixel_offset': 6400}, {'pixel_offset': -1}, {'pixel_offset': True},
                     {'side': 320, 'pixel_offset': 1}):
            self.assertEqual(self.request('artwork', reference=self.reference, **args)['outcome'], 'rejected')
        last = self.request('artwork', reference=self.reference, side=81, pixel_offset=6400)['data']
        self.assertEqual(len(last['pixels']), 161 * 4)
        self.assertIsNone(last['next_offset'])

    def test_all_new_actions_share_single_flight_gate(self):
        with self.contract.lock:
            for action, args in [('battery_report', dict(level=10, charging=False, client_id='display')),
                                 ('charge?', {}), ('artwork', dict(reference=self.reference, side=320))]:
                self.assertEqual(self.request(action, **args)['error']['code'], 'BUSY')
        self.assertIsNone(self.contract.last_battery_report)

    def test_tls_authentication_revocation_and_no_static_route(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            create(root / 'tls')
            with closing(Vault(root / 'vault')) as vault:
                pairing = Pairing(vault)
                contract = Contract(self.service, vault)
                httpd = server(contract, pairing, root/'tls/trust.pem', root/'tls/key.pem', port=0)
                worker = threading.Thread(target=httpd.serve_forever, daemon=True)
                worker.start()
                try:
                    client = Client('https://127.0.0.1:' + str(httpd.server_port), root/'tls/trust.pem')
                    actions = [('battery_report', dict(level=20, charging=False, client_id='display')),
                               ('charge?', {}), ('artwork', dict(reference=self.reference, side=320))]
                    for action, args in actions:
                        with self.assertRaises(urllib.error.HTTPError) as denied:
                            client.request(action, args)
                        self.assertEqual(denied.exception.code, 401)
                    self.assertIsNone(contract.last_battery_report)
                    auth = client.pair(pairing.issue())
                    client.request('snapshot')
                    for action, args in actions:
                        self.assertEqual(client.request(action, args)['outcome'], 'observed')
                    self.assertEqual(client.request('charge?')['data'], {'charge': 'yes', 'reason': 'window'})
                    for path in ('/', '/charge?', '/artwork/' + '0'*64 + '.jpg'):
                        with self.assertRaises(urllib.error.HTTPError) as denied:
                            urllib.request.urlopen(client.url + path, context=ssl.create_default_context(cafile=str(root/'tls/trust.pem')))
                        self.assertEqual(denied.exception.code, 501)
                    pairing.revoke(auth['device'])
                    for action, args in actions:
                        with self.assertRaises(urllib.error.HTTPError) as denied:
                            client.request(action, args)
                        self.assertEqual(denied.exception.code, 401)
                finally:
                    httpd.shutdown(); httpd.server_close(); worker.join()
