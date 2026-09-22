"""Operator console behavior; all configuration and codes are synthetic."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import m2_setup
from m2_provisioning import EnrollmentError

class SetupTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); root=Path(self.temp.name)
        self.config=root/'desktop.json'
        self.config.write_text(json.dumps({'url':'https://fixture.invalid','trust':str(root/'trust.pem'),'state':str(root/'state')}))
        self.flow=Mock(); self.flow.status.return_value={'state':'unpaired'}
        self.flow.target={'origin':'https://fixture.invalid','trust_sha256':'a'*64}
        self.vault=Mock(); self.code='PRIVATE_SYNTHETIC_CODE'
    def tearDown(self): self.temp.cleanup()
    def run_action(self, action, confirmation='PAIR', tty=True):
        output=io.StringIO()
        with contextlib.redirect_stdout(output), patch.object(m2_setup,'Vault',return_value=self.vault), \
            patch.object(m2_setup,'Enrollment',return_value=self.flow), \
            patch.object(m2_setup.sys.stdin,'isatty',return_value=tty), \
            patch.object(m2_setup.sys.stderr,'isatty',return_value=tty), \
            patch('builtins.input',return_value=confirmation), \
            patch.object(m2_setup.getpass,'getpass',return_value=self.code) as hidden:
            result=m2_setup.main(['--config',str(self.config),action])
        self.assertNotIn(self.code,output.getvalue())
        self.vault.close.assert_called_once()
        return result,output.getvalue(),hidden
    def test_pair_hidden_once_no_automatic_verify(self):
        result,output,hidden=self.run_action('pair')
        self.assertEqual(result,0); hidden.assert_called_once()
        self.flow.pair.assert_called_once_with(self.code); self.flow.verify.assert_not_called()
        self.assertIn('SHA-256',output)
    def test_pair_cancelled_before_secret_prompt(self):
        result,_,hidden=self.run_action('pair','no')
        self.assertEqual(result,1); hidden.assert_not_called(); self.flow.pair.assert_not_called()
    def test_noninteractive_pair_refused_without_secret_read(self):
        result,output,hidden=self.run_action('pair',tty=False)
        self.assertEqual(result,1); hidden.assert_not_called(); self.flow.pair.assert_not_called()
        self.assertIn('private interactive terminal',output)
    def test_existing_pair_not_overwritten(self):
        self.flow.status.return_value={'state':'paired','device':'a'*24}
        result,_,hidden=self.run_action('pair')
        self.assertEqual(result,1); hidden.assert_not_called(); self.flow.pair.assert_not_called()
    def test_unknown_outcome_guides_recovery_without_retry(self):
        self.flow.pair.side_effect=EnrollmentError('PAIRING_OUTCOME_UNKNOWN')
        result,output,_=self.run_action('pair')
        self.assertEqual(result,1); self.flow.pair.assert_called_once()
        self.assertIn('revoke an identified orphan',output); self.flow.forget.assert_not_called()
    def test_unexpected_error_does_not_print_private_exception(self):
        self.flow.pair.side_effect=RuntimeError(self.code)
        result,_,_=self.run_action('pair'); self.assertEqual(result,1)
    def test_forget_is_explicit_and_local(self):
        result,output,_=self.run_action('forget','FORGET')
        self.assertEqual(result,0); self.flow.forget.assert_called_once()
        self.flow.pair.assert_not_called(); self.flow.verify.assert_not_called()
        self.assertIn('does not revoke',output)
    def test_forget_cancel_preserves_record(self):
        result,_,_=self.run_action('forget','no')
        self.assertEqual(result,1); self.flow.forget.assert_not_called()
    def test_noninteractive_forget_refused(self):
        result,_,_=self.run_action('forget','FORGET',False)
        self.assertEqual(result,1); self.flow.forget.assert_not_called()
    def test_status_is_local_without_trust_file(self):
        result,output,_=self.run_action('status',tty=False)
        self.assertEqual(result,0); self.assertIn('Not paired',output)
        self.flow.pair.assert_not_called(); self.flow.verify.assert_not_called()
    def test_verify_only_reads(self):
        self.flow.verify.return_value={'state':'connected','fixture':True}
        result,output,_=self.run_action('verify',tty=False)
        self.assertEqual(result,0); self.assertIn('silent fixture',output)
        self.flow.verify.assert_called_once(); self.flow.pair.assert_not_called()
    def test_unknown_arguments_are_not_echoed(self):
        output=io.StringIO()
        with contextlib.redirect_stderr(output), self.assertRaises(SystemExit):
            m2_setup.main(['--config',str(self.config),'pair','--code',self.code])
        self.assertNotIn(self.code,output.getvalue())
    def test_configuration_rejects_inline_secrets_and_relative_paths(self):
        for data in ({'url':'https://fixture.invalid','trust':'relative','state':'relative'},
                     {'url':'https://fixture.invalid','trust':str(self.config),'state':str(self.config.parent),'credential':self.code}):
            self.config.write_text(json.dumps(data))
            with self.assertRaises(ValueError): m2_setup.configuration(self.config)
    def test_echo_fallback_warning_aborts_before_pairing(self):
        import warnings
        with patch.object(m2_setup.sys.stdin,'isatty',return_value=True), \
             patch.object(m2_setup.sys.stderr,'isatty',return_value=True), \
             patch.object(m2_setup.getpass,'getpass',side_effect=lambda *_:warnings.warn('no echo control',m2_setup.getpass.GetPassWarning)):
            with self.assertRaises(m2_setup.getpass.GetPassWarning): m2_setup.private_code()
