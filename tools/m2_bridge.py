"""Version 1 bounded controller contract. Default adapter is SILENT FIXTURE."""
import argparse
import hashlib
import http.server
import json
import re
import ssl
import threading
import time
import uuid

from controller_service import Bridge
from m2_artwork import ArtworkDelivery, fixture_jpeg
from m2_security import Pairing, Vault

MAX_REQUEST = 8192
MAX_RESPONSE = 32768
PAGE_SIZE = 12
MUTATIONS = {'play', 'amplifier', 'transport', 'library_save'}
FIELDS = {'snapshot': set(), 'search': {'query', 'kind', 'cursor', 'result_id', 'offset'},
          'browse': {'reference', 'offset'}, 'queue': {'offset'},
          'library_state': {'reference'}, 'library_save': {'reference', 'saved'},
          'play': {'reference'}, 'amplifier': {'direction'}, 'transport': {'command'},
          'voice_review': {'fixture'}, 'suggest': {'prompt'},
          'library_page': {'kind', 'cursor', 'offset'}, 'artwork': {'reference'}}


def configured_service(vault):
    """Explicit opt-in wiring for a provisioned host; never invoked by fixtures."""
    from naim_client import NaimClient
    from tidal_catalog import TidalCatalog
    from m2_library import PersistentLibrary
    config = vault.data.get('provider_config', {})
    naim = NaimClient(config['ndx_address'])
    catalog = TidalCatalog(config['client_id'], config['client_secret'], config.get('country', 'GB'))
    service = Bridge(naim, catalog)
    service.library = PersistentLibrary(catalog, vault)
    return service


class FixtureNaim:
    """No sockets, audio, physical microphone or inferred amplifier level."""
    def __init__(self):
        self.title = 'Silent fixture - ready'
        self.calls = []
    def status(self):
        return {'title': self.title, 'artist': 'Fixture Ensemble', 'album': 'Silent album',
                'transportState': '2', 'sourceDetail': 'tidal', 'duration': 330000, 'transportPosition': 76000}
    def queue(self):
        return {'children': [{'ussi': 'inputs/tidal/tracks/101', 'title': self.title}]}
    def browse(self, reference, offset=0):
        kind = reference.split('/')[2]
        title = ('Fixture Ensemble' if kind == 'artists' else 'Silent track' if kind == 'tracks' else
                 'An exceptionally long album title for seated reading and layout trials')
        child = 'inputs/tidal/albums/1' if kind == 'artists' else 'inputs/tidal/tracks/101'
        return {'ussi': reference, 'class': {'albums':'object.tidalAlbum', 'tracks':'object.tidalTrack',
                'artists':'object.tidalArtist', 'playlists':'object.tidalPlaylist'}.get(kind),
                'artist': 'Fixture Ensemble', 'title': title,
                'children': [{'ussi': child, 'title': 'Silent album' if kind == 'artists' else 'Silent track'}], 'totalCount': 1}
    def play(self, reference, placement):
        self.calls.append(('play', reference, placement)); self.title = 'Silent track'
    def amplifier_nudge(self, direction):
        self.calls.append(('amplifier', direction))
    def transport(self, command):
        self.calls.append(('transport', command))


