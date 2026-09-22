"""Portable package boundaries and launcher recovery; no real bridge commands."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock,patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import m2_launcher as launch
from m2_provisioning import EnrollmentError

class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)/'app'; self.root.mkdir()
        self.file=self.root/'ndx_fixture.exe'; self.file.write_bytes(b'synthetic')
        self.manifest={'format':1,'files':{'ndx_fixture.exe':hashlib.sha256(b'synthetic').hexdigest()}}
        self.save()
    def tearDown(self): self.temp.cleanup()
    def save(self): (self.root/'manifest.json').write_text(json.dumps(self.manifest))
    def test_manifest_rejects_changed_file(self):
        launch.verify_package(self.root); self.file.write_bytes(b'changed')
        with self.assertRaises(ValueError): launch.verify_package(self.root)
    def test_manifest_rejects_path_escape(self):
        outside=self.root.parent/'private'; outside.write_bytes(b'synthetic')
        self.manifest['files']={'../private':hashlib.sha256(b'synthetic').hexdigest()}; self.save()
        with self.assertRaises(ValueError): launch.verify_package(self.root)
    def test_external_state_boundary(self):
        with patch.object(launch,'ROOT',self.root):
            with self.assertRaises(ValueError): launch.external(self.root/'state')
            launch.external(self.root.parent/'state')
    def run_launch(self,error=None,check=False,paired=True):
        config={'url':'https://fixture.invalid','trust':str(self.root.parent/'trust'),'state':str(self.root.parent/'state')}
        flow=Mock(); flow.status.return_value={'state':'paired' if paired else 'unpaired'}
        flow.verify.side_effect=error
        vault=Mock(); child=Mock(returncode=0); output=io.StringIO()
        args=['--config',str(self.root.parent/'config')]+(['--check'] if check else [])
        with patch.object(launch,'ROOT',self.root), patch.object(launch,'configuration',return_value=config), \
             patch.object(launch,'Vault',return_value=vault),patch.object(launch,'Enrollment',return_value=flow), \
             patch.object(launch.subprocess,'run',return_value=child) as run,contextlib.redirect_stdout(output):
            result=launch.main(args)
        return result,run,flow,vault,output.getvalue()
    def test_offline_launch_still_opens_recovering_ui(self):
        result,run,flow,vault,output=self.run_launch(EnrollmentError('BRIDGE_UNAVAILABLE'))
        self.assertEqual(result,0); run.assert_called_once(); flow.verify.assert_called_once()
        vault.close.assert_called_once(); self.assertIn('reconnect',output)
    def test_offline_check_does_not_launch(self):
        result,run,_,_,_=self.run_launch(EnrollmentError('BRIDGE_UNAVAILABLE'),True)
        self.assertEqual(result,1); run.assert_not_called()
    def test_revoked_launch_requires_explicit_setup(self):
        result,run,_,_,_=self.run_launch(EnrollmentError('AUTHORIZATION_REQUIRED'))
        self.assertEqual(result,1); run.assert_not_called()
    def test_unpaired_does_not_connect_or_launch(self):
        result,run,flow,_,_=self.run_launch(paired=False)
        self.assertEqual(result,1); run.assert_not_called(); flow.verify.assert_not_called()
    def test_ready_check_never_starts_native_process(self):
        result,run,_,_,_=self.run_launch(check=True)
        self.assertEqual(result,0); run.assert_not_called()
