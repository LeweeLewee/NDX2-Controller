"""Bridge-only durable authorization. Windows DPAPI; POSIX owner-only storage.

One service process owns a vault. No secret values are logged or returned by errors.
"""
import copy
import ctypes
import hashlib
import json
import os
from pathlib import Path
import secrets
import tempfile
import threading
import time


def _dpapi(raw, decrypt=False):
    from ctypes import wintypes
    class Blob(ctypes.Structure):
        _fields_ = [('size', wintypes.DWORD), ('data', ctypes.POINTER(ctypes.c_byte))]
    buf = ctypes.create_string_buffer(raw)
    source = Blob(len(raw), ctypes.cast(buf, ctypes.POINTER(ctypes.c_byte)))
    target = Blob()
    fn = ctypes.windll.crypt32.CryptUnprotectData if decrypt else ctypes.windll.crypt32.CryptProtectData
    if not fn(ctypes.byref(source), None, None, None, None, 1, ctypes.byref(target)):
        raise OSError('Protected storage unavailable')
    try:
        return ctypes.string_at(target.data, target.size)
    finally:
        ctypes.windll.kernel32.LocalFree(target.data)


class Vault:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        if self.directory.is_symlink():
            raise OSError('Vault must not be a symlink')
        if os.name != 'nt':
            if self.directory.stat().st_uid != os.getuid() or self.directory.stat().st_mode & 0o077:
                raise OSError('Vault requires owner-only directory')
        self.path = self.directory / 'authorization.bin'
        self.lock = threading.RLock()
        self.process_lock = open(self.directory / 'service.lock', 'a+b')
        self.process_lock.seek(0)
        if os.name == 'nt':
            import msvcrt
            if self.process_lock.read(1) == b'':
                self.process_lock.write(b'0'); self.process_lock.flush()
            self.process_lock.seek(0)
            msvcrt.locking(self.process_lock.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(self.process_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if self.path.exists():
            if self.path.is_symlink() or (os.name != 'nt' and self.path.stat().st_mode & 0o077):
                raise OSError('Unsafe authorization file')
            raw = self.path.read_bytes()
            self.data = json.loads(_dpapi(raw, True) if os.name == 'nt' else raw)
        else:
            self.data = {'devices': {}, 'commands': {}, 'refresh': None}

    def close(self):
        self.process_lock.close()

    def update(self, change):
        with self.lock:
            candidate = copy.deepcopy(self.data)
            change(candidate)
            raw = json.dumps(candidate, separators=(',', ':')).encode()
            if os.name == 'nt':
                raw = _dpapi(raw)
            fd, temp = tempfile.mkstemp(dir=self.directory)
            try:
                with os.fdopen(fd, 'wb') as stream:
                    stream.write(raw); stream.flush(); os.fsync(stream.fileno())
                os.replace(temp, self.path)
                if os.name != 'nt':
                    dfd = os.open(self.directory, os.O_RDONLY)
                    try: os.fsync(dfd)
                    finally: os.close(dfd)
                self.data = candidate
            finally:
                if os.path.exists(temp): os.unlink(temp)


class Pairing:
    def __init__(self, vault, clock=time.monotonic):
        self.vault, self.clock = vault, clock
        self.pending = None
        self.lock = threading.Lock()

    def issue(self):
        # Local console administration only; never an HTTP admin endpoint.
        with self.lock:
            code = secrets.token_urlsafe(24)
            self.pending = (code, self.clock() + 120, 0)
            return code

    def devices(self):
        """Local admin inventory: public IDs only, never credential hashes."""
        with self.vault.lock:
            return sorted(self.vault.data['devices'])

    def cancel(self):
        with self.lock:
            self.pending = None

    def pair(self, code):
        with self.lock:
            pending = self.pending
            if not pending or self.clock() >= pending[1] or pending[2] >= 5:
                self.pending = None
                raise PermissionError('Pairing unavailable')
            self.pending = (pending[0], pending[1], pending[2] + 1)
            if not isinstance(code, str) or not secrets.compare_digest(code, pending[0]):
                raise PermissionError('Pairing unavailable')
            self.pending = None
            device, token = secrets.token_hex(12), secrets.token_urlsafe(32)
            self.vault.update(lambda d: d['devices'].update({device: hashlib.sha256(token.encode()).hexdigest()}))
            return {'device': device, 'credential': token}

    def authenticate(self, token):
        digest = hashlib.sha256(token.encode()).hexdigest()
        with self.vault.lock:
            for device, expected in self.vault.data['devices'].items():
                if secrets.compare_digest(digest, expected): return device
        raise PermissionError('Authentication required')

    def revoke(self, device):
        self.vault.update(lambda d: d['devices'].pop(device, None))


class Renewal:
    """Single flight; durable rotation precedes publishing an access token.

    Provider must raise Revoked only for invalid_grant/revocation. Transient
    failures retain durable authorization and do not replay collection writes.
    """
    def __init__(self, vault, exchange, clock=time.monotonic):
        self.vault, self.exchange, self.clock = vault, exchange, clock
        self.lock = threading.Lock()
        self.access, self.expires = None, 0
        self.failed_until = 0
        self.storage_uncertain = False

    def get(self):
        with self.lock:
            if self.storage_uncertain: raise RuntimeError('Authorization storage requires recovery')
            if self.clock() < self.expires: return self.access
            if self.clock() < self.failed_until: raise RuntimeError('Renewal temporarily unavailable')
            old = self.vault.data['refresh']
            if not old: raise PermissionError('Account disconnected')
            try:
                data = self.exchange(old)
                access, lifetime = data['access_token'], data['expires_in']
                refresh = data.get('refresh_token', old)
                if (not isinstance(access, str) or not 1 <= len(access) <= 8192 or
                        '\r' in access or '\n' in access or not isinstance(refresh, str) or
                        not 1 <= len(refresh) <= 8192 or type(lifetime) not in (int, float) or
                        not 1 <= lifetime <= 86400):
                    raise ValueError('Invalid authorization response')
                try:
                    self.vault.update(lambda d: d.update(refresh=refresh))
                except Exception:
                    self.storage_uncertain = True
                    raise
            except Revoked:
                self.vault.update(lambda d: d.update(refresh=None))
                self.access, self.expires = None, 0
                raise PermissionError('Account disconnected') from None
            except Exception:
                self.failed_until = self.clock() + 2
                raise RuntimeError('Renewal temporarily unavailable') from None
            self.access, self.expires = access, self.clock() + lifetime * .9
            return access

    def disconnect(self):
        with self.lock:
            self.vault.update(lambda d: d.update(refresh=None))
            self.access, self.expires = None, 0
            self.storage_uncertain = False


class Revoked(Exception):
    pass
