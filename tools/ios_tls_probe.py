"""Synthetic loopback-only TLS peer for native URLSession tests; no NDX access.

Ephemeral keys stay in ignored local/. Public fixture metadata is bundled into
the test target by CI. No actual enrollment or credentials are used.
"""
import base64
import json
import os
from pathlib import Path
import ssl
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def prepare(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    os.chmod(directory, 0o700)

    def openssl(*args):
        subprocess.run(['openssl', *args], cwd=directory, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    root_config = '''[req]
distinguished_name = dn
x509_extensions = ca
prompt = no
[dn]
CN = Synthetic Still Water TLS CA
[ca]
basicConstraints = critical,CA:true,pathlen:0
keyUsage = critical,keyCertSign,cRLSign
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always
'''
    (directory / 'root.cnf').write_text(root_config)
    for name in ('root', 'unrelated'):
        openssl('req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-sha256',
                '-days', '2', '-config', 'root.cnf', '-keyout', name + '.key', '-out', name + '.pem')
        os.chmod(directory / (name + '.key'), 0o600)
    for name, san in [('valid', 'IP:127.0.0.1'), ('wrong-host', 'DNS:wrong.invalid')]:
        (directory / (name + '.cnf')).write_text('''[leaf]
basicConstraints = critical,CA:false
keyUsage = critical,digitalSignature,keyEncipherment
extendedKeyUsage = serverAuth
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always
subjectAltName = ''' + san + '\n')
        openssl('req', '-new', '-newkey', 'rsa:2048', '-nodes', '-sha256',
                '-subj', '/CN=Synthetic Still Water TLS peer',
                '-keyout', name + '.key', '-out', name + '.csr')
        os.chmod(directory / (name + '.key'), 0o600)
        openssl('x509', '-req', '-in', name + '.csr', '-CA', 'root.pem',
                '-CAkey', 'root.key', '-CAcreateserial', '-days', '1', '-sha256',
                '-extfile', name + '.cnf', '-extensions', 'leaf', '-out', name + '.pem')
        (directory / (name + '-chain.pem')).write_bytes(
            (directory / (name + '.pem')).read_bytes() + (directory / 'root.pem').read_bytes())
    return directory


class Peer(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        length = int(self.headers.get('Content-Length', '0'))
        if self.path != '/v1/pair' or not 0 < length <= 8192:
            self.send_error(400)
            return
        self.rfile.read(length)
        body = b'{"synthetic_tls_probe":true}'
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def serve(directory, metadata):
    peers = []
    values = {'available': True}
    for name in ('root', 'unrelated'):
        der = ssl.PEM_cert_to_DER_cert((directory / (name + '.pem')).read_text())
        values[name] = base64.b64encode(der).decode('ascii')
    for name in ('valid', 'wrong-host'):
        peer = ThreadingHTTPServer(('127.0.0.1', 0), Peer)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.load_cert_chain(directory / (name + '-chain.pem'), directory / (name + '.key'))
        peer.socket = context.wrap_socket(peer.socket, server_side=True)
        threading.Thread(target=peer.serve_forever, daemon=True).start()
        peers.append(peer)
        values[name] = 'https://127.0.0.1:' + str(peer.server_port)
    metadata.write_text(json.dumps(values), encoding='utf-8')
    print('Synthetic TLS peers ready on loopback only', flush=True)
    threading.Event().wait(1200)
    for peer in peers:
        peer.shutdown()
        peer.server_close()


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    serve(prepare(root / 'local/ios-ci/tls-probe'),
          root / 'ios/StillWaterTests/TLSProbe.json')
