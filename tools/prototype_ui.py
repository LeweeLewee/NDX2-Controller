"""Loopback-only prototype UI. Demo by default; --ndx enables native control."""
import argparse
import getpass
import http.server
import json
import os
import pathlib
import urllib.parse
from naim_client import NaimClient
from tidal_catalog import TidalCatalog, CatalogError
from music_discovery import MusicDiscovery, DiscoveryError, read_key
from tidal_library import LibraryError
from controller_service import Bridge, native_item

UI = pathlib.Path(__file__).parents[1] / 'ui' / 'index.html'


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
