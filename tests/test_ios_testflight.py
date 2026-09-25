"""Offline distribution gates; no signing credential or Apple request is used."""
from datetime import datetime, timedelta
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from ios_testflight import build_number, export_options, profile_identity, value


class TestFlightGates(unittest.TestCase):
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
