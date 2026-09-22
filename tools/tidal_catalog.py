"""Experimental TIDAL catalogue metadata adapter. No audio or player calls.

Uses this project's own TIDAL developer credentials, never Naim credentials.
Live search and pagination passed; returned IDs still need Naim verification.
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
    def __init__(self, message, status=None, retry_after=None, oauth_error=None):
        super().__init__(message)
        self.status, self.retry_after = status, retry_after
        self.oauth_error = oauth_error


def ordered_items(page, kind):
    """Resolve a relationship page in result order, not included-object order."""
    included = {(item.get('type'), item.get('id')): item
                for item in (page.get('included') or []) if isinstance(item, dict)}
    items = []
    for reference in (page.get('data') or []):
        if reference.get('type') != kind:
            continue
        item = included.get((kind, reference.get('id')), reference)
        attrs = item.get('attributes') or {}
        items.append({'id': item.get('id'), 'title': attrs.get('title', attrs.get('name')),
                      'candidate_native_reference': candidate_reference(kind, item.get('id'))})
    return items


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
            oauth_error = None
            try:
                body = exc.read(8193)
                if len(body) <= 8192 and json.loads(body).get('error') == 'invalid_grant':
                    oauth_error = 'invalid_grant'
            except (ValueError, AttributeError, OSError):
                pass
            finally:
                exc.close()
            try:
                retry_after = float(exc.headers.get('Retry-After', '2'))
            except (TypeError, ValueError):
                retry_after = 2
            raise CatalogError('TIDAL request failed (HTTP ' + str(exc.code) + ')',
                               exc.code, retry_after, oauth_error) from None
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

    def related(self, reference):
        """Resolve exact album/artist relationships, never a title-search guess."""
        parts = reference.split('/') if isinstance(reference, str) else []
        if len(parts) != 4 or parts[2] not in ('tracks', 'albums') or candidate_reference(parts[2], parts[3]) != reference:
            raise ValueError('Expected a TIDAL track or album')
        kinds = ('albums', 'artists') if parts[2] == 'tracks' else ('artists',)
        data = self._get(parts[2] + '/' + parts[3], {'countryCode': self.country, 'include': ','.join(kinds)})
        resource = data.get('data') or {}
        if resource.get('type') != parts[2] or resource.get('id') != parts[3]:
            raise CatalogError('TIDAL returned a different item')
        result = []
        for kind in kinds:
            page = {'data': (resource.get('relationships', {}).get(kind) or {}).get('data'),
                    'included': data.get('included')}
            for item in ordered_items(page, kind):
                if item['candidate_native_reference']:
                    result.append({'reference': item['candidate_native_reference'], 'kind': kind,
                                   'title': item['title'] or kind[:-1].title(), 'artist': ''})
        return result

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
        catalog = TidalCatalog(client_id, secret, args.country)
        result = catalog.search(args.query, args.kind)
        resources = result.get('data', [])
        if isinstance(resources, dict):
            resources = [resources]
        items = ordered_items(catalog.page(resources[0]['id'], args.kind), args.kind) if resources else []
        print(json.dumps({'items': items, 'native_playback_verified': False}, ensure_ascii=False, indent=2))
    except (CatalogError, ValueError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
