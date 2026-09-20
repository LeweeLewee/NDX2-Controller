"""Loopback-only prototype UI. Demo by default; --ndx enables native control."""
import argparse
import getpass
import http.server
import json
import os
import pathlib
import urllib.parse
import hashlib
from collections import OrderedDict

from naim_client import NaimClient, native_ref, playback_state
from tidal_catalog import TidalCatalog, CatalogError, ordered_items
from music_discovery import MusicDiscovery, DiscoveryError, read_key
from artwork_cache import ArtworkCache, validate_artwork_url
from tidal_library import TidalLibrary, LibraryError

UI = pathlib.Path(__file__).parents[1] / 'ui' / 'index.html'


def native_item(data):
    reference = str(data.get('ussi', '')).strip('/')
    return {'reference': reference, 'title': str(data.get('title') or data.get('name') or 'Untitled'),
            'artist': str(data.get('artist') or data.get('artistName') or ''),
            'kind': reference.split('/')[2] if reference.startswith('inputs/tidal/') else 'tracks'}


class Bridge:
    def __init__(self, naim=None, catalog=None, ai=None):
        self.naim, self.catalog = naim, catalog
        self.ai = ai
        self.library = None
        self.resolved = set()
        self.artwork = ArtworkCache()
        self.artwork_refs = OrderedDict()

    def cover(self, value):
        try:
            url = validate_artwork_url(value)
        except ValueError:
            return None
        path = '/artwork/' + hashlib.sha256(url.encode()).hexdigest() + '.jpg'
        self.artwork_refs[path] = url
        self.artwork_refs.move_to_end(path)
        while len(self.artwork_refs) > 32:
            self.artwork_refs.popitem(last=False)
        return path

    def image(self, path):
        # Only URLs previously returned by the Naim metadata can be fetched.
        if path not in self.artwork_refs:
            raise ValueError('Unknown artwork')
        return self.artwork.get(self.artwork_refs[path])

    def request(self, action, args):
        if not isinstance(action, str):
            raise ValueError('Expected an action')
        if self.catalog and self.library is None:
            self.library = TidalLibrary(self.catalog)
        if action == 'config':
            return {'live': self.naim is not None, 'catalog': self.catalog is not None, 'ai': self.ai is not None,
                    'library': bool(self.library and self.library.connected)}
        if action.startswith('library_'):
            if not self.library:
                raise LibraryError('Configure this project’s TIDAL app before connecting your library.')
            if action == 'library_connect':
                return {'url': self.library.begin(self.oauth_redirect)}
            if action == 'library_disconnect':
                self.library.disconnect()
                return {'message': 'TIDAL library disconnected from this controller session.'}
            if action == 'library_page':
                return self.library.page(args.get('kind', 'albums'), args.get('cursor'))
            if action == 'library_state':
                return {'saved': self.library.contains(args.get('reference'), args.get('fresh', False))}
            if action == 'library_save':
                return self.library.save(args.get('reference'), args.get('saved'))
            raise ValueError('Unknown collection action')
        if action == 'discover':
            if not self.ai:
                raise DiscoveryError('AI search is not configured on this server.')
            return self.ai.discover(args.get('prompt'), args.get('context', ''))
        if action == 'search':
            if not self.catalog:
                raise ValueError('Catalogue credentials are not configured')
            kind = args.get('kind', 'tracks')
            result_id = args.get('result_id')
            if not result_id:
                data = self.catalog.search(args.get('query', ''), kind).get('data', [])
                if isinstance(data, dict):
                    data = [data]
                if not data:
                    return {'items': [], 'cursor': None}
                result_id = data[0]['id']
            page = self.catalog.page(result_id, kind, args.get('cursor'))
            link = page.get('links', {}).get('next')
            if isinstance(link, dict):
                link = link.get('href')
            cursor = urllib.parse.parse_qs(urllib.parse.urlsplit(link or '').query).get('page[cursor]', [None])[0]
            return {'items': [{'reference': i['candidate_native_reference'], 'title': i['title'] or i['id'],
                               'artist': '', 'kind': kind} for i in ordered_items(page, kind)],
                    'result_id': result_id, 'cursor': cursor}
        if not self.naim:
            raise ValueError('NDX is not configured; use the on-screen demo')
        if action == 'status':
            data = self.naim.status()
            fields = ('title', 'artist', 'artistName', 'duration', 'transportPosition', 'sourceDetail', 'bitDepth', 'sampleRate')
            return {**{key: data.get(key) for key in fields}, 'album': data.get('album') or data.get('albumName'),
                    'artwork': self.cover(data.get('artwork')), 'state': playback_state(data)}
        if action == 'queue':
            return {'items': [native_item(i) for i in self.naim.queue().get('children', [])]}
        if action == 'current_item':
            data = self.naim.queue()
            current = next((i for i in data.get('children', []) if i.get('ussi') == data.get('current')), {})
            if current.get('class') != 'object.track.tidal' or current.get('serverId') != 'tidal':
                raise LibraryError('The current item has no verified TIDAL track reference.')
            from tidal_catalog import candidate_reference
            reference = candidate_reference('tracks', str(current.get('track', '')))
            if not reference:
                raise LibraryError('The current track has no TIDAL identifier.')
            return {'reference': reference, 'kind': 'tracks', 'title': current.get('name', '')}
        if action == 'browse':
            reference = args.get('reference', 'inputs/tidal/favourites')
            self.resolved.discard(reference)
            data = self.naim.browse(reference, args.get('offset', 0))
            # Only a matching native object grants a play capability. Children do not.
            item = native_item(data)
            item['artwork'] = self.cover(data.get('artwork'))
            try:
                native_ref(reference)
                expected_class = {'tracks': 'object.tidalTrack', 'albums': 'object.tidalAlbum',
                                  'playlists': 'object.tidalPlaylist'}.get(reference.split('/')[2])
                playable = item['reference'] == reference and data.get('class') == expected_class
            except ValueError:
                playable = False
            if playable:
                self.resolved.add(reference)
            return {'item': item, 'playable': playable,
                    'items': [native_item(i) for i in data.get('children', [])], 'total': data.get('totalCount')}
        if action == 'play':
            reference = args.get('reference')
            if reference not in self.resolved:
                raise ValueError('Resolve this item through Naim before playing')
            # Read before every mutation; do not silently proceed if the player is unreachable.
            self.naim.status()
            self.naim.play(reference, args.get('placement', 'replace'))
            return {'message': 'Request sent. Check now playing or queue for the resulting state.'}
        if action == 'transport':
            command = args.get('command')
            if command not in ('pause', 'resume', 'stop', 'next', 'prev'):
                raise ValueError('Unsupported transport command')
            self.naim.status()
            self.naim.transport(command)
            return {'message': 'Request sent. Waiting for player state.'}
        if action == 'amplifier':
            if set(args) != {'direction'} or args.get('direction') not in ('down', 'up'):
                raise ValueError('Expected one amplifier direction: down or up')
            self.naim.amplifier_nudge(args['direction'])
            return {'message': 'Amplifier volume ' + args['direction'] + ' request sent.'}
        raise ValueError('Unknown action')


