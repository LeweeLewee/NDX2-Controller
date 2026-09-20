import io
import json
import pathlib
import sys
import unittest
import urllib.error

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / 'tools'))
from music_discovery import MusicDiscovery, DiscoveryError
from prototype_ui import Bridge


class Opener:
    def __init__(self, data):
        self.data, self.requests = data, []

    def open(self, request, timeout):
        self.requests.append(request)
        if isinstance(self.data, Exception):
            raise self.data
        return io.BytesIO(json.dumps(self.data).encode())


class DiscoveryTests(unittest.TestCase):
    def test_refinement_is_metadata_only_and_drops_extra_model_fields(self):
        answer = {'summary': 'Brighter bass grooves', 'suggestions': [{'query': 'Four Tet', 'reason': 'Rhythmic textures', 'reference': 'fake'}]}
        opener = Opener({'status': 'completed', 'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': json.dumps(answer)}]}]})
        result = Bridge(ai=MusicDiscovery('test-secret', opener=opener)).request('discover', {'prompt': 'More upbeat', 'context': 'Like Bonobo'})
        payload = json.loads(opener.requests[0].data)
        self.assertFalse(payload['store'])
        self.assertEqual(json.loads(payload['input'])['previous_brief'], 'Like Bonobo')
        self.assertNotIn('reference', result['suggestions'][0])
        self.assertNotIn('tools', payload)
        self.assertEqual(opener.requests[0].full_url, 'https://api.openai.com/v1/responses')

    def test_input_limits_prevent_requests(self):
        opener = Opener({})
        ai = MusicDiscovery('test-secret', opener=opener)
        for prompt, context in [('', ''), ('x'*1001, ''), ('fine', 'x'*3001)]:
            with self.assertRaises(ValueError):
                ai.discover(prompt, context)
        for data, mime in [(b'x', 'text/html'), (b'', 'audio/webm'), (b'x'*(3*1024*1024+1), 'audio/webm')]:
            with self.assertRaises(ValueError):
                ai.transcribe(data, mime)
        self.assertEqual(opener.requests, [])

    def test_refusal_incomplete_and_malformed_output_are_not_results(self):
        for reply in [{'status': 'incomplete'}, {'status': 'completed', 'output': []},
                      {'status': 'completed', 'output': [{'type': 'message', 'content': [{'type': 'refusal', 'refusal': 'no'}]}]}]:
            with self.assertRaises(DiscoveryError):
                MusicDiscovery('test-secret', opener=Opener(reply)).discover('Music')

    def test_transcription_uses_fixed_endpoint_and_memory_upload(self):
        opener = Opener({'text': 'More upbeat please'})
        result = MusicDiscovery('test-secret', opener=opener).transcribe(b'synthetic-audio', 'audio/webm;codecs=opus')
        self.assertEqual(result['text'], 'More upbeat please')
        request = opener.requests[0]
        self.assertEqual(request.full_url, 'https://api.openai.com/v1/audio/transcriptions')
        self.assertIn(b'synthetic-audio', request.data)
        self.assertNotIn(b'test-secret', request.data)

    def test_errors_never_echo_credentials(self):
        error = urllib.error.HTTPError('https://api.openai.com/test-secret', 429, 'test-secret', {}, io.BytesIO(b'test-secret'))
        with self.assertRaises(DiscoveryError) as caught:
            MusicDiscovery('test-secret', opener=Opener(error)).discover('Music')
        self.assertNotIn('test-secret', str(caught.exception))
        self.assertIn('quota', str(caught.exception))
