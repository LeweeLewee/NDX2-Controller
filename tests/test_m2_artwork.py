import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parents[1] / 'tools'))
from m2_artwork import ArtworkDelivery, normalize, fixture_jpeg, SIDE, TTL
from m2_bridge import Contract, FixtureService, MAX_RESPONSE


class ArtworkTests(unittest.TestCase):
    def setUp(self):
        self.service = FixtureService()
        self.now = [100.0]
        self.delivery = ArtworkDelivery(self.service, lambda: self.now[0])
        self.reference = next(iter(self.service.fixture_images))

    def test_live_queue_artwork_is_registered_without_browsing_queue_ids(self):
        class Vault:
            data = {'commands': {}}
        contract = Contract(self.service, Vault(), lambda: self.now[0])
        def request(action, args=None):
            return contract.handle('fixture', {'version': 1, 'request_id': 'a'*32,
                                              'action': action, 'args': args or {}})
        children = [{'ussi': f'inputs/playqueue/{n}', 'name': f'Track {n}',
                     'artwork': f'https://resources.tidal.com/images/fixture/queue{n}.jpg'}
                    for n in range(50)]
        with patch.object(self.service.naim, 'queue', return_value={'children': children}), \
             patch.object(self.service.naim, 'browse', side_effect=AssertionError('No queue browse')):
            first = request('snapshot')['data']['queue']
            second = request('queue', {'offset': 12})['data']['items']
        self.assertEqual(len(first), 12)
        self.assertEqual(second[0]['reference'], 'inputs/playqueue/12')
        for item in first + second:
            ref = item['artwork']
            self.assertIn(ref, contract.artwork.registered)
            self.assertIn(ref, self.service.artwork_refs)
            self.service.fixture_images[ref] = fixture_jpeg()
            self.assertTrue(request('artwork', {'reference': ref, 'side': 320})['data']['available'])
        self.assertLessEqual(len(contract.artwork.cache), 4)
        self.assertLessEqual(len(self.service.artwork_refs), 32)
        self.assertEqual(self.service.naim.calls, [])

    def test_registration_and_url_injection(self):
        for value in (self.reference, 'https://resources.tidal.com/images/other.jpg',
                      'http://127.0.0.1/secret', '/artwork/' + '0' * 64 + '.jpg'):
            self.assertFalse(self.delivery.get(value)['available'])
        self.delivery.register(self.reference)
        self.assertTrue(self.delivery.get(self.reference)['available'])
        self.assertEqual(self.service.naim.calls, [])

    def test_bounds_and_corrupt_input(self):
        from PIL import Image
        for dimensions, kind in (((1025, 1), 'JPEG'), ((10, 10), 'PNG')):
            output = io.BytesIO(); Image.new('RGB', dimensions).save(output, format=kind)
            with self.assertRaises(ValueError): normalize(output.getvalue())
        for raw in (b'bad', fixture_jpeg()[:40], b'x' * (1024 * 1024 + 1)):
            with self.assertRaises((ValueError, OSError)): normalize(raw)
        self.assertEqual(len(normalize(fixture_jpeg())), SIDE * SIDE * 4)

    def test_cache_expiry_and_negative_cache(self):
        self.delivery.register(self.reference)
        with patch.object(self.service, 'image', wraps=self.service.image) as fetch:
            first = self.delivery.get(self.reference)
            self.assertEqual(self.delivery.get(self.reference), first)
            self.assertEqual(fetch.call_count, 1)
            self.now[0] += TTL + 1
            self.assertFalse(self.delivery.get(self.reference)['available'])
            self.delivery.register(self.reference)
            self.delivery.get(self.reference)
            self.assertEqual(fetch.call_count, 2)
        self.delivery.cache.clear()
        with patch.object(self.service, 'image', side_effect=ValueError('PRIVATE')) as fetch:
            self.assertEqual(self.delivery.get(self.reference), {'available': False})
            self.delivery.get(self.reference)
            self.assertEqual(fetch.call_count, 1)

    def test_eviction_and_removed_registration(self):
        for n in range(40):
            reference = self.service.cover(f'https://resources.tidal.com/images/fixture/{n}.jpg')
            self.service.fixture_images[reference] = fixture_jpeg()
            self.delivery.register(reference); self.delivery.get(reference)
        self.assertLessEqual(len(self.delivery.cache), 4)
        self.assertLessEqual(len(self.delivery.registered), 32)
        self.service.artwork_refs.clear()
        self.assertFalse(self.delivery.get(reference)['available'])

    def test_contract_registration_envelope_and_changed_cover(self):
        class Vault:
            data = {'commands': {}}
        contract = Contract(self.service, Vault(), lambda: self.now[0])
        def request(action, args=None):
            return contract.handle('fixture', {'version': 1, 'request_id': 'a'*32,
                                              'action': action, 'args': args or {}})
        self.assertEqual(request('artwork')['outcome'], 'rejected')
        first = request('snapshot')['data']['player']['artwork']
        artwork = request('artwork', {'reference': first})
        self.assertLess(len(json.dumps(artwork).encode()), MAX_RESPONSE)
        self.assertTrue(artwork['data']['available'])
        self.service.naim.art_variant = 1
        second = request('snapshot')['data']['player']['artwork']
        self.assertNotEqual(first, second)
        self.assertNotEqual(artwork['data']['pixels'], request('artwork', {'reference': second})['data']['pixels'])
        self.assertFalse(request('artwork', {'reference': 'https://example.invalid'})['data']['available'])
        self.assertEqual(self.service.naim.calls, [])
