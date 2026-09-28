import base64
import hashlib
import json
import pathlib
import sys
import unittest
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / 'tools'))
from tidal_library import TidalLibrary, LibraryError, SCOPES
from tidal_catalog import CatalogError, ordered_items


class Catalog:
    _client_id = 'project-client'

    def __init__(self):
        self.calls = []
        self.saved = {'1', '2'}

    def _json(self, request):
        self.calls.append(request)
        if '/oauth2/token' in request.full_url:
            return {'access_token': 'private-token', 'refresh_token': 'private-refresh',
                    'expires_in': 3600, 'scope': SCOPES}
        if request.method != 'GET':
            item = json.loads(request.data)['data'][0]
            if request.method == 'POST':
                self.saved.add(item['id'])
            else:
                self.saved.discard(item['id'])
            return {}
        ids = sorted(self.saved)
        if 'page%5Bcursor%5D' not in request.full_url:
            return {'data': [{'type': 'albums', 'id': i} for i in ids[:1]],
                    'links': {'next': '?page[cursor]=second'} if len(ids) > 1 else {}}
        return {'data': [{'type': 'albums', 'id': i} for i in ids[1:]]}


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.catalog = Catalog()
        self.library = TidalLibrary(self.catalog, clock=lambda: 100, sleep=lambda seconds: None)

    def connect(self):
        url = self.library.begin('http://127.0.0.1:8990/oauth/callback')
        params = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
        self.library.finish({'state': params['state'], 'code': ['code']})
        return params

    def test_read_only_consent_accepts_read_scope_and_blocks_writes(self):
        from unittest.mock import patch
        self.library = TidalLibrary(self.catalog,clock=lambda:100,sleep=lambda _:None,read_only=True)
        with patch.object(self.catalog,'_json',return_value={'access_token':'read-token','expires_in':3600,'scope':'collection.read'}):
            params = self.connect()
        self.assertEqual(params['scope'],['collection.read'])
        self.assertTrue(self.library.connected)
        self.assertTrue(self.library.page('albums')['items'])
        count = len(self.catalog.calls)
        with self.assertRaises(LibraryError): self.library.save('inputs/tidal/albums/1',True)
        with self.assertRaises(LibraryError): self.library._request('albums','POST',item_id='1')
        self.assertEqual(len(self.catalog.calls),count)

    def test_pkce_state_and_single_use_callback(self):
        url = self.library.begin('http://127.0.0.1:8990/oauth/callback')
        params = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
        verifier = self.library.pending[1]
        expected = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=')
        self.assertEqual(params['code_challenge'], [expected])
        self.assertEqual(params['scope'], [SCOPES])
        with self.assertRaises(LibraryError):
            self.library.finish({'state': ['wrong'], 'code': ['code']})
        self.assertFalse(self.catalog.calls)
        self.library.finish({'state': params['state'], 'code': ['code']})
        self.assertTrue(self.library.connected)
        form = urllib.parse.parse_qs(self.catalog.calls[0].data.decode())
        self.assertEqual(form['code_verifier'], [verifier])
        with self.assertRaises(LibraryError):
            self.library.finish({'state': params['state'], 'code': ['code']})

    def test_cancelled_expired_and_missing_scopes_fail(self):
        for params in ({'error': ['access_denied']}, {'code': []}):
            self.library.begin('http://127.0.0.1:8990/oauth/callback')
            with self.assertRaises(LibraryError):
                self.library.finish({'state': [self.library.pending[0]], **params})
        self.library.begin('http://127.0.0.1:8990/oauth/callback')
        self.library.clock = lambda: 99999
        with self.assertRaises(LibraryError):
            self.library.finish({'state': [self.library.pending[0]], 'code': ['code']})
        self.library.clock = lambda: 100
        self.catalog._json = lambda request: {'access_token': 'token', 'expires_in': 3600, 'scope': 'collection.read'}
        with self.assertRaises(LibraryError):
            self.connect()
        self.assertFalse(self.library.connected)

    def test_pagination_save_remove_and_no_duplicate_mutation(self):
        self.connect()
        self.assertTrue(self.library.contains('inputs/tidal/albums/2'))
        self.assertTrue(self.library.save('inputs/tidal/albums/3', True)['saved'])
        writes = [r for r in self.catalog.calls if r.method == 'POST' and '/v2/' in r.full_url]
        self.assertEqual(len(writes), 1)
        self.assertEqual(json.loads(writes[0].data), {'data': [{'type': 'albums', 'id': '3'}]})
        self.library.save('inputs/tidal/albums/3', True)
        self.assertEqual(len([r for r in self.catalog.calls if r.method == 'POST' and '/v2/' in r.full_url]), 1)
        self.assertFalse(self.library.save('inputs/tidal/albums/3', False)['saved'])
        self.assertEqual(self.catalog.saved, {'1', '2'})

    def test_partial_collection_is_never_reported_as_unsaved(self):
        self.connect()
        self.library.page = lambda *args: {'items': [], 'cursor': 'repeated'}
        with self.assertRaises(LibraryError):
            self.library.save('inputs/tidal/albums/3', True)
        self.assertEqual(self.catalog.saved, {'1', '2'})

    def test_invalid_targets_disconnect_and_expiry(self):
        for ref in ('http://example.com', 'inputs/tidal/albums/../1', 'inputs/tidal/favourites', None):
            with self.assertRaises(ValueError):
                self.library.save(ref, True)
        self.connect()
        with self.assertRaises(ValueError):
            self.library.save('inputs/tidal/albums/3', 'true')
        self.library.expires = 0
        self.assertTrue(self.library.contains('inputs/tidal/albums/1'))
        self.assertIn(b'grant_type=refresh_token', self.catalog.calls[1].data)
        self.library.disconnect()
        self.assertFalse(self.library.connected)
        with self.assertRaises(LibraryError):
            self.library.contains('inputs/tidal/albums/1')

    def test_rate_limit_retries_read_once_but_never_write(self):
        self.connect()
        sleeps, calls = [], []
        self.library.sleep = sleeps.append
        def limited(request):
            calls.append(request.method)
            if len(calls) == 1:
                raise CatalogError('Rate limited', 429, 2)
            return {'data': []}
        self.catalog._json = limited
        self.library.page('albums')
        self.assertEqual(calls, ['GET', 'GET'])
        self.assertIn(2, sleeps)
        calls.clear()
        with self.assertRaises(CatalogError):
            self.library._request('albums', 'POST', item_id='3')
        self.assertEqual(calls, ['POST'])

    def test_null_optional_metadata_and_empty_pages(self):
        self.assertEqual(ordered_items({'data': None, 'included': None}, 'albums'), [])
        self.assertEqual(ordered_items({'data': [{'type': 'albums', 'id': '1'}],
            'included': [{'type': 'albums', 'id': '1', 'attributes': None}]}, 'albums')[0]['id'], '1')


if __name__ == '__main__':
    unittest.main()
