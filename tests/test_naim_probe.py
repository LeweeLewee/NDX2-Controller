import importlib.util
import io
import json
import pathlib
import unittest

spec = importlib.util.spec_from_file_location("probe", pathlib.Path(__file__).parents[1] / "tools" / "naim_native_probe.py")
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class Response(io.BytesIO):
    status = 200


class FakeOpener:
    def __init__(self, payload):
        self.payload = payload
        self.requests = []

    def open(self, request, timeout):
        self.requests.append(request)
        return Response(self.payload)


class ProbeTests(unittest.TestCase):
    def test_no_commands_or_arbitrary_fetches(self):
        opener = FakeOpener(b'{}')
        for path in ('/nowplaying?cmd=play', '/inputs/tidal?cmd=select', '/levels/room?volume=100', '//example.com', '/login'):
            with self.assertRaises(ValueError):
                probe.read_endpoint(opener, 'http://192.168.1.2:15081', path, 1)
        self.assertFalse(opener.requests)

    def test_read_and_default_deny_redaction(self):
        payload = {'model': 'NDX 2', 'accessToken': 'SECRET', 'unknown': 'SECRET', 'source': 'inputs/tidal', 'url': 'SECRET', 'children': [{'ussi': 'inputs/tidal?token=SECRET', 'password': 'SECRET'}]}
        opener = FakeOpener(json.dumps(payload).encode())
        entry, raw = probe.read_endpoint(opener, 'http://192.168.1.2:15081', '/system', 1)
        self.assertEqual(opener.requests[0].get_method(), 'GET')
        self.assertNotIn('SECRET', json.dumps(entry))
        self.assertEqual(entry['structure']['model'], 'NDX 2')
        self.assertEqual(raw, payload)

    def test_only_advertised_native_inputs(self):
        payload = {'children': [{'ussi': 'inputs/tidal'}, {'ussi': '/inputs/playqueue'}, {'ussi': 'inputs/tidal?cmd=play'}, {'ussi': 'http://example.com'}]}
        self.assertEqual(probe.advertised_inputs(payload), ['inputs/playqueue', 'inputs/tidal'])

    def test_reject_nonprivate_targets(self):
        for address in ('8.8.8.8', '127.0.0.1', '169.254.169.254', 'example.com'):
            with self.assertRaises(ValueError):
                probe.collect(address)

    def test_non_json_and_oversized_bodies_not_retained(self):
        for data in (b'<html>SECRET</html>', b'SECRET' + b'x' * probe.MAX_BYTES):
            entry, raw = probe.read_endpoint(FakeOpener(data), 'http://192.168.1.2:15081', '/', 1)
            self.assertIsNone(raw)
            self.assertNotIn('SECRET', json.dumps(entry))

    def test_redirects_not_followed(self):
        self.assertIsNone(probe.NoRedirect().redirect_request(None, None, 302, '', {}, 'http://example.com'))


if __name__ == '__main__':
    unittest.main()
