import pathlib
import sys
import threading
import unittest
from unittest.mock import patch
sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / 'tools'))
from tidal_live_reads import DeferredRelated, ObservedReadOnlyLibrary
from tidal_library import TidalLibrary, LibraryError

class LiveReadsTests(unittest.TestCase):
    def test_slow_lookup_never_waits_or_accumulates_work(self):
        entered, release, done = threading.Event(), threading.Event(), threading.Event()
        class Source:
            calls = 0
            def related(self, reference):
                self.calls += 1
                entered.set()
                release.wait(2)
                return [{'reference': reference, 'kind': 'albums'}]
        source = Source()
        links = DeferredRelated(source)
        original = links._load
        def load(reference):
            try: original(reference)
            finally: done.set()
        links._load = load
        try:
            self.assertEqual(links.related('one'), [])
            self.assertTrue(entered.wait(1))
            for n in range(100): self.assertEqual(links.related(str(n)), [])
            self.assertEqual(source.calls, 1)
        finally: release.set()
        self.assertTrue(done.wait(1))
        self.assertEqual(links.related('one')[0]['reference'], 'one')
        result = links.related('one'); result[0]['reference'] = 'altered'
        self.assertEqual(links.related('one')[0]['reference'], 'one')

    def test_cache_bound_expiry_and_error_backoff(self):
        class Source:
            def related(self, ref):
                if ref == 'error': raise RuntimeError('unavailable')
                return [{'reference': ref}]
        now = [0]
        links = DeferredRelated(Source(), clock=lambda: now[0])
        for n in range(40): links._load(str(n))
        self.assertEqual(len(links.cache), 32)
        self.assertNotIn('0', links.cache)
        links._load('error')
        self.assertEqual(links.cache['error'], (10, []))
        now[0] = 60
        links.busy = True
        self.assertEqual(links.related('39'), [])

    def test_membership_does_not_scan_or_guess_absence(self):
        now = [100]
        lib = ObservedReadOnlyLibrary(object(), clock=lambda: now[0])
        lib.token, lib.expires = 'test', 1000
        ref = 'inputs/tidal/albums/1'
        with patch.object(TidalLibrary, 'page', return_value={'items':[{'reference':ref}], 'cursor':'more'}) as page:
            self.assertIsNone(lib.contains(ref, fresh=True))
            self.assertIsNone(lib.contains(ref))
            page.assert_not_called()
            lib.page('albums')
            self.assertTrue(lib.contains(ref))
            self.assertIsNone(lib.contains(ref, fresh=True))
            self.assertIsNone(lib.contains('inputs/tidal/albums/2'))
            now[0] = 160
            self.assertIsNone(lib.contains(ref))
            self.assertEqual(page.call_count, 1)
        with self.assertRaises(LibraryError): lib.save(ref, True)
        lib.disconnect()
        self.assertFalse(lib.observed)

    def test_native_string_count_survives_authenticated_browse(self):
        from controller_service import Bridge
        from m2_bridge import Contract
        class Naim:
            def browse(self, ref, offset):
                return {'id': ref, 'class': 'object.tidalAlbum', 'totalCount': '24', 'children': []}
        class Vault:
            data = {'commands': {}}
        contract = Contract(Bridge(Naim()), Vault())
        reply = contract.handle('test', {'version': 1, 'request_id': 'a'*32,
            'action': 'browse', 'args': {'reference':'inputs/tidal/albums/1'}})
        self.assertEqual(reply['outcome'], 'observed')
        self.assertEqual(reply['data']['total'], 24)
        self.assertEqual(reply['data']['next_offset'], 12)
