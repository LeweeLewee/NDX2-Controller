"""Small native Naim control client; never fetches or supplies audio URLs.

Experimental API 1.4.0 support. Caller owns user authorization for mutations.
Search and authentication are deliberately not implemented.
"""
import ipaddress
import json
import re
import time
import urllib.parse
import urllib.request

from naim_native_probe import MAX_BYTES, NoRedirect


def native_ref(value, queue=False):
    pattern = r'inputs/playqueue/[0-9]+' if queue else r'inputs/tidal/(?:tracks|albums|playlists)/[A-Za-z0-9_-]+'
    if not isinstance(value, str) or not re.fullmatch(pattern, value):
        raise ValueError('Expected a native reference returned by the NDX')
    return value


def playback_state(data):
    """Observed firmware values; retain unknown values rather than guess."""
    return {'1': 'stopped', '2': 'playing', '3': 'paused'}.get(str(data.get('transportState')), 'unknown')


class NaimClient:
    def __init__(self, address, opener=None, timeout=8):
        ip = ipaddress.IPv4Address(address)
        if not any(ip in ipaddress.IPv4Network(net) for net in ('10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16')):
            raise ValueError('Use a private LAN IPv4 address')
        self.base = 'http://' + str(ip) + ':15081/'
        self.opener = opener or urllib.request.build_opener(NoRedirect())
        self.timeout = timeout

    def _request(self, path, method='GET', **params):
        url = self.base + path
        if params:
            url += '?' + urllib.parse.urlencode(params)
        request = urllib.request.Request(url, method=method, headers={'Accept': 'application/json'})
        # Mutations are never automatically retried: timeouts may follow success.
        with self.opener.open(request, timeout=self.timeout) as response:
            raw = response.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise ValueError('Response too large')
            result = json.loads(raw) if raw else {}
            if not isinstance(result, dict):
                raise ValueError('Expected a JSON object')
            return result

    def status(self):
        return self._request('nowplaying')

    def amplifier_nudge(self, direction):
        """Verified System Automation burst, not a digital volume target.

        One press frame followed by four held frames. No retries or restoration:
        an uncertain response may already have moved the physical amplifier.
        """
        if direction not in ('down', 'up'):
            raise ValueError('Expected amplifier direction down or up')
        self.status()
        if str(self._request('automation').get('enabled')) != '1':
            raise ValueError('System Automation is not enabled on this NDX')
        command = 'irVolumeDown' if direction == 'down' else 'irVolumeUp'
        for repeat in ('false', 'true', 'true', 'true', 'true'):
            self._request('automation', cmd=command, repeat=repeat)
            time.sleep(0.2)
        self.status()

    def queue(self):
        # Firmware ignores limit on this endpoint; bound the response in bytes.
        return self._request('inputs/playqueue')

    def browse(self, reference='inputs/tidal/favourites', offset=0, limit=20):
        if not isinstance(reference, str) or not re.fullmatch(r'inputs/tidal/(?:favourites(?:/(?:albums|artists|tracks|playlists))?|(?:albums|artists|tracks|playlists)/[A-Za-z0-9_-]+)', reference):
            raise ValueError('Unsupported native browse reference')
        if type(offset) is not int or offset < 0 or type(limit) is not int or not 1 <= limit <= 50:
            raise ValueError('Invalid page bounds')
        return self._request(reference, offset=offset, limit=limit)

    def play(self, reference, placement='replace'):
        command = {'replace': 'play', 'next': 'playNext', 'last': 'playLast'}.get(placement)
        if command is None:
            raise ValueError('Unknown placement')
        return self._request(native_ref(reference), cmd=command)

    def transport(self, command, position_ms=None):
        if command not in ('play', 'pause', 'resume', 'stop', 'next', 'prev', 'seek'):
            raise ValueError('Unsupported transport command')
        params = {'cmd': command}
        if command == 'seek':
            if type(position_ms) is not int or position_ms < 0:
                raise ValueError('Seek requires nonnegative milliseconds')
            params['position'] = position_ms
        elif position_ms is not None:
            raise ValueError('Position only applies to seek')
        return self._request('nowplaying', **params)

    def move(self, reference, before):
        return self._request('inputs/playqueue', cmd='move', what=native_ref(reference, True), where=native_ref(before, True))

    def remove(self, reference):
        return self._request(native_ref(reference, True), method='DELETE')

    def select(self, reference):
        return self._request('inputs/playqueue', method='PUT', current=native_ref(reference, True))
