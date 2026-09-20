import io
import json
import pathlib
import sys
import unittest
import urllib.error
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / 'tools'))
from tidal_catalog import TidalCatalog, CatalogError, candidate_reference, ordered_items


class Opener:
    def __init__(self, replies):
        self.replies, self.requests = list(replies), []
    def open(self, request, timeout):
        self.requests.append(request)
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return io.BytesIO(json.dumps(reply).encode())


TOKEN = {'access_token': 'test-token', 'expires_in': 100}


class CatalogTests(unittest.TestCase):
    def test_result_order_comes_from_relationship_not_metadata(self):
        page = {'data': [{'type': 'artists', 'id': '2'}, {'type': 'artists', 'id': '1'},
                         {'type': 'artists', 'id': '3'}],
                'included': [{'type': 'artists', 'id': '1', 'attributes': {'name': 'Second'}},
                             {'type': 'artists', 'id': '2', 'attributes': {'name': 'First'}},
                             {'type': 'albums', 'id': '2', 'attributes': {'title': 'Unrelated'}}]}
        items = ordered_items(page, 'artists')
        self.assertEqual([item['id'] for item in items], ['2', '1', '3'])
        self.assertEqual([item['title'] for item in items], ['First', 'Second', None])

    def test_search_is_metadata_only_and_caches_token(self):
        opener = Opener([TOKEN, {'data': []}, {'data': []}])
        catalog = TidalCatalog('id', 'secret', opener=opener)
        catalog.search('Massive Attack & Friends')
        catalog.search('Another', 'albums')
        self.assertEqual(len(opener.requests), 3)
        self.assertEqual(opener.requests[0].get_method(), 'POST')
        for request in opener.requests[1:]:
            self.assertEqual(request.get_method(), 'GET')
            self.assertEqual(urllib.parse.urlsplit(request.full_url).netloc, 'openapi.tidal.com')
            self.assertNotIn('secret', request.full_url)
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(opener.requests[1].full_url).query)
        self.assertEqual(query['filter[query]'], ['Massive Attack & Friends'])
        self.assertEqual(query['countryCode'], ['GB'])

    def test_token_refresh_after_expiry(self):
        now = [0]
        opener = Opener([TOKEN, {}, TOKEN, {}])
        catalog = TidalCatalog('id', 'secret', opener=opener, clock=lambda: now[0])
        catalog.search('First')
        now[0] = 91
        catalog.search('Second')
        self.assertEqual([r.get_method() for r in opener.requests], ['POST','GET','POST','GET'])

    def test_opaque_id_and_cursor_cannot_change_host(self):
        opener = Opener([TOKEN, {}])
        catalog = TidalCatalog('id', 'secret', opener=opener)
        catalog.page('https://elsewhere/x?y', 'tracks', 'a&injected=1')
        url = urllib.parse.urlsplit(opener.requests[-1].full_url)
        self.assertEqual(url.netloc, 'openapi.tidal.com')
        self.assertIn('https%3A%2F%2Felsewhere', url.path)
        self.assertEqual(urllib.parse.parse_qs(url.query)['page[cursor]'], ['a&injected=1'])

    def test_invalid_input_makes_no_network_requests(self):
        opener = Opener([])
        catalog = TidalCatalog('id', 'secret', opener=opener)
        for query, kind in (('', 'tracks'), ('x'*257, 'tracks'), ('test', 'audio')):
            with self.assertRaises(ValueError):catalog.search(query, kind)
        with self.assertRaises(ValueError):catalog.page('..', 'tracks')
        self.assertEqual(opener.requests, [])

    def test_native_refs_are_candidates_with_restricted_ids(self):
        self.assertEqual(candidate_reference('tracks', '123'), 'inputs/tidal/tracks/123')
        for kind, item_id in (('tracks', '1?cmd=play'), ('audio', '123'), ('albums', 'https://example.com'), ('tracks', None)):
            self.assertIsNone(candidate_reference(kind, item_id))

    def test_error_does_not_expose_credentials_or_response(self):
        error = urllib.error.HTTPError('https://example.com/secret', 401, 'secret', {}, io.BytesIO(b'secret'))
        catalog = TidalCatalog('id', 'secret', opener=Opener([error]))
        with self.assertRaises(CatalogError) as caught:catalog.search('test')
        self.assertNotIn('secret', str(caught.exception))
        self.assertIn('401', str(caught.exception))

    def test_invalid_token_is_rejected(self):
        for token in ({'access_token': 'x', 'expires_in': 'NaN'}, {'access_token': 'x\r\nsecret', 'expires_in': 100}, {'access_token': 'x'}):
            with self.assertRaises(CatalogError):
                TidalCatalog('id','secret',opener=Opener([token])).search('test')
