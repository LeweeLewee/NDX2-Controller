"""Offline enrollment lifecycle, durable uncertainty and redaction."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
import urllib.error
from unittest.mock import Mock, patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from m2_security import Vault, Pairing
from m2_provisioning import Enrollment, EnrollmentError, controller_client

class ProvisioningTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.path=Path(self.temp.name)/'controller'
        self.vault=Vault(self.path); self.client=Mock()
        self.target={'origin':'https://fixture.invalid','trust_sha256':'a'*64}
        self.patcher=patch('m2_provisioning.binding',return_value=(self.client,self.target)); self.patcher.start()
        self.flow=Enrollment(self.vault,'https://fixture.invalid','unused')
        self.result={'device':'a'*24,'credential':'b'*43}; self.code='c'*32
        self.client.post.return_value=self.result
        self.client.request.return_value={'outcome':'observed','fixture':True}
    def tearDown(self):
        self.patcher.stop(); self.vault.close(); self.temp.cleanup()
    def reopen(self):
        self.vault.close(); self.vault=Vault(self.path)
        self.flow=Enrollment(self.vault,'https://fixture.invalid','unused')
    def test_pair_persist_restart_verify_and_redaction(self):
        result=self.flow.pair(self.code); self.reopen()
        self.assertEqual(self.flow.status(),result)
        self.assertEqual(self.flow.verify()['state'],'connected')
        self.assertNotIn(self.result['credential'],json.dumps(result))
        self.assertNotIn(self.code,json.dumps(self.vault.data))
        self.client.post.assert_called_once()
    def test_pending_saved_before_network_and_lost_reply_never_retried(self):
        def lose(*_):
            self.assertEqual(self.vault.data['enrollment']['state'],'pending')
            raise TimeoutError('synthetic secret '+self.code)
        self.client.post.side_effect=lose
        with self.assertRaisesRegex(EnrollmentError,'^PAIRING_OUTCOME_UNKNOWN$'): self.flow.pair(self.code)
        self.reopen(); self.assertEqual(self.flow.status()['state'],'outcome_unknown')
        with self.assertRaisesRegex(EnrollmentError,'LOCAL_RECOVERY_REQUIRED'): self.flow.pair(self.code)
        self.client.post.assert_called_once()
    def test_storage_failure_prevents_remote_pairing(self):
        with patch.object(self.vault,'update',side_effect=OSError('private path')):
            with self.assertRaisesRegex(EnrollmentError,'^STORAGE_UNCERTAIN$'): self.flow.pair(self.code)
        self.client.post.assert_not_called()
        self.assertEqual(self.flow.status()['state'],'storage_uncertain')
    def test_storage_failure_after_issue_keeps_durable_pending(self):
        update=self.vault.update; calls=0
        def fail(change):
            nonlocal calls
            calls+=1
            if calls==2: raise OSError()
            update(change)
        with patch.object(self.vault,'update',side_effect=fail):
            with self.assertRaises(EnrollmentError): self.flow.pair(self.code)
        self.reopen(); self.assertEqual(self.flow.status()['state'],'outcome_unknown')
        self.assertNotIn('controller',self.vault.data)
        self.client.post.assert_called_once()
    def test_malformed_reply_is_not_saved_or_retried(self):
        self.client.post.return_value={'device':'a'*24,'credential':'bad\nheader'}
        with self.assertRaises(EnrollmentError): self.flow.pair(self.code)
        self.assertNotIn('controller',self.vault.data)
        self.assertEqual(self.flow.status()['state'],'outcome_unknown')
    def test_existing_pair_not_overwritten(self):
        self.flow.pair(self.code)
        with self.assertRaises(EnrollmentError): self.flow.pair(self.code)
        self.client.post.assert_called_once()
    def test_origin_or_trust_change_blocks_credentials_before_network(self):
        self.flow.pair(self.code)
        for field in self.target:
            changed={**self.target,field:'different'}
            with patch('m2_provisioning.binding',return_value=(Mock(),changed)):
                with self.assertRaisesRegex(EnrollmentError,'ENROLLMENT_REQUIRED'): self.flow.verify()
        self.client.request.assert_not_called()
    def test_revocation_blocks_following_requests_and_survives_restart(self):
        self.flow.pair(self.code)
        self.client.request.side_effect=urllib.error.HTTPError('fixture',401,'unauthorized',{},None)
        with self.assertRaisesRegex(EnrollmentError,'AUTHORIZATION_REQUIRED'): self.flow.verify()
        self.reopen(); self.assertEqual(self.flow.status()['state'],'authorization_required')
        with self.assertRaises(EnrollmentError): self.flow.verify()
        self.client.request.assert_called_once()
    def test_outage_preserves_pair_and_explicit_read_recovers(self):
        self.flow.pair(self.code); self.client.request.side_effect=TimeoutError()
        with self.assertRaisesRegex(EnrollmentError,'BRIDGE_UNAVAILABLE'): self.flow.verify()
        self.assertEqual(self.flow.status()['state'],'paired')
        self.client.request.side_effect=None; self.assertEqual(self.flow.verify()['state'],'connected')
        self.client.post.assert_called_once()
    def test_forget_is_local_and_preserves_other_state(self):
        self.vault.update(lambda d:d.update(display={'palette':1},refresh='synthetic-provider'))
        self.flow.pair(self.code); self.flow.forget()
        self.assertEqual(self.flow.status()['state'],'unpaired')
        self.assertEqual(self.vault.data['display'],{'palette':1})
        self.assertEqual(self.vault.data['refresh'],'synthetic-provider')
        self.client.post.assert_called_once()
    def test_admin_inventory_cancel_and_revoke_storage_failure(self):
        pairing=Pairing(self.vault); code=pairing.issue(); pairing.cancel()
        with self.assertRaises(PermissionError): pairing.pair(code)
        result=pairing.pair(pairing.issue()); self.assertEqual(pairing.devices(),[result['device']])
        with patch.object(self.vault,'update',side_effect=OSError()):
            with self.assertRaises(OSError): pairing.revoke(result['device'])
        self.assertEqual(pairing.authenticate(result['credential']),result['device'])
        pairing.revoke(result['device']); self.assertEqual(pairing.devices(),[])
    def test_invalid_code_never_reaches_network_or_storage(self):
        with self.assertRaisesRegex(EnrollmentError,'INVALID_SETUP_CODE'): self.flow.pair('invalid')
        self.client.post.assert_not_called(); self.assertNotIn('enrollment',self.vault.data)

    def test_bound_record_cannot_downgrade_to_legacy_or_unknown_version(self):
        self.flow.pair(self.code)
        self.vault.update(lambda d:d.pop('enrollment'))
        with self.assertRaises(EnrollmentError): controller_client(self.vault,'unused','unused')
        self.assertEqual(self.flow.status()['state'],'recovery_required')
        self.vault.update(lambda d:d.update(enrollment={'version':2}))
        self.assertEqual(self.flow.status()['state'],'recovery_required')
        with self.assertRaises(EnrollmentError): self.flow.pair(self.code)
        with self.assertRaises(EnrollmentError): controller_client(self.vault,'unused','unused')
        self.client.request.assert_not_called()

    def test_trust_update_verifies_once_preserves_identity_and_history(self):
        self.flow.pair(self.code)
        self.vault.update(lambda d:d['commands'].update(previous={'outcome':'unknown'}))
        new={**self.target,'trust_sha256':'f'*64}
        with patch('m2_provisioning.binding',return_value=(self.client,new)):
            flow=Enrollment(self.vault,'unused','unused'); flow.update_trust()
        self.assertEqual(self.vault.data['controller']['credential'],self.result['credential'])
        self.assertEqual(self.vault.data['controller']['trust_sha256'],'f'*64)
        self.assertIn('previous',self.vault.data['commands'])
        self.client.post.assert_called_once(); self.client.request.assert_called_once_with('snapshot')
        self.reopen(); self.assertEqual(self.vault.data['controller']['trust_sha256'],'f'*64)
    def test_trust_update_failure_and_interruption_retain_old_binding(self):
        self.flow.pair(self.code)
        new={**self.target,'trust_sha256':'f'*64}
        with patch('m2_provisioning.binding',return_value=(self.client,new)):
            flow=Enrollment(self.vault,'unused','unused')
            for error in (TimeoutError(),KeyboardInterrupt()):
                self.client.request.side_effect=error
                with self.assertRaises((EnrollmentError,KeyboardInterrupt)): flow.update_trust()
                self.assertEqual(self.vault.data['controller']['trust_sha256'],self.target['trust_sha256'])
        self.client.post.assert_called_once()
    def test_trust_update_storage_failure_does_not_publish_success(self):
        self.flow.pair(self.code)
        new={**self.target,'trust_sha256':'f'*64}
        with patch('m2_provisioning.binding',return_value=(self.client,new)):
            flow=Enrollment(self.vault,'unused','unused')
            with patch.object(self.vault,'update',side_effect=OSError()):
                with self.assertRaisesRegex(EnrollmentError,'STORAGE_UNCERTAIN'): flow.update_trust()
            self.assertEqual(flow.status()['state'],'storage_uncertain')
        self.reopen(); self.assertEqual(self.vault.data['controller']['trust_sha256'],self.target['trust_sha256'])
    def test_trust_commit_then_failure_requires_reopen_without_rollback(self):
        self.flow.pair(self.code); update=self.vault.update
        def committed(change):
            update(change); raise OSError()
        new={**self.target,'trust_sha256':'f'*64}
        with patch('m2_provisioning.binding',return_value=(self.client,new)):
            flow=Enrollment(self.vault,'unused','unused')
            with patch.object(self.vault,'update',side_effect=committed):
                with self.assertRaisesRegex(EnrollmentError,'STORAGE_UNCERTAIN'): flow.update_trust()
            with self.assertRaises(EnrollmentError): flow.update_trust()
        self.reopen(); self.assertEqual(self.flow.status()['trust_sha256'],'f'*64)
        self.client.request.assert_called_once_with('snapshot')
    def test_trust_update_rejects_origin_change_before_sending_credential(self):
        self.flow.pair(self.code)
        with patch('m2_provisioning.binding',return_value=(self.client,{**self.target,'origin':'https://other.invalid'})):
            flow=Enrollment(self.vault,'unused','unused')
            with self.assertRaises(EnrollmentError): flow.update_trust()
        self.client.request.assert_not_called()
    def test_trust_file_change_after_confirmation_is_rejected(self):
        self.flow.pair(self.code)
        with patch('m2_provisioning.binding',return_value=(self.client,{**self.target,'trust_sha256':'f'*64})):
            with self.assertRaisesRegex(EnrollmentError,'TRUST_CHANGED'): self.flow.update_trust()
        self.client.request.assert_not_called()

    def test_revoked_or_legacy_enrollment_cannot_use_trust_update(self):
        self.flow.pair(self.code)
        self.vault.update(lambda d:d.update(enrollment={'version':1,'state':'authorization_required'}))
        with self.assertRaises(EnrollmentError): self.flow.update_trust()
        self.vault.update(lambda d:d.pop('enrollment'))
        with self.assertRaises(EnrollmentError): self.flow.update_trust()
        self.client.request.assert_not_called()