def handler_for(bridge, port):
    hosts = {'127.0.0.1:' + str(port), 'localhost:' + str(port)}
    bridge.oauth_redirect = 'http://127.0.0.1:' + str(port) + '/oauth/callback'

    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send(self, data, status=200, mime='application/json', cache='no-store'):
            raw = data if isinstance(data, bytes) else json.dumps(data).encode()
            self.send_response(status)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(raw)))
            self.send_header('Cache-Control', cache)
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):
            if self.headers.get('Host') not in hosts:
                self.send({'error': 'Invalid host'}, 403)
            elif self.path == '/':
                self.send(UI.read_bytes(), mime='text/html; charset=utf-8')
            elif self.path == '/api/config':
                self.send(bridge.request('config', {}))
            elif urllib.parse.urlsplit(self.path).path == '/oauth/callback':
                try:
                    if not bridge.library:
                        raise LibraryError('Start sign-in from Collection first.')
                    bridge.library.finish(urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query))
                    self.send_response(303)
                    self.send_header('Location', '/?library=connected')
                    self.send_header('Cache-Control', 'no-store')
                    self.send_header('Referrer-Policy', 'no-referrer')
                    self.end_headers()
                except Exception:
                    self.send(b'<h1>TIDAL sign-in was not completed</h1><p>Please return to Collection and connect again.</p><a href="/">Return to controller</a>',
                              400, 'text/html; charset=utf-8')
            elif self.path == '/?library=connected':
                self.send(UI.read_bytes(), mime='text/html; charset=utf-8')
            elif self.path in ('/discovery.js', '/discovery.css', '/library.js'):
                self.send((UI.parent / self.path[1:]).read_bytes(), mime='text/javascript' if self.path.endswith('.js') else 'text/css')
            elif self.path.startswith('/artwork/'):
                try:
                    self.send(bridge.image(self.path), mime='image/jpeg', cache='private, max-age=3600')
                except Exception:
                    self.send({'error': 'Artwork unavailable'}, 404)
            else:
                self.send({'error': 'Not found'}, 404)

        def do_POST(self):
            host = self.headers.get('Host')
            if host not in hosts or self.headers.get('Origin') != 'http://' + host:
                self.send({'error': 'Same-origin requests required'}, 403)
                return
            if self.path not in ('/api', '/api/transcribe'):
                self.send({'error': 'Invalid request'}, 400)
                return
            try:
                length = int(self.headers.get('Content-Length', 0))
                if self.path == '/api/transcribe':
                    if not bridge.ai:
                        raise DiscoveryError('Voice transcription is not configured on this server.')
                    if not 0 < length <= 3 * 1024 * 1024:
                        raise ValueError('Recording too large')
                    self.send(bridge.ai.transcribe(self.rfile.read(length), self.headers.get('Content-Type', '')))
                    return
                if self.headers.get('Content-Type') != 'application/json':
                    raise ValueError('JSON required')
                if not 0 < length <= 8192:
                    raise ValueError('Request too large or empty')
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict) or not isinstance(data.get('args', {}), dict):
                    raise ValueError('Expected an object')
                self.send(bridge.request(data.get('action'), data.get('args', {})))
            except (DiscoveryError, CatalogError) as exc:
                self.send({'error': str(exc)}, 502)
            except (ValueError, TypeError):
                self.send({'error': 'Request rejected. Check selection and configuration.'}, 400)
            except Exception:
                # Never serialize an upstream body, URL, credential or traceback.
                self.send({'error': 'Service unavailable. Refresh to check state; commands are not retried.'}, 502)
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ndx', help='Private NDX IPv4 address; enables live controls')
    parser.add_argument('--tidal', action='store_true', help='Enable live catalogue; credentials prompted without echo')
    parser.add_argument('--country', default='GB')
    parser.add_argument('--ai', action='store_true', help='Enable OpenAI discovery and transcription')
    parser.add_argument('--openai-env-file', help='Explicit approved local env file; only OPENAI_API_KEY is read')
    parser.add_argument('--ai-model', default='gpt-4.1-mini')
    parser.add_argument('--port', type=int, default=8990)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error('Use a port from 1024 to 65535')
    naim = NaimClient(args.ndx) if args.ndx else None
    catalog = None
    if args.tidal:
        catalog = TidalCatalog(os.environ.get('TIDAL_CLIENT_ID') or getpass.getpass('TIDAL client ID: '),
                               os.environ.get('TIDAL_CLIENT_SECRET') or getpass.getpass('TIDAL client secret: '), args.country)
    ai = MusicDiscovery(read_key(args.openai_env_file), args.ai_model) if args.ai else None
    bridge = Bridge(naim, catalog, ai)
    server = http.server.HTTPServer(('127.0.0.1', args.port), handler_for(bridge, args.port))
    print('Open http://127.0.0.1:' + str(args.port), flush=True)
    print('Live NDX controls enabled.' if naim else 'Demo playback only; no NDX commands.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
