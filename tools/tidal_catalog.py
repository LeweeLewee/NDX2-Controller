"""Experimental TIDAL catalogue metadata adapter. No audio or player calls.

Uses this project's own TIDAL developer credentials, never Naim credentials.
Live search and compatibility of returned IDs with Naim remain unverified.
"""
import argparse
import base64
import getpass
import json
import math
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

from naim_native_probe import NoRedirect

KINDS = ('tracks', 'albums', 'artists', 'playlists')
MAX_BYTES = 2 * 1024 * 1024


class CatalogError(RuntimeError):
    pass


def candidate_reference(kind, item_id):
    """A candidate only: resolve it through Naim browse before using it."""
    if kind not in KINDS or not isinstance(item_id, str):
        return None
    pattern = r'[A-Za-z0-9_-]{1,128}' if kind == 'playlists' else r'[0-9]{1,32}'
    if not re.fullmatch(pattern, item_id):
        return None
    return 'inputs/tidal/' + kind + '/' + item_id


class TidalCatalog:
    def __init__(self, client_id, client_secret, country='GB', opener=None, clock=time.monotonic):
        if not isinstance(client_id, str) or not isinstance(client_secret, str) or not client_id or not client_secret:
            raise ValueError('TIDAL developer client ID and secret are required')
        if not re.fullmatch(r'[A-Z]{2}', country):
            raise ValueError('Use a two-letter uppercase country code')
        self._client_id, self._client_secret = client_id, client_secret
        self.country = country
        self.opener = opener or urllib.request.build_opener(NoRedirect())
        self.clock, self._expires, self._token = clock, 0, None

    def _json(self, request):
        try:
            with self.opener.open(request, timeout=10) as response:
                raw = response.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise CatalogError('TIDAL response exceeded size limit')
            data = json.loads(raw)
            if not isinstance(data, dict):
                raise ValueError()
            return data
        except urllib.error.HTTPError as exc:
            # Never retain/print server bodies, which can reflect credentials.
            raise CatalogError('TIDAL request failed (HTTP ' + str(exc.code) + ')') from None
        except (urllib.error.URLError, TimeoutError, OSError):
            raise CatalogError('TIDAL connection failed or timed out') from None
        except (ValueError, UnicodeError):
            raise CatalogError('TIDAL returned invalid JSON data') from None

    def _access_token(self):
        if self._token and self.clock() < self._expires:
            return self._token
        credential = base64.b64encode((self._client_id + ':' + self._client_secret).encode()).decode('ascii')
        request = urllib.request.Request('https://auth.tidal.com/v1/oauth2/token',
            data=b'grant_type=client_credentials', method='POST',
            headers={'Authorization': 'Basic ' + credential, 'Content-Type': 'application/x-www-form-urlencoded'})
        data = self._json(request)
        token = data.get('access_token')
        try:
            lifetime = float(data.get('expires_in', 0))
        except (ValueError, TypeError):
            lifetime = 0
        if not isinstance(token, str) or not token or '\r' in token or '\n' in token or not math.isfinite(lifetime) or lifetime <= 0:
            raise CatalogError('TIDAL returned invalid token metadata')
        self._token = token
        self._expires = self.clock() + lifetime * 0.9
        return token

    def _get(self, path, params):
        request = urllib.request.Request('https://openapi.tidal.com/v2/' + path + '?' + urllib.parse.urlencode(params),
            headers={'Accept': 'application/vnd.api+json', 'Authorization': 'Bearer ' + self._access_token()})
        return self._json(request)

    def search(self, query, kind='tracks'):
        if kind not in KINDS or not isinstance(query, str) or not 1 <= len(query.strip()) <= 256:
            raise ValueError('Use a 1..256 character search and a supported type')
        return self._get('searchResults', {'filter[query]': query.strip(), 'countryCode': self.country, 'include': kind})

    def page(self, result_id, kind, cursor=None):
        # Current API IDs are opaque; do not substitute the search text for ID.
        if kind not in KINDS or not isinstance(result_id, str) or not 1 <= len(result_id) <= 2048 or result_id in ('.', '..'):
            raise ValueError('Expected a returned search-results ID')
        params = {'countryCode': self.country, 'include': kind}
        if cursor is not None:
            if not isinstance(cursor, str) or not 1 <= len(cursor) <= 4096:
                raise ValueError('Expected a returned page cursor')
            params['page[cursor]'] = cursor
        return self._get('searchResults/' + urllib.parse.quote(result_id, safe='') + '/relationships/' + kind, params)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query')
    parser.add_argument('--kind', choices=KINDS, default='tracks')
    parser.add_argument('--country', default='GB')
    args = parser.parse_args()
    client_id = os.environ.get('TIDAL_CLIENT_ID') or getpass.getpass('TIDAL developer client ID: ')
    secret = os.environ.get('TIDAL_CLIENT_SECRET') or getpass.getpass('TIDAL developer client secret: ')
    try:
        result = TidalCatalog(client_id, secret, args.country).search(args.query, args.kind)
        items = []
        for item in result.get('included', []):
            if item.get('type') != args.kind:
                continue
            attrs = item.get('attributes', {})
            items.append({'id': item.get('id'), 'title': attrs.get('title', attrs.get('name')),
                          'candidate_native_reference': candidate_reference(args.kind, item.get('id'))})
        print(json.dumps({'items': items, 'native_playback_verified': False}, ensure_ascii=False, indent=2))
    except (CatalogError, ValueError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
