import http.client
import http.server
import pathlib
import sys
import threading
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / 'tools'))
from naim_request_recorder import control_summary, handler_for


class RecorderTests(unittest.TestCase):
    def test_credentials_and_nested_data_are_not_recorded(self):
        self.assertEqual(control_summary({'cmd': 'volumeDown', 'token': 'secret',
                         'password': 'secret', 'value': {'private': 'data'}}),
                         {'cmd': 'volumeDown', 'token': '[omitted]',
                          'password': '[omitted]', 'value': '[omitted]'})

    def test_forwarding_and_pac_without_device(self):
        received, records = [], []

        class Upstream(http.server.BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def reply(self):
                received.append((self.command, self.path,
                                 self.rfile.read(int(self.headers.get('Content-Length', 0)))))
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"ok":true}')

            do_GET = do_PUT = reply

        upstream = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Upstream)
        proxy = http.server.ThreadingHTTPServer(('127.0.0.1', 0), http.server.BaseHTTPRequestHandler)
        proxy.RequestHandlerClass = handler_for('127.0.0.1', [upstream.server_port],
                                    '127.0.0.1', proxy.server_port, 'test', records.append)
        threads = [threading.Thread(target=s.serve_forever, daemon=True) for s in (upstream, proxy)]
        for thread in threads:
            thread.start()

        def request(method, path, body=None, headers=None):
            conn = http.client.HTTPConnection('127.0.0.1', proxy.server_port, timeout=3)
            conn.request(method, path, body, headers or {})
            response = conn.getresponse()
            result = response.status, response.read()
            conn.close()
            return result

        try:
            status, pac = request('GET', '/test.pac')
            self.assertEqual(status, 200)
            self.assertIn(b'; DIRECT', pac)
            self.assertIn(b'return "DIRECT"', pac)
            base = 'http://127.0.0.1:' + str(upstream.server_port)
            self.assertEqual(request('GET', base + '/description.xml')[0], 200)
            self.assertEqual(request('GET', base + '/inputs?offset=20')[0], 200)
            payload = b'{"cmd":"volumeDown","token":"private"}'
            self.assertEqual(request('PUT', base + '/automation?cmd=volumeDown', payload,
                                    {'Content-Type': 'application/json'})[0], 200)
            self.assertEqual(received[-1], ('PUT', '/automation?cmd=volumeDown', payload))
            self.assertEqual(len(received), 3)
            self.assertNotIn('private', str(records))
            self.assertEqual(records[-1]['body_fields']['cmd'], 'volumeDown')
            self.assertEqual(request('GET', 'http://example.com/')[0], 403)
            self.assertEqual(request('GET', 'http://127.0.0.1:1/')[0], 403)
            self.assertEqual(request('CONNECT', 'example.com:443')[0], 403)
            self.assertEqual(len(received), 3)
        finally:
            for server in (proxy, upstream):
                server.shutdown()
                server.server_close()
            for thread in threads:
                thread.join()