class FixtureService(Bridge):
    fixture = True
    def __init__(self):
        super().__init__(FixtureNaim())
        self.fixture_images = {self.cover('https://resources.tidal.com/images/fixture/a.jpg'): fixture_jpeg(),
                               self.cover('https://resources.tidal.com/images/fixture/b.jpg'): fixture_jpeg(True)}
        self.saved = {'inputs/tidal/artists/1': False, 'inputs/tidal/tracks/101': False}
    def image(self, path):
        return self.fixture_images[path]
    def request(self, action, args):
        if action == 'status':
            data = super().request(action, args)
            data['artwork'] = list(self.fixture_images)[self.naim.title == 'Silent track']
            return data
        if action == 'browse':
            data = super().request(action, args)
            data['item']['artwork'] = list(self.fixture_images)[0]
            return data
        if action in ('search', 'library_page'):
            kind = args.get('kind', 'albums')
            items = [{'reference': 'inputs/tidal/' + kind + '/' + str(i), 'title':
                      'An exceptionally long album title for seated reading' if i == 1 else 'Silent ' + kind[:-1] + ' ' + str(i),
                      'artist': 'Fixture Ensemble', 'kind': kind, 'artwork': None,
                      'saved': {1: 'saved', 2: 'unsaved'}.get(i, 'unknown')} for i in range(1, 30)]
            if action == 'library_page':
                items = [i for i in items if self.saved.get(i['reference'], i['saved'] == 'saved')]
            return {'items': items, 'cursor': None, 'result_id': 'fixture'}
        if action == 'current_item':
            return {'reference':'inputs/tidal/tracks/101', 'title':self.naim.title, 'kind':'tracks'}
        if action == 'related':
            return {'items':[{'reference':'inputs/tidal/albums/1','title':'Silent album','kind':'albums'},
                             {'reference':'inputs/tidal/artists/1','title':'Fixture Ensemble','kind':'artists'}]}
        if action == 'library_state': return {'saved': self.saved.get(args['reference'])}
        if action == 'library_save':
            self.saved[args['reference']] = args['saved']
            return {'saved': args['saved']}
        return super().request(action, args)


class ContractError(Exception):
    def __init__(self, code): self.code = code


