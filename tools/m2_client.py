"""Desktop contract client and UI model; never retries a mutation."""
import copy
import json
import ssl
import random
import time
import urllib.request
import urllib.error
import uuid
from naim_native_probe import NoRedirect
from m2_limits import MAX_RESPONSE


class Client:
    def __init__(self, url, trust, credential=None):
        from urllib.parse import urlsplit
        parsed = urlsplit(url)
        if parsed.scheme != 'https' or parsed.username or parsed.password or parsed.path not in ('', '/'):
            raise ValueError('HTTPS bridge origin required')
        self.url, self.credential = url.rstrip('/'), credential
        context = ssl.create_default_context(cafile=str(trust))
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        self.opener = urllib.request.build_opener(NoRedirect(), urllib.request.HTTPSHandler(context=context),
                                                  urllib.request.ProxyHandler({}))

    def post(self, path, body):
        headers = {'Content-Type': 'application/json'}
        if self.credential: headers['Authorization'] = 'Bearer ' + self.credential
        request = urllib.request.Request(self.url + path, json.dumps(body).encode(), headers)
        try:
            with self.opener.open(request, timeout=5) as response:
                raw = response.read(MAX_RESPONSE + 1)
        except urllib.error.HTTPError as exc:
            exc.close()
            raise
        if len(raw) > MAX_RESPONSE: raise ValueError('Response too large')
        return json.loads(raw)

    def pair(self, code):
        result = self.post('/v1/pair', {'code': code})
        self.credential = result['credential']
        return result

    def request(self, action, args=None):
        rid = uuid.uuid4().hex
        result = self.post('/v1/request', {'version': 1, 'request_id': rid, 'action': action, 'args': args or {}})
        if result.get('version') != 1 or result.get('request_id') != rid:
            raise ValueError('Invalid bridge response')
        return result


class Controller:
    def __init__(self, client, clock=time.monotonic):
        self.client, self.clock = client, clock
        self.context = {'screen': 'now', 'query': '', 'kind': 'albums', 'offset': 0,
                        'cursor': None, 'result_id': None, 'scroll': 0, 'items': []}
        self.history = []
        self.snapshot = None
        self.online = False
        self.deadline = 0
        self.wake_contact = True
        self.pending = None
        self.generation = 0
        self.voice = 'idle'
        self.transcript = ''
        self.outcome = None
        self.selected = None
        self.busy = False
        self.retry_at, self.backoff = 0, 1

    @property
    def available(self):
        return self.online and self.clock() < self.deadline and not self.wake_contact and not self.busy

    def disconnect(self):
        self.generation += 1
        self.online = False
        self.deadline = 0
        if self.pending: self.outcome = 'unknown'
        self.pending = None
        self.wake_contact = True
        self.cancel_voice()

    def wake(self):
        self.disconnect()
        return self.reconnect()

    def touch(self, pressed):
        # Entire wake contact is consumed; only a later press may be accepted.
        if self.wake_contact:
            if not pressed: self.wake_contact = False
            return False
        return pressed

    def reconnect(self):
        generation = self.generation
        started = self.clock()
        try:
            result = self.client.request('snapshot')
            if generation != self.generation: return False
            if result['outcome'] != 'observed': raise RuntimeError()
            self.snapshot = result['data']
            # Includes request transit time conservatively; never extend freshness
            # just because a delayed response finally arrived.
            self.deadline = started + self.snapshot['valid_for_ms'] / 1000
            self.online = True
            self.backoff = 1
            return True
        except Exception:
            self.online = False
            self.retry_at = self.clock() + self.backoff * random.uniform(.8, 1.2)
            self.backoff = min(30, self.backoff * 2)
            return False

    def read(self, action, args=None):
        result = self.client.request(action, args)
        if result['outcome'] != 'observed': raise RuntimeError(result['error']['code'])
        return result['data']

    def search(self, query=None, kind=None, more=False):
        next_context = copy.deepcopy(self.context)
        if not more:
            next_context.update(query=query if query is not None else next_context['query'],
                                kind=kind or next_context['kind'], offset=0, cursor=None, result_id=None, scroll=0)
        args = {k: next_context[k] for k in ('query', 'kind', 'offset', 'cursor', 'result_id') if next_context[k] is not None}
        data = self.read('search', args)
        next_context.update(screen='find', items=data['items'], next_offset=data.get('next_offset'),
                            next_cursor=data.get('cursor'), result_id=data.get('result_id'))
        self.context = next_context

    def more(self):
        previous = copy.deepcopy(self.context)
        if self.context.get('next_offset') is not None:
            self.context['offset'] = self.context['next_offset']
        elif self.context.get('next_cursor'):
            self.context.update(offset=0, cursor=self.context['next_cursor'])
        else: return
        try: self.search(more=True)
        except Exception:
            self.context = previous
            raise

    def details(self, item):
        data = self.read('browse', {'reference': item['reference']})
        self.push('details')
        self.selected = data

    def push(self, screen):
        self.cancel_voice()
        self.history.append((copy.deepcopy(self.context), copy.deepcopy(self.selected)))
        self.history = self.history[-16:]
        self.context['screen'] = screen
        if screen == 'voice': self.record()

    def back(self):
        self.cancel_voice()
        if self.history: self.context, self.selected = self.history.pop()

    def mutate(self, action, args):
        if not self.available: return 'rejected'
        self.busy = True
        generation = self.generation
        self.pending = action
        try:
            result = self.client.request(action, args)
            if generation != self.generation: self.outcome = 'unknown'
            else: self.outcome = result['outcome']
        except Exception:
            self.outcome = 'unknown'
            self.disconnect()
        finally:
            self.pending = None
            self.busy = False
        # Authoritative READ only. Unknown volume is never corrected or retried.
        if generation == self.generation: self.reconnect()
        return self.outcome

    def record(self):
        if self.available:
            self.voice, self.transcript = 'recording_fixture', ''
            self.record_deadline = self.clock() + 30

    def stop_recording(self):
        if self.voice == 'recording_fixture': self.voice = 'stopped'

    def tick(self):
        if self.voice == 'recording_fixture' and self.clock() >= self.record_deadline:
            self.stop_recording()  # Never transcribe or search automatically.

    def cancel_voice(self):
        self.voice, self.transcript = 'idle', ''

    def submit_voice(self):
        if self.voice not in ('recording_fixture', 'stopped'): return
        self.stop_recording()
        query = self.read('voice_review', {'fixture': 'silent'})['transcript']
        self.cancel_voice()
        self.search(query)  # Suggestions and transcripts are searches only.
