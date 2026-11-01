import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from pi_bridge import allowed, atomic_json, TrialPairing, ConnectedBridge, TrialContract
from m2_bridge import FixtureService, ContractError
from m2_security import Vault
from package_pi_bridge import build


class PiBridgeTests(unittest.TestCase):
    def test_trial_controls_keep_native_bounded_scope(self):
        for command in ('pause', 'resume', 'next', 'prev'):
            self.assertFalse(allowed('transport', {'command': command}, False))
            self.assertTrue(allowed('transport', {'command': command}, True))
        self.assertFalse(allowed('transport', {'command': 'toggle'}, True))
        self.assertFalse(allowed('library_save', {'saved': True}, True))
        self.assertFalse(allowed('amplifier', {'direction': 'up', 'level': 100}, True))
        for reference in ('inputs/tidal/albums/123', 'inputs/tidal/tracks/456', 'inputs/playqueue/7'):
            self.assertTrue(allowed('play', {'reference': reference}, True))
        for reference in ('http://example.test/audio', 'inputs/tidal/playlists/123', 'inputs/tidal/tracks/12/../4'):
            self.assertFalse(allowed('play', {'reference': reference}, True))

    def test_read_only_gate_precedes_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Vault(Path(directory) / 'vault')
            try:
                contract = TrialContract(FixtureService(), vault)
                with self.assertRaises(ContractError):
                    contract._execute('device', 'id', 'transport', {'command': 'resume'})
            finally:
                vault.close()

    def test_pairing_ten_minutes_five_attempts_one_use(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Vault(Path(directory) / 'vault')
            try:
                now = [1000]
                pairing = TrialPairing(vault, clock=lambda: now[0])
                code = pairing.issue()
                self.assertRegex(code, r'^\d{8}$')
                now[0] += 599
                paired = pairing.pair(code)
                self.assertEqual(pairing.authenticate(paired['credential']), paired['device'])
                with self.assertRaises(PermissionError): pairing.pair(code)
                code = pairing.issue()
                now[0] += 600
                with self.assertRaises(PermissionError): pairing.pair(code)
                code = pairing.issue()
                for _ in range(5):
                    with self.assertRaises(PermissionError): pairing.pair('invalid')
                with self.assertRaises(PermissionError): pairing.pair(code)
            finally:
                vault.close()

    def test_rotated_account_is_durable(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Vault(Path(directory) / 'vault')
            try:
                vault.update(lambda d: d.update(tidal={'client_id': 'fixture', 'client_secret': 'fixture',
                             'token': 'old', 'refresh_token': 'old-refresh', 'expires_at': 0}))
                service = ConnectedBridge(object(), vault)
                def rotated(*_):
                    service.library.token = 'new'
                    service.library.refresh_token = 'new-refresh'
                    return {'items': []}
                with patch('pi_bridge.Bridge.request', side_effect=rotated):
                    service.request('library_page', {'kind': 'albums'})
            finally:
                vault.close()
            vault = Vault(Path(directory) / 'vault')
            try:
                self.assertEqual(vault.data['tidal']['refresh_token'], 'new-refresh')
                self.assertEqual(vault.data['tidal']['token'], 'new')
            finally:
                vault.close()

    def test_package_excludes_state_and_atomic_status(self):
        with tempfile.TemporaryDirectory() as directory:
            output = build(Path(directory) / 'app')
            self.assertTrue((output / 'tools/pi_bridge.py').is_file())
            self.assertFalse(list(output.rglob('*.bin')))
            self.assertFalse(list(output.rglob('*.pem')))
            self.assertFalse((output / 'local').exists())
            status = Path(directory) / 'status.json'
            atomic_json(status, {'uptime': 5})
            atomic_json(status, {'uptime': 10})
            self.assertEqual(json.loads(status.read_text()), {'uptime': 10})
            if os.name != 'nt': self.assertEqual(status.stat().st_mode & 0o777, 0o600)


if __name__ == '__main__': unittest.main()
