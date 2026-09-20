"""Loopback-only prototype UI. Demo by default; --ndx enables native control."""
import argparse
import getpass
import http.server
import json
import os
import pathlib
import urllib.parse

from naim_client import NaimClient, native_ref, playback_state
from tidal_catalog import TidalCatalog, ordered_items

UI = pathlib.Path(__file__).parents[1] / 'ui' / 'index.html'


def native_item(data):
    reference = str(data.get('ussi', '')).strip('/')
    return {'reference': reference, 'title': str(data.get('title') or data.get('name') or 'Untitled'),
            'artist': str(data.get('artist') or data.get('artistName') or ''),
            'kind': reference.split('/')[2] if reference.startswith('inputs/tidal/') else 'tracks'}


class Bridge:
    def __init__(self, naim=None, catalog=None):
        self.naim, self.catalog = naim, catalog
        self.resolved = set()

    def request(self, action, args):
        if action == 'config':
            return {'live': self.naim is not None, 'catalog': self.catalog is not None}
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
            fields = ('title', 'artist', 'artistName', 'album', 'duration', 'transportPosition', 'sourceDetail', 'bitDepth', 'sampleRate')
            return {**{key: data.get(key) for key in fields}, 'state': playback_state(data)}
        if action == 'queue':
            return {'items': [native_item(i) for i in self.naim.queue().get('children', [])]}
        if action == 'browse':
            reference = args.get('reference', 'inputs/tidal/favourites')
            self.resolved.discard(reference)
            data = self.naim.browse(reference, args.get('offset', 0))
            # Only a matching native object grants a play capability. Children do not.
            item = native_item(data)
            try:
                native_ref(reference)
                playable = item['reference'] == reference and str(data.get('class', '')).endswith('.tidal')
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
        raise ValueError('Unknown action')


def handler_for(bridge, port):
    hosts = {'127.0.0.1:' + str(port), 'localhost:' + str(port)}

    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send(self, data, status=200, mime='application/json'):
            raw = data if isinstance(data, bytes) else json.dumps(data).encode()
            self.send_response(status)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(raw)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):
            if self.headers.get('Host') not in hosts:
                self.send({'error': 'Invalid host'}, 403)
            elif self.path == '/':
                self.send(UI.read_bytes(), mime='text/html; charset=utf-8')
            elif self.path == '/api/config':
                self.send(bridge.request('config', {}))
            else:
                self.send({'error': 'Not found'}, 404)

        def do_POST(self):
            host = self.headers.get('Host')
            if host not in hosts or self.headers.get('Origin') != 'http://' + host:
                self.send({'error': 'Same-origin requests required'}, 403)
                return
            if self.path != '/api' or self.headers.get('Content-Type') != 'application/json':
                self.send({'error': 'Invalid request'}, 400)
                return
            try:
                length = int(self.headers.get('Content-Length', 0))
                if not 0 < length <= 8192:
                    raise ValueError('Request too large or empty')
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict) or not isinstance(data.get('args', {}), dict):
                    raise ValueError('Expected an object')
                self.send(bridge.request(data.get('action'), data.get('args', {})))
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
    parser.add_argument('--port', type=int, default=8990)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error('Use a port from 1024 to 65535')
    naim = NaimClient(args.ndx) if args.ndx else None
    catalog = None
    if args.tidal:
        catalog = TidalCatalog(os.environ.get('TIDAL_CLIENT_ID') or getpass.getpass('TIDAL client ID: '),
                               os.environ.get('TIDAL_CLIENT_SECRET') or getpass.getpass('TIDAL client secret: '), args.country)
    bridge = Bridge(naim, catalog)
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
