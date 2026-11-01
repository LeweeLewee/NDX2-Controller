"""Home Assistant host entry point; existing HTTPS contract and native adapters.

No Supervisor token, new HTTP route, automatic playback or public setup endpoint.
Operator files live in the app's private persistent configuration directory.
"""
import argparse
import json
import os
from pathlib import Path
import re
import secrets
import signal
import threading
import time

from controller_service import Bridge
from m2_bridge import Contract, ContractError, server
from m2_security import Pairing, Vault
from naim_client import NaimClient
from tidal_catalog import TidalCatalog
from tidal_live_reads import DeferredRelated, ObservedReadOnlyLibrary


def allowed(action, args, controls):
    if action in {'snapshot', 'queue', 'browse', 'artwork', 'library_state',
                  'library_page', 'search', 'artist_bio', 'battery_report', 'charge?'}:
        return True
    if not controls or not isinstance(args, dict):
        return False
    if action == 'transport':
        return args.get('command') in {'pause', 'resume', 'next', 'prev'}
    if action == 'amplifier':
        return set(args) == {'direction'} and args['direction'] in {'up', 'down'}
    if action == 'play':
        return bool(re.fullmatch(r'(?:inputs/tidal/(?:albums|tracks)/[0-9]{1,32}|inputs/playqueue/[0-9]{1,32})',
                                 str(args.get('reference', ''))))
    return False


class TrialContract(Contract):
    def __init__(self, service, vault, controls=False):
        super().__init__(service, vault)
        self.controls = controls
        self.counts = {}
        self.last_request = None

    def _execute(self, device, rid, action, args):
        if not allowed(action, args, self.controls):
            raise ContractError('READ_ONLY_TRIAL')
        return super()._execute(device, rid, action, args)

    def handle(self, device, request):
        reply = super().handle(device, request)
        outcome = reply.get('outcome', 'invalid')
        self.counts[outcome] = self.counts.get(outcome, 0) + 1
        self.last_request = int(time.time())
        return reply


class TrialPairing(Pairing):
    def issue(self):
        with self.lock:
            code = f'{secrets.randbelow(100_000_000):08d}'
            self.pending = (code, self.clock() + 600, 0)
            return code


class ConnectedBridge(Bridge):
    def __init__(self, naim, vault):
        self.vault = vault
        account = vault.data['tidal']
        catalog = TidalCatalog(account['client_id'], account['client_secret'])
        super().__init__(naim, catalog)
        self.library = ObservedReadOnlyLibrary(catalog)
        self.library.token = account.get('token')
        self.library.refresh_token = account.get('refresh_token')
        self.library.expires = self.library.clock() + max(0, account.get('expires_at', 0) - time.time())
        self.links = DeferredRelated(TidalCatalog(account['client_id'], account['client_secret']))

    def request(self, action, args):
        if action == 'related':
            return {'items': self.links.related(args.get('reference'))}
        try:
            return super().request(action, args)
        finally:
            account = self.vault.data['tidal']
            if (account.get('token'), account.get('refresh_token')) != (self.library.token, self.library.refresh_token):
                update = dict(account, token=self.library.token, refresh_token=self.library.refresh_token,
                              expires_at=time.time() + max(0, self.library.expires - self.library.clock()))
                self.vault.update(lambda data: data.update(tidal=update))


def atomic_json(path, value):
    temporary = path.with_suffix('.tmp')
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as stream:
        json.dump(value, stream)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--state', type=Path, default=Path('/config/private'))
    args = parser.parse_args()
    os.umask(0o077)
    state = args.state
    config = json.loads((state / 'host.json').read_text(encoding='utf-8'))
    vault = Vault(state / 'vault')
    service = ConnectedBridge(NaimClient(config['ndx_address']), vault)
    contract = TrialContract(service, vault, config.get('controls_enabled') is True)
    pairing = TrialPairing(vault)
    httpd = server(contract, pairing, str(state / 'server-chain.pem'),
                   str(state / 'server-key.pem'), '0.0.0.0', 8991)
    stopped = threading.Event()
    started = int(time.time())
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    signal.signal(signal.SIGTERM, lambda *_: stopped.set())
    signal.signal(signal.SIGINT, lambda *_: stopped.set())
    print('Authenticated bridge ready; no automatic player commands.', flush=True)
    try:
        while not stopped.wait(5):
            # Local operator request only, consumed once. Codes never appear in logs.
            request = state / 'issue-pairing'
            if request.exists():
                request.unlink()
                atomic_json(state / 'pairing.json', {'code': pairing.issue(), 'expires_at': int(time.time()) + 600})
            code_file = state / 'pairing.json'
            if code_file.exists() and (pairing.pending is None or pairing.clock() >= pairing.pending[1]):
                code_file.unlink()
            atomic_json(state / 'status.json', {'started_at': started, 'checked_at': int(time.time()),
                        'uptime_seconds': int(time.time()) - started, 'counts': dict(contract.counts),
                        'last_authenticated_request': contract.last_request,
                        'enrolled_devices': len(pairing.devices()), 'controls_enabled': contract.controls})
    finally:
        pairing.cancel()
        (state / 'pairing.json').unlink(missing_ok=True)
        httpd.shutdown()
        httpd.server_close()
        vault.close()


if __name__ == '__main__':
    main()
