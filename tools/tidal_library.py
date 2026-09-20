"""TIDAL My Collection, using the project's own OAuth account authorization.

Tokens stay in memory. This adapter has no audio or Naim playback methods.
"""
import base64
import hashlib
import json
import math
import re
import secrets
import time
import urllib.parse
import urllib.request

from tidal_catalog import CatalogError, candidate_reference, ordered_items

SCOPES = 'collection.read collection.write'
KINDS = ('albums', 'tracks', 'artists', 'playlists')


class LibraryError(CatalogError):
    pass


class TidalLibrary:
    def __init__(self, catalog, clock=time.monotonic, sleep=time.sleep):
        self.catalog, self.clock = catalog, clock
        self.pending = None
        self.token = self.refresh_token = None
        self.expires = 0
        self.cache = {}
        self.sleep, self.last_read = sleep, 0

    @property
    def connected(self):
        return bool(self.token and (self.clock() < self.expires or self.refresh_token))

    def begin(self, redirect):
        if not re.fullmatch(r'http://127\.0\.0\.1:[0-9]{4,5}/oauth/callback', redirect):
            raise ValueError('Use the registered loopback callback')
        verifier, state = secrets.token_urlsafe(48), secrets.token_urlsafe(32)
        self.pending = (state, verifier, redirect, self.clock() + 600)
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=')
        return 'https://login.tidal.com/authorize?' + urllib.parse.urlencode({
            'response_type': 'code', 'client_id': self.catalog._client_id,
            'redirect_uri': redirect, 'scope': SCOPES, 'state': state,
            'code_challenge': challenge, 'code_challenge_method': 'S256'})

    def _tokens(self, fields):
        data = self.catalog._json(urllib.request.Request('https://auth.tidal.com/v1/oauth2/token',
            data=urllib.parse.urlencode({'client_id': self.catalog._client_id, **fields}).encode(),
            headers={'Content-Type': 'application/x-www-form-urlencoded'}, method='POST'))
        token = data.get('access_token')
        try:
            lifetime = float(data.get('expires_in', 0))
        except (TypeError, ValueError):
            lifetime = 0
        if not isinstance(token, str) or not token or '\r' in token or '\n' in token or not math.isfinite(lifetime) or lifetime <= 0:
            raise LibraryError('TIDAL returned invalid authorization metadata')
        if not set(SCOPES.split()).issubset(set(data.get('scope', '').split())):
            raise LibraryError('TIDAL did not grant collection read and write access')
        self.token, self.expires = token, self.clock() + lifetime * .9
        self.refresh_token = data.get('refresh_token', self.refresh_token)

    def finish(self, params):
        pending = self.pending
        supplied = params.get('state', [])
        if not pending or len(supplied) != 1 or not secrets.compare_digest(supplied[0], pending[0]):
            raise LibraryError('Unrecognized sign-in response. Start again from Collection.')
        self.pending = None
        if self.clock() >= pending[3] or params.get('error'):
            raise LibraryError('Sign-in expired or was declined. Start again from Collection.')
        code = params.get('code', [])
        if len(code) != 1 or not 1 <= len(code[0]) <= 4096:
            raise LibraryError('Missing sign-in code')
        self._tokens({'grant_type': 'authorization_code', 'code': code[0],
                      'redirect_uri': pending[2], 'code_verifier': pending[1]})
        self.cache.clear()

    def disconnect(self):
        self.token = self.refresh_token = self.pending = None
        self.expires = 0
        self.cache.clear()

    def _request(self, kind, method='GET', params=None, item_id=None):
        if kind not in KINDS:
            raise ValueError('Unsupported collection type')
        if not self.connected:
            raise LibraryError('Connect your TIDAL library from Collection first.')
        if self.clock() >= self.expires:
            try:
                self._tokens({'grant_type': 'refresh_token', 'refresh_token': self.refresh_token})
            except CatalogError:
                self.disconnect()
                raise LibraryError('TIDAL sign-in expired. Reconnect from Collection.') from None
        url = 'https://openapi.tidal.com/v2/userCollection' + kind.capitalize() + '/me/relationships/items'
        if params:
            url += '?' + urllib.parse.urlencode(params)
        body = None if item_id is None else json.dumps({'data': [{'type': kind, 'id': item_id}]}).encode()
        request = urllib.request.Request(url, data=body, method=method,
            headers={'Authorization': 'Bearer ' + self.token, 'Accept': 'application/vnd.api+json',
                     'Content-Type': 'application/vnd.api+json'})
        if method == 'GET':
            # Large libraries must not exhaust the service's per-endpoint burst limit.
            self.sleep(max(0, .4 - (self.clock() - self.last_read)))
            self.last_read = self.clock()
        try:
            return self.catalog._json(request)
        except CatalogError as exc:
            if method == 'GET' and exc.status == 429 and isinstance(exc.retry_after, (int, float)) and math.isfinite(exc.retry_after) and 0 <= exc.retry_after <= 15:
                self.sleep(max(1, exc.retry_after))
                self.last_read = self.clock()
                return self.catalog._json(request)
            # Never retry a write: the service may have applied it already.
            raise

    def page(self, kind, cursor=None):
        if cursor is not None and (not isinstance(cursor, str) or len(cursor) > 4096):
            raise ValueError('Invalid collection cursor')
        params = {'include': 'items'}
        if cursor:
            params['page[cursor]'] = cursor
        data = self._request(kind, params=params)
        link = data.get('links', {}).get('next')
        if isinstance(link, dict):
            link = link.get('href')
        next_cursor = urllib.parse.parse_qs(urllib.parse.urlsplit(link or '').query).get('page[cursor]', [None])[0]
        if link and not next_cursor:
            raise LibraryError('TIDAL returned unsupported collection pagination')
        return {'items': [{'reference': i['candidate_native_reference'], 'title': i['title'] or i['id'],
                           'kind': kind, 'artist': '', 'saved': True} for i in ordered_items(data, kind)],
                'cursor': next_cursor}

    def contains(self, reference, fresh=False):
        kind, item_id = self.parse(reference)
        cached = self.cache.get(kind)
        if not fresh and cached and self.clock() < cached[0]:
            return reference in cached[1]
        seen, refs, cursor = set(), set(), None
        # Never turn a partial collection read into an incorrect empty heart.
        for _ in range(100):
            page = self.page(kind, cursor)
            refs.update(i['reference'] for i in page['items'])
            cursor = page['cursor']
            if not cursor:
                self.cache[kind] = (self.clock() + 60, refs)
                return reference in refs
            if cursor in seen:
                break
            seen.add(cursor)
        raise LibraryError('Collection is too large to verify saved state. No changes made.')

    @staticmethod
    def parse(reference):
        parts = reference.split('/') if isinstance(reference, str) else []
        if len(parts) != 4 or candidate_reference(parts[2], parts[3]) != reference:
            raise ValueError('Invalid TIDAL item')
        return parts[2], parts[3]

    def save(self, reference, saved):
        kind, item_id = self.parse(reference)
        if type(saved) is not bool:
            raise ValueError('Expected saved boolean')
        previous = self.contains(reference, fresh=True)
        if previous != saved:
            self.cache.pop(kind, None)
            self._request(kind, 'POST' if saved else 'DELETE', item_id=item_id)
        actual = self.contains(reference, fresh=True)
        if actual != saved:
            raise LibraryError('TIDAL has not confirmed the change. Refresh before trying again.')
        return {'saved': actual, 'message': 'Saved to TIDAL collection.' if actual else 'Removed from TIDAL collection.'}
