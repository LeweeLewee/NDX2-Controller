import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / 'tools'))
from artist_metadata import plain_biography
from controller_service import Bridge
from tidal_catalog import TidalCatalog, CatalogError
from m2_bridge import Contract, ContractError, FixtureService
from m2_ios_fixtures import MemoryVault


class ArtistMetadataTests(unittest.TestCase):
    def test_plain_text_entities_hidden_markup_unicode_and_bound(self):
        self.assertEqual(plain_biography('<p>Piano &amp; strings</p><script>hidden</script><p>Quiet.</p>'), 'Piano & strings Quiet.')
        self.assertEqual(len(plain_biography('🎵' * 2001)), 2000)
        self.assertIsNone(plain_biography('<style>hidden</style>'))
        self.assertIsNone(plain_biography(None))

    def test_only_exact_catalogue_relationships_and_allowlisted_portrait(self):
        catalog = TidalCatalog('client', 'secret')
        page = {'data': {'type': 'artists', 'id': '1', 'relationships': {
            'biography': {'data': {'type': 'artistBiographies', 'id': 'b'}},
            'profileArt': {'data': [{'type': 'artworks', 'id': 'p'}]}}},
            'included': [{'type': 'artistBiographies', 'id': 'other', 'attributes': {'text': 'Wrong'}},
                         {'type': 'artistBiographies', 'id': 'b', 'attributes': {'text': '<p>Right</p>'}},
                         {'type': 'artworks', 'id': 'p', 'attributes': {'files': [
                             {'href': 'http://127.0.0.1/private.jpg'},
                             {'href': 'https://resources.tidal.com/images/artist/a.jpg'}]}}]}
        calls = []
        def get(path, params):
            calls.append((path, params))
            return page
        catalog._get = get
        bridge = Bridge(catalog=catalog)
        result = bridge.request('artist_bio', {'reference': 'inputs/tidal/artists/1'})
        self.assertTrue(result['available'])
        self.assertEqual(result['biography'], 'Right')
        self.assertIn(result['artwork'], bridge.artwork_refs)
        self.assertFalse(bridge.resolved)
        self.assertEqual(calls[0], ('artists/1', {'countryCode': 'GB', 'include': 'biography,profileArt'}))
        page['data']['id'] = '2'
        with self.assertRaises(CatalogError): catalog.artist_metadata('inputs/tidal/artists/1')
        for reference in ('inputs/tidal/tracks/1', 'https://example.com', 'inputs/tidal/artists/../1'):
            with self.assertRaises(ValueError): catalog.artist_metadata(reference)

    def test_missing_metadata_is_unavailable_without_placeholder(self):
        catalog = TidalCatalog('client', 'secret')
        catalog._get = lambda *args: {'data': {'type': 'artists', 'id': '1'}}
        for bridge in (Bridge(catalog=catalog), Bridge()):
            result = bridge.request('artist_bio', {'reference': 'inputs/tidal/artists/1'})
            self.assertEqual(result, {'reference': 'inputs/tidal/artists/1', 'available': False, 'biography': None, 'artwork': None})

    def test_fixture_read_registers_chunked_portrait_without_mutation(self):
        service = FixtureService()
        contract = Contract(service, MemoryVault(), clock=lambda: 100)
        def read(action, args):
            return contract.handle('fixture', {'version': 1, 'request_id': 'artist_test_0001', 'action': action, 'args': args})
        bio = read('artist_bio', {'reference': 'inputs/tidal/artists/1'})
        self.assertEqual(bio['outcome'], 'observed')
        self.assertTrue(bio['data']['available'])
        for offset in (0, 96000):
            portrait = read('artwork', {'reference': bio['data']['artwork'], 'side': 320, 'pixel_offset': offset})
            self.assertEqual(portrait['outcome'], 'observed')
        self.assertFalse(service.naim.calls)
        self.assertFalse(contract.vault.data['commands'])
        for args in ({}, {'reference': 'inputs/tidal/artists/1', 'url': 'https://example.com'}):
            self.assertEqual(read('artist_bio', args)['outcome'], 'rejected')