class Contract:
    def __init__(self, service, vault, clock=time.monotonic):
        self.service, self.vault, self.clock = service, vault, clock
        self.boot = uuid.uuid4().hex
        self.lock = threading.Lock()
        self.fresh = {}
        self.revision = 0
        self.artwork = ArtworkDelivery(service, clock)

    def detail_links(self, item):
        # Only exact provider relationships; absence never becomes a search guess.
        item = dict(item)
        if item.get('kind') not in ('albums', 'tracks'): return item
        try: related = self.service.request('related', {'reference': item['reference']})['items']
        except Exception: return item
        for kind, field in (('artists', 'artist'), ('albums', 'album')):
            link = next((i for i in related if i.get('kind') == kind), None)
            if link and not (kind == 'albums' and item.get('kind') == 'albums'):
                item[field] = link['title']; item[field + '_reference'] = link['reference']
        return item

    def envelope(self, request_id, state, data=None, error=None):
        response = {'version': 1, 'request_id': request_id, 'boot_id': self.boot,
                    'outcome': state, 'fixture': bool(getattr(self.service, 'fixture', False)),
                    'data': data, 'error': {'code': error} if error else None}
        if len(json.dumps(response).encode()) > MAX_RESPONSE: raise ContractError('RESPONSE_TOO_LARGE')
        return response

    def validate(self, request):
        if not isinstance(request, dict) or set(request) != {'version', 'request_id', 'action', 'args'}:
            raise ContractError('INVALID_REQUEST')
        rid, action, args = request['request_id'], request['action'], request['args']
        if type(request['version']) is not int or request['version'] != 1: raise ContractError('VERSION_UNSUPPORTED')
        if not isinstance(rid, str) or not re.fullmatch(r'[a-zA-Z0-9_-]{16,64}', rid): raise ContractError('INVALID_REQUEST_ID')
        if not isinstance(action, str) or action not in FIELDS or not isinstance(args, dict) or set(args) - FIELDS[action]:
            raise ContractError('INVALID_ACTION')
        for key, value in args.items():
            if key == 'saved':
                if type(value) is not bool: raise ContractError('INVALID_ARGUMENT')
            elif key == 'offset':
                if type(value) is not int or not 0 <= value <= 10000: raise ContractError('INVALID_ARGUMENT')
            elif not isinstance(value, str) or len(value.encode()) > (4096 if key == 'cursor' else 256):
                raise ContractError('INVALID_ARGUMENT')
        required = {'play': {'reference'}, 'browse': {'reference'}, 'artwork': {'reference'}, 'library_state': {'reference'},
                    'library_save': {'reference', 'saved'}, 'amplifier': {'direction'}, 'transport': {'command'}}
        if not required.get(action, set()).issubset(args): raise ContractError('INVALID_ARGUMENT')
        if action == 'amplifier' and args['direction'] not in ('up', 'down'): raise ContractError('INVALID_ARGUMENT')
        if action == 'transport' and args['command'] not in ('pause', 'resume', 'stop', 'next', 'prev'): raise ContractError('INVALID_ARGUMENT')
        if action in ('search', 'library_page') and args.get('kind', 'albums') not in ('albums','tracks','artists','playlists'):
            raise ContractError('INVALID_ARGUMENT')
        return rid, action, args

    def handle(self, device, request):
        rid = request.get('request_id') if isinstance(request, dict) else None
        if not isinstance(rid, str) or not re.fullmatch(r'[a-zA-Z0-9_-]{16,64}', rid): rid = None
        try:
            rid, action, args = self.validate(request)
            if not self.lock.acquire(blocking=False): raise ContractError('BUSY')
            try: return self._execute(device, rid, action, args)
            finally: self.lock.release()
        except ContractError as exc: return self.envelope(rid, 'rejected', error=exc.code)
        except Exception: return self.envelope(rid, 'rejected', error='SERVICE_UNAVAILABLE')

    def _execute(self, device, rid, action, args):
        mutation = action in MUTATIONS
        key = device + ':' + rid
        fingerprint = hashlib.sha256(json.dumps([action, args], sort_keys=True).encode()).hexdigest()
        if mutation:
            previous = self.vault.data['commands'].get(key)
            if previous:
                if previous['fingerprint'] != fingerprint: raise ContractError('REQUEST_ID_CONFLICT')
                return self.envelope(rid, previous['outcome'], error='OUTCOME_UNKNOWN' if previous['outcome'] == 'unknown' else None)
            if self.clock() - self.fresh.get(device, float('-inf')) > 5: raise ContractError('STATE_STALE')
            # Fail closed when full; never evict an ID and accidentally re-execute it.
            if len(self.vault.data['commands']) >= 10000: raise ContractError('JOURNAL_FULL')
            self.vault.update(lambda d: d['commands'].update({key: {'fingerprint': fingerprint, 'outcome': 'unknown'}}))
        try:
            if action == 'artwork':
                data = self.artwork.get(args['reference'])
            elif action == 'snapshot':
                sampled_at = self.clock()
                player = self.service.request('status', {})
                self.artwork.register(player.get('artwork'))
                queue = self.service.request('queue', {})
                try: current = self.detail_links(self.service.request('current_item', {}))
                except Exception: current = None
                age_ms = max(0, int((self.clock() - sampled_at) * 1000))
                self.revision += 1
                data = {'player': player, 'current_item': current, 'queue': queue.get('items', [])[:PAGE_SIZE],
                        'queue_total': len(queue.get('items', [])), 'revision': self.revision,
                        'age_ms': age_ms, 'valid_for_ms': max(0, 5000 - age_ms), 'account':
                        'fixture' if getattr(self.service, 'fixture', False) else
                        ('connected' if self.service.library and self.service.library.connected else 'disconnected')}
                self.fresh[device] = sampled_at
            elif action in ('voice_review', 'suggest'):
                if not getattr(self.service, 'fixture', False): raise ContractError('NOT_CONFIGURED')
                data = {'transcript': 'Find quiet instrumental albums', 'queries': ['quiet instrumental'], 'fixture': True}
            else:
                offset = args.get('offset', 0)
                passed = {k: v for k, v in args.items() if k != 'offset'}
                if action == 'browse': passed['offset'] = offset
                if action == 'play':
                    # Resolve on EVERY play request, never trust cached catalogue IDs.
                    detail = self.service.request('browse', {'reference': args['reference']})
                    if not detail['playable']: raise ContractError('NATIVE_UNRESOLVED')
                if action == 'library_state': passed['fresh'] = True
                data = self.service.request(action, passed)
                if action == 'browse':
                    data = {**data, 'item': self.detail_links(data['item'])}
                    self.artwork.register(data['item'].get('artwork'))
                if 'items' in data:
                    items = data['items']
                    start = 0 if action == 'browse' else offset
                    data = {**data, 'items': items[start:start + PAGE_SIZE],
                            'next_offset': offset + PAGE_SIZE if len(items) > start + PAGE_SIZE else None}
                    if action == 'browse' and data.get('total', 0) and offset + PAGE_SIZE < data['total']:
                        data['next_offset'] = offset + PAGE_SIZE
                if action in ('library_state', 'library_save'):
                    data['saved_state'] = {True: 'saved', False: 'unsaved', None: 'unknown'}[data.get('saved')]
            outcome = 'submitted' if mutation else 'observed'
            response = self.envelope(rid, outcome, data)
            if mutation:
                self.vault.update(lambda d: d['commands'][key].update(outcome=outcome))
                self.fresh.pop(device, None)
            return response
        except Exception as exc:
            self.fresh.pop(device, None)
            if mutation: return self.envelope(rid, 'unknown', error='OUTCOME_UNKNOWN')
            if action == 'library_state': return self.envelope(rid, 'observed', {'saved_state': 'unknown'})
            raise ContractError(exc.code if isinstance(exc, ContractError) else 'SERVICE_UNAVAILABLE') from None


