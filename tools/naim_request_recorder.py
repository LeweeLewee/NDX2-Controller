"""Temporary NDX-only HTTP recorder; use the generated PAC on an authorized phone.

Forwards the phone's requests once, including mutations. No TLS interception,
cloud proxying, response logging, or playback commands of its own.
"""
import argparse
import http.client
import http.server
import ipaddress
import json
import pathlib
import re
import secrets
import threading
import urllib.parse

CONTROL_FIELDS = {'cmd', 'command', 'action', 'direction', 'code', 'key',
                  'repeat', 'value', 'volume', 'mute', 'state', 'pressed'}
HOP_HEADERS = {'connection', 'proxy-connection', 'proxy-authorization',
               'keep-alive', 'te', 'trailer', 'transfer-encoding', 'upgrade'}


def control_summary(values):
    return {str(k): v if k in CONTROL_FIELDS and isinstance(v, (str, int, bool))
            and re.fullmatch(r'[A-Za-z0-9_.+,: /-]{0,80}', str(v)) else '[omitted]'
            for k, v in values.items()}


def handler_for(target, ports, listen, port, token, record):
    pac_path = '/' + token + '.pac'
    pac = ('function FindProxyForURL(url, host) { if (host === ' + json.dumps(target)
           + ' && url.substring(0,5) === "http:") return '
           + json.dumps('PROXY ' + listen + ':' + str(port) + '; DIRECT')
           + '; return "DIRECT"; }').encode()

    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_CONNECT(self):
            self.send_error(403, 'TLS is not intercepted or forwarded')

        def forward(self):
            if self.command == 'GET' and self.path == pac_path:
                self.send_response(200)
                self.send_header('Content-Type', 'application/x-ns-proxy-autoconfig')
                self.send_header('Content-Length', str(len(pac)))
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                self.wfile.write(pac)
                return
            connection = None
            try:
                url = urllib.parse.urlsplit(self.path if not self.path.startswith('/')
                       else 'http://' + self.headers.get('Host', '') + self.path)
                if (url.scheme != 'http' or url.hostname != target
                        or (url.port or 80) not in ports or url.username or url.password):
                    self.send_error(403, 'Only the configured NDX ports are forwarded')
                    return
                if self.headers.get('Transfer-Encoding'):
                    self.send_error(400, 'Chunked request bodies are unsupported')
                    return
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 <= length <= 1048576:
                    self.send_error(413)
                    return
                self.connection.settimeout(20)
                body = self.rfile.read(length) if length else None
                row = {'method': self.command, 'path': url.path, 'port': url.port or 80,
                       'query': control_summary(dict(urllib.parse.parse_qsl(url.query))),
                       'body_bytes': length}
                if body and 'application/json' in self.headers.get('Content-Type', ''):
                    try:
                        data = json.loads(body)
                        if isinstance(data, dict):
                            row['body_fields'] = control_summary(data)
                    except (ValueError, UnicodeError):
                        pass
                record(row)
                excluded = HOP_HEADERS | {'host', 'content-length'}
                excluded |= {v.strip().lower() for v in self.headers.get('Connection', '').split(',')}
                headers = {k: v for k, v in self.headers.items() if k.lower() not in excluded}
                connection = http.client.HTTPConnection(target, url.port or 80, timeout=20)
                connection.request(self.command, urllib.parse.urlunsplit(('', '', url.path, url.query, '')), body, headers)
                response = connection.getresponse()
                self.send_response(response.status)
                excluded = HOP_HEADERS | {v.strip().lower() for v in response.getheader('Connection', '').split(',')}
                for k, v in response.getheaders():
                    if k.lower() not in excluded:
                        self.send_header(k, v)
                self.send_header('Connection', 'close')
                self.end_headers()
                while self.command != 'HEAD':
                    chunk = response.read1(65536)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    self.wfile.flush()
                self.close_connection = True
            except (OSError, ValueError, http.client.HTTPException) as exc:
                record({'error_type': type(exc).__name__})
                self.close_connection = True
            finally:
                if connection:
                    connection.close()

        do_GET = do_POST = do_PUT = do_DELETE = do_PATCH = do_OPTIONS = do_HEAD = forward

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('listen', 'phone', 'ndx'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--ndx-ports', type=int, nargs='+', required=True)
    parser.add_argument('--port', type=int, default=8899)
    parser.add_argument('--minutes', type=int, default=15)
    parser.add_argument('--log', type=pathlib.Path, required=True)
    args = parser.parse_args()
    for address in (args.listen, args.phone, args.ndx):
        ip = ipaddress.IPv4Address(address)
        if not any(ip in ipaddress.IPv4Network(n) for n in ('10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16')):
            parser.error('Use private LAN IPv4 addresses')
    if not 1 <= args.minutes <= 30 or any(not 1 <= p <= 65535 for p in [args.port, *args.ndx_ports]):
        parser.error('Invalid port or duration')
    args.log.parent.mkdir(parents=True, exist_ok=True)
    lock = threading.Lock()

    def record(row):
        with lock, args.log.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(row) + '\n')

    class PhoneServer(http.server.ThreadingHTTPServer):
        daemon_threads = True

        def verify_request(self, request, address):
            return address[0] in (args.phone, args.listen)

    token = secrets.token_urlsafe(18)
    server = PhoneServer((args.listen, args.port), handler_for(args.ndx, args.ndx_ports,
                         args.listen, args.port, token, record))
    timer = threading.Timer(args.minutes * 60, server.shutdown)
    timer.daemon = True
    timer.start()
    print('PAC: http://' + args.listen + ':' + str(args.port) + '/' + token + '.pac', flush=True)
    print('NDX-only recorder; expires in ' + str(args.minutes) + ' minutes. PAC falls back to DIRECT.', flush=True)
    try:
        server.serve_forever()
    finally:
        timer.cancel()
        server.server_close()


if __name__ == '__main__':
    main()
