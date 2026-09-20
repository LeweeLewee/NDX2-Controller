import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / 'tools'))
from tidal_catalog import TidalCatalog, CatalogError
from prototype_ui import Bridge


class RelatedTests(unittest.TestCase):
    def test_exact_relationships_preserve_multiple_artists_and_ignore_unrelated_metadata(self):
        catalog = TidalCatalog('client', 'secret')
        calls = []
        def get(path, params):
            calls.append((path, params))
            return {'data': {'id': '12', 'type': 'tracks', 'relationships': {
                'albums': {'data': [{'id': '34', 'type': 'albums'}]},
                'artists': {'data': [{'id': '56', 'type': 'artists'}, {'id': '78', 'type': 'artists'}]}}},
                'included': [{'id': '99', 'type': 'albums', 'attributes': {'title': 'Wrong album'}},
                             {'id': '34', 'type': 'albums', 'attributes': {'title': 'Exact album'}},
                             {'id': '78', 'type': 'artists', 'attributes': {'name': 'Second artist'}},
                             {'id': '56', 'type': 'artists', 'attributes': {'name': 'First artist'}}]}
        catalog._get = get
        bridge = Bridge(catalog=catalog)
        items = bridge.request('related', {'reference': 'inputs/tidal/tracks/12'})['items']
        self.assertEqual([i['title'] for i in items], ['Exact album', 'First artist', 'Second artist'])
        self.assertEqual(items[0]['reference'], 'inputs/tidal/albums/34')
        self.assertEqual(calls, [('tracks/12', {'countryCode': 'GB', 'include': 'albums,artists'})])
        self.assertFalse(bridge.resolved)  # Metadata never grants native playback capability.

    def test_invalid_or_mismatched_identity_cannot_produce_links(self):
        catalog = TidalCatalog('client', 'secret')
        catalog._get = lambda *args: {'data': {'type': 'tracks', 'id': '99'}}
        with self.assertRaises(CatalogError):
            catalog.related('inputs/tidal/tracks/12')
        for ref in (None, 'inputs/tidal/artists/12', 'inputs/tidal/tracks/../12', 'https://example.com'):
            with self.assertRaises(ValueError):
                catalog.related(ref)

    def test_missing_relationship_is_empty_not_a_search_guess(self):
        catalog = TidalCatalog('client', 'secret')
        catalog._get = lambda *args: {'data': {'type': 'albums', 'id': '12'}}
        self.assertEqual(catalog.related('inputs/tidal/albums/12'), [])
