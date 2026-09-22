"""Desktop-only TLS transport for the native SDL client; framed JSON on pipes.

No credentials cross the pipe. ESP32 uses esp_http_client instead. Configuration
contains public origin/trust/state paths, never inline credentials. Fixture-only
unless a trusted local operator explicitly configures allow_live=true.
"""
import json
from pathlib import Path
import sys
from m2_client import Client
from m2_security import Vault


def main():
    config=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    vault=Vault(config['state'])
    client=Client(config['url'],config['trust'],vault.data['controller']['credential'])
    try:
        for line in iter(lambda:sys.stdin.buffer.readline(8194),b''):
            try:
                if len(line)>8193 or not line.endswith(b'\n'): break
                request=json.loads(line)
                if request.get('action') in ('play','amplifier','transport','library_save') and not config.get('allow_live',False):
                    if not client.request('snapshot').get('fixture'):
                        raise PermissionError('Live bridge not enabled')
                response=client.post('/v1/request',request)
                if not response.get('fixture') and not config.get('allow_live',False):
                    raise PermissionError('Live bridge not enabled')
            except Exception:
                response={"transport_error":"UNAVAILABLE"}
            sys.stdout.write(json.dumps(response,separators=(',',':'))+'\n'); sys.stdout.flush()
    finally: vault.close()


if __name__=='__main__': main()
