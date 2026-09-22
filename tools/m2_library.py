"""Persistent account adapter; retains prototype PKCE/scopes and write-once/read-back."""
import json
import threading
import urllib.parse
import urllib.request
from tidal_library import TidalLibrary, SCOPES, LibraryError
from tidal_catalog import CatalogError
from m2_security import Renewal, Revoked


class PersistentLibrary(TidalLibrary):
    def __init__(self, catalog, vault, **kwargs):
        super().__init__(catalog, **kwargs)
        self.vault = vault
        self.session_lock = threading.RLock()
        self.renewal = Renewal(vault, self.exchange, self.clock)

    @property
    def connected(self):
        return bool(self.vault.data['refresh'] or (self.token and self.clock() < self.expires))

    def exchange(self, refresh):
        try:
            data = self.catalog._json(urllib.request.Request('https://auth.tidal.com/v1/oauth2/token',
                data=urllib.parse.urlencode({'client_id': self.catalog._client_id,
                     'grant_type': 'refresh_token', 'refresh_token': refresh}).encode(),
                headers={'Content-Type': 'application/x-www-form-urlencoded'}, method='POST'))
        except CatalogError as exc:
            # Only a whitelisted OAuth error survives adapter sanitization.
            if exc.oauth_error == 'invalid_grant': raise Revoked() from None
            raise
        if not set(SCOPES.split()).issubset(set(data.get('scope', '').split())):
            raise Revoked()
        return data

    def _tokens(self, fields):
        # Prototype code validates OAuth state, PKCE, token syntax and scopes.
        with self.session_lock:
            old = (self.token, self.refresh_token, self.expires)
            try:
                super()._tokens(fields)
                if not self.refresh_token: raise LibraryError('Persistent refresh authorization required')
                self.vault.update(lambda d: d.update(refresh=self.refresh_token))
                self.renewal.access, self.renewal.expires = self.token, self.expires
            except Exception:
                self.token, self.refresh_token, self.expires = old
                raise

    def _request(self, *args, **kwargs):
        with self.session_lock:
            try:
                self.token = self.renewal.get()
            except PermissionError:
                self.token = self.refresh_token = None
                self.expires = 0
                self.cache.clear()
                raise
            self.expires = self.renewal.expires
            self.refresh_token = self.vault.data['refresh']
            return super()._request(*args, **kwargs)

    def disconnect(self):
        with self.session_lock:
            self.renewal.disconnect()
            super().disconnect()
