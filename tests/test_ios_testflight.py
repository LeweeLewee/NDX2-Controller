"""Offline distribution gates; no signing credential or Apple request is used."""
from datetime import datetime, timedelta
import os
import plistlib
import tempfile
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from ios_testflight import build_mode, inspect_archive, build_number, export_options, profile_identity, value


class TestFlightGates(unittest.TestCase):
    def test_build_mode_is_explicit_and_rejects_unknown_values(self):
        self.assertEqual(build_mode('preview'), 'STILL_WATER_PREVIEW')
        self.assertEqual(build_mode('live'), 'STILL_WATER_LIVE_BETA')
        for mode in ['', None, 'production', 'live;command']:
            with self.assertRaises(ValueError): build_mode(mode)

    def test_archive_must_match_selected_mode_and_remain_internal_identity(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            app = root / 'Products/Applications/StillWater.app'
            app.mkdir(parents=True)
            (app / 'Assets.car').write_bytes(b'synthetic')
            (app / 'StillWater').write_bytes(b'synthetic executable')
            privacy = Path(__file__).resolve().parents[1] / 'ios/StillWater/Resources/PrivacyInfo.xcprivacy'
            (app / 'PrivacyInfo.xcprivacy').write_bytes(privacy.read_bytes())
            info = {'CFBundleIdentifier':'com.example.test', 'CFBundleShortVersionString':'0.1.0',
                    'CFBundleVersion':'9.1.0', 'CFBundleSupportedPlatforms':['iPhoneOS'],
                    'DTXcode':'2630', 'DTSDKName':'iphoneos26.2', 'MinimumOSVersion':'17.0',
                    'CFBundleIcons':{'CFBundlePrimaryIcon':{'CFBundleIconName':'AppIcon'}}}
            with patch('ios_testflight.OUTPUT', root):
                for mode, other in [('preview','live'), ('live','preview')]:
                    info['StillWaterBuildMode'] = build_mode(mode)
                    (app / 'Info.plist').write_bytes(plistlib.dumps(info))
                    self.assertEqual(inspect_archive(root,'com.example.test',mode), app)
                    with self.assertRaises(ValueError): inspect_archive(root,'com.example.test',other)
                    with self.assertRaises(ValueError): inspect_archive(root,'com.example.other',mode)

    def profile(self):
        return {'UUID': '11111111-2222-3333-4444-555555555555',
                'TeamIdentifier': ['ABCDEFGHIJ'], 'ExpirationDate': datetime(2030, 1, 1),
                'DeveloperCertificates': [b'synthetic'], 'Entitlements': {
                    'application-identifier': 'ABCDEFGHIJ.com.example.test',
                    'com.apple.developer.team-identifier': 'ABCDEFGHIJ', 'get-task-allow': False}}

    def test_distribution_profile_binds_exact_app_team_and_expiry(self):
        p = self.profile()
        self.assertEqual(profile_identity(p, 'ABCDEFGHIJ', 'com.example.test'), p['UUID'])
        for team, bundle in [('OTHERTEAM1', 'com.example.test'), ('ABCDEFGHIJ', 'com.example.other')]:
            with self.assertRaises(ValueError): profile_identity(p, team, bundle)
        for delta in [timedelta(0), timedelta(seconds=1)]:
            with self.assertRaises(ValueError):
                profile_identity(p, 'ABCDEFGHIJ', 'com.example.test', p['ExpirationDate'] + delta)

    def test_development_ad_hoc_enterprise_and_wildcard_profiles_are_refused(self):
        variants = [{'ProvisionedDevices': ['synthetic']}, {'ProvisionsAllDevices': True}, {'DeveloperCertificates': []}]
        for field in variants:
            p = self.profile(); p.update(field)
            with self.assertRaises(ValueError): profile_identity(p, 'ABCDEFGHIJ', 'com.example.test')
        for field in [{'get-task-allow': True}, {'application-identifier': 'ABCDEFGHIJ.*'}]:
            p = self.profile(); p['Entitlements'].update(field)
            with self.assertRaises(ValueError): profile_identity(p, 'ABCDEFGHIJ', 'com.example.test')

    def test_export_is_internal_only_and_uses_supplied_profile(self):
        options = export_options('ABCDEFGHIJ', 'com.example.test', 'profile')
        self.assertEqual(options['destination'], 'upload')
        self.assertEqual(options['method'], 'app-store-connect')
        self.assertIs(options['testFlightInternalTestingOnly'], True)
        self.assertIs(options['manageAppVersionAndBuildNumber'], False)
        self.assertEqual(options['provisioningProfiles'], {'com.example.test': 'profile'})

    def test_signing_password_preserves_significant_whitespace(self):
        with patch.dict(os.environ, {'APPLE_CERTIFICATE_PASSWORD': ' synthetic password '}):
            self.assertEqual(value('APPLE_CERTIFICATE_PASSWORD', strip=False), ' synthetic password ')

    def test_build_numbers_distinguish_reruns_and_refuse_invalid_counters(self):
        with patch.dict(os.environ, {'GITHUB_RUN_NUMBER': '42', 'GITHUB_RUN_ATTEMPT': '2'}):
            self.assertEqual(build_number(), '42.2.0')
        for number in ['0', '10000', '4;command']:
            with patch.dict(os.environ, {'GITHUB_RUN_NUMBER': number}):
                with self.assertRaises(ValueError): build_number()


if __name__ == '__main__':
    unittest.main()