def handler_for(contract, pairing):
    class Handler(http.server.BaseHTTPRequestHandler):
        def setup(self):
            super().setup(); self.connection.settimeout(5)
        def log_message(self, *args): pass
        def do_POST(self):
            status = 200
            try:
                if self.headers.get('Origin') or self.headers.get('Transfer-Encoding'):
                    raise PermissionError()
                if self.headers.get('Content-Type') != 'application/json': raise ValueError()
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= MAX_REQUEST: raise ValueError()
                if self.path == '/v1/pair':
                    data = json.loads(self.rfile.read(length))
                    result = pairing.pair(data.get('code'))
                elif self.path == '/v1/request':
                    auth = self.headers.get('Authorization', '')
                    if not auth.startswith('Bearer ') or len(auth) > 128: raise PermissionError()
                    device = pairing.authenticate(auth[7:])
                    result = contract.handle(device, json.loads(self.rfile.read(length)))
                else: raise ValueError()
            except PermissionError:
                status, result = 401, {'error': {'code': 'AUTHENTICATION_REQUIRED'}}
            except Exception:
                status, result = 400, {'error': {'code': 'INVALID_REQUEST'}}
            raw = json.dumps(result).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(raw)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Connection', 'close')
            self.end_headers(); self.wfile.write(raw)
    return Handler


def server(contract, pairing, cert, key, host='127.0.0.1', port=8991):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(cert, key)
    # Bounded single-worker service: concurrent commands cannot overlap bursts.
    class TLSServer(http.server.HTTPServer):
        request_queue_size = 8
        def get_request(self):
            connection, address = self.socket.accept()
            connection.settimeout(5)
            try: return context.wrap_socket(connection, server_side=True), address
            except Exception:
                connection.close()
                raise
    httpd = TLSServer((host, port), handler_for(contract, pairing))
    return httpd


def main():
    parser = argparse.ArgumentParser(description='Authenticated SILENT FIXTURE bridge; no live commands')
    parser.add_argument('--state', default='local/m2/bridge')
    parser.add_argument('--cert', required=True); parser.add_argument('--key', required=True)
    parser.add_argument('--host', default='127.0.0.1'); parser.add_argument('--port', type=int, default=8991)
    parser.add_argument('--live', action='store_true', help='Use explicitly provisioned protected configuration; can control real playback')
    args = parser.parse_args()
    vault = Vault(args.state); pairing = Pairing(vault)
    service = configured_service(vault) if args.live else FixtureService()
    httpd = server(Contract(service, vault), pairing, args.cert, args.key, args.host, args.port)
    def console():
        while True:
            try: command = input('Local admin: pair | cancel | devices | revoke DEVICE | quit\n').split()
            except EOFError: return
            try:
                if command == ['pair']: print('Single-use setup code (120 s):', pairing.issue())
                elif command == ['cancel']: pairing.cancel(); print('Setup code cancelled.')
                elif command == ['devices']: print('Controller IDs:', ', '.join(pairing.devices()) or 'none')
                elif len(command) == 2 and command[0] == 'revoke':
                    pairing.revoke(command[1]); print('Controller authorization removed.')
                elif command == ['quit']: httpd.shutdown(); return
            except Exception:
                print('Administration failed; inspect protected storage before retrying.')
    threading.Thread(target=console, daemon=True).start()
    print('LIVE native bridge ready.' if args.live else 'SILENT FIXTURE HTTPS bridge ready; provider credentials are not needed.')
    try: httpd.serve_forever()
    finally: httpd.server_close(); vault.close()


if __name__ == '__main__': main()
