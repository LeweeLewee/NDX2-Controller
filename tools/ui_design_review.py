"""Serve only the local, silent design-review board and an existing fixture capture."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]

class ReviewHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        routes = {
            '/': (ROOT / 'docs/ui-review/index.html', 'text/html; charset=utf-8'),
            '/fixture.bmp': (ROOT / 'local/m2/native-captures/01-now.bmp', 'image/bmp'),
        }
        item = routes.get(self.path)
        if not item or not item[0].is_file():
            self.send_error(404)
            return
        data = item[0].read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', item[1])
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'self' data:; connect-src 'none'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *_):
        pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8766)
    args = parser.parse_args()
    print(f'Silent UI design review: http://127.0.0.1:{args.port}', flush=True)
    HTTPServer(('127.0.0.1', args.port), ReviewHandler).serve_forever()
