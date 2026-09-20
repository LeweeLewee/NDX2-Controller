import pathlib
import sys
import unittest
import http.client
import http.server
import threading

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / 'tools'))
from prototype_ui import Bridge, handler_for


class Naim:
    def __init__(self):
        self.calls = []
        self.description = {'ussi': 'inputs/tidal/tracks/123', 'class': 'object.tidalTrack', 'title': 'Example'}

    def browse(self, *args):
        return self.description

    def status(self):
        self.calls.append('status')
        return {'transportState': 1}

    def play(self, reference, placement):
        self.calls.append(('play', reference, placement))


class BridgeTests(unittest.TestCase):
    def test_artwork_is_registered_from_metadata_not_arbitrary_requests(self):
        bridge = Bridge()
        url = 'https://resources.tidal.com/images/album/640x640.jpg'
        path = bridge.cover(url)
        self.assertTrue(path.startswith('/artwork/'))
        self.assertEqual(path, bridge.cover(url))
        self.assertIsNone(bridge.cover('http://192.168.1.1/private.jpg'))
        self.assertIsNone(bridge.cover(None))
        with self.assertRaises(ValueError):
            bridge.image('/artwork/unknown.jpg')
        self.assertNotEqual(path, bridge.cover(url.replace('album', 'next-album')))

    def test_status_exposes_local_cover_and_album_name(self):
        naim = Naim()
        naim.status = lambda: {'transportState': '2', 'albumName': 'The album',
                              'artwork': 'https://resources.tidal.com/images/album/640x640.jpg'}
        data = Bridge(naim).request('status', {})
        self.assertEqual(data['album'], 'The album')
        self.assertTrue(data['artwork'].startswith('/artwork/'))
        self.assertEqual(data['state'], 'playing')

    def test_candidate_cannot_play_until_native_identity_matches(self):
        naim = Naim()
        bridge = Bridge(naim)
        ref = 'inputs/tidal/tracks/123'
        with self.assertRaises(ValueError):
            bridge.request('play', {'reference': ref})
        naim.description['ussi'] = 'inputs/tidal/tracks/999'
        self.assertFalse(bridge.request('browse', {'reference': ref})['playable'])
        with self.assertRaises(ValueError):
            bridge.request('play', {'reference': ref})
        naim.description['ussi'] = ref
        self.assertTrue(bridge.request('browse', {'reference': ref})['playable'])
        bridge.request('play', {'reference': ref})
        self.assertEqual(naim.calls, ['status', ('play', ref, 'replace')])

    def test_failed_reresolution_revokes_play_capability(self):
        naim = Naim()
        bridge = Bridge(naim)
        ref = naim.description['ussi']
        bridge.request('browse', {'reference': ref})
        naim.description['class'] = 'object.track.upnp'
        bridge.request('browse', {'reference': ref})
        with self.assertRaises(ValueError):
            bridge.request('play', {'reference': ref})
        self.assertEqual(naim.calls, [])

    def test_browse_class_must_match_reference_kind(self):
        naim = Naim()
        for kind, classname in [('tracks', 'object.tidalTrack'), ('albums', 'object.tidalAlbum'), ('playlists', 'object.tidalPlaylist')]:
            ref = 'inputs/tidal/' + kind + '/123'
            naim.description = {'ussi': ref, 'class': classname}
            self.assertTrue(Bridge(naim).request('browse', {'reference': ref})['playable'])
            naim.description['class'] = 'object.track.tidal'
            self.assertFalse(Bridge(naim).request('browse', {'reference': ref})['playable'])

    def test_demo_backend_cannot_mutate_player(self):
        bridge = Bridge()
        self.assertEqual(bridge.request('config', {}), {'live': False, 'catalog': False, 'ai': False})
        with self.assertRaises(ValueError):
            bridge.request('transport', {'command': 'resume'})

    def test_volume_is_not_exposed(self):
        naim = Naim()
        with self.assertRaises(ValueError):
            Bridge(naim).request('transport', {'command': 'volume'})
        self.assertEqual(naim.calls, [])

    def test_http_rejects_cross_origin_and_unexpected_host(self):
        server = http.server.HTTPServer(('127.0.0.1', 0), http.server.BaseHTTPRequestHandler)
        port = server.server_port
        server.RequestHandlerClass = handler_for(Bridge(), port)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for headers in ({'Origin': 'https://other.example'}, {'Host': 'other.example', 'Origin': 'http://other.example'}):
                connection = http.client.HTTPConnection('127.0.0.1', port, timeout=2)
                connection.request('POST', '/api', '{"action":"config"}', {'Content-Type': 'application/json', **headers})
                response = connection.getresponse()
                self.assertEqual(response.status, 403)
                response.read()
                connection.close()
            connection = http.client.HTTPConnection('127.0.0.1', port, timeout=2)
            connection.request('POST', '/api', '{"action":"config"}', {'Content-Type': 'application/json', 'Origin': 'http://127.0.0.1:' + str(port)})
            response = connection.getresponse()
            self.assertEqual(response.status, 200)
            self.assertNotIn(b'secret', response.read())
            connection.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
