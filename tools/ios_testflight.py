"""Build/check the silent preview; upload only with an explicit signed action.

Signing inputs come from a GitHub environment. They are never written to source
or uploaded as artifacts. Apple account/provisioning setup is performed separately.
"""
import argparse
import base64
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import secrets
import subprocess
import tempfile

OUTPUT = Path('local/ios-release')
ARCHIVE = OUTPUT / 'StillWater.xcarchive'
MODE = 'STILL_WATER_PREVIEW'


def run(*args, private=False):
    result = subprocess.run(args, capture_output=private, text=True)
    if result.returncode:
        # Private subprocess arguments/output can include passwords or identities.
        raise RuntimeError(f'{Path(args[0]).name} failed (exit {result.returncode})')


def value(name, pattern=None, *, strip=True):
    text = os.environ.get(name, '')
    if strip:
        text = text.strip()
    if not text or (pattern and not re.fullmatch(pattern, text)):
        raise ValueError(f'Missing or invalid {name}')
    return text


def write_secret(path, raw):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)


def profile_identity(profile, team, bundle, now=None):
    now = now or datetime.now()
    entitlements = profile.get('Entitlements', {})
    if (profile.get('TeamIdentifier') != [team]
            or entitlements.get('com.apple.developer.team-identifier') != team
            or entitlements.get('application-identifier') != team + '.' + bundle
            or entitlements.get('get-task-allow') is not False
            or profile.get('ProvisionedDevices') is not None
            or profile.get('ProvisionsAllDevices', False)
            or profile.get('ExpirationDate', datetime.min) <= now
            or not profile.get('DeveloperCertificates')):
        raise ValueError('Profile must be an unexpired App Store profile for the selected team and bundle')
    identifier = profile.get('UUID', '')
    if not re.fullmatch(r'[A-Fa-f0-9-]{36}', identifier):
        raise ValueError('Invalid profile UUID')
    return identifier


def build_number():
    # A rerun gets a distinct version as well; Apple allows up to three components.
    number = os.environ.get('GITHUB_RUN_NUMBER', '1')
    attempt = os.environ.get('GITHUB_RUN_ATTEMPT', '1')
    if not number.isdigit() or not attempt.isdigit() or not 1 <= int(number) <= 9999 or not 1 <= int(attempt) <= 99:
        raise ValueError('Build counter exhausted or invalid; update the version policy explicitly')
    return f'{int(number)}.{int(attempt)}.0'


def archive(bundle, signing=()):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if ARCHIVE.exists():
        raise ValueError('Archive already exists; use a fresh checkout/job rather than overwrite evidence')
    run('python3', 'tools/generate_ios_project.py', '--check')
    run('xcodebuild', 'archive', '-project', 'ios/StillWater.xcodeproj', '-scheme', 'StillWater',
        '-configuration', 'Release', '-destination', 'generic/platform=iOS',
        '-archivePath', str(ARCHIVE), '-derivedDataPath', str(OUTPUT / 'DerivedData'),
        f'PRODUCT_BUNDLE_IDENTIFIER={bundle}', f'CURRENT_PROJECT_VERSION={build_number()}',
        f'STILL_WATER_MODE={MODE}', *signing)
    return inspect_archive(ARCHIVE, bundle)


def inspect_archive(path, bundle):
    app = path / 'Products/Applications/StillWater.app'
    info = plistlib.loads((app / 'Info.plist').read_bytes())
    if (info.get('CFBundleIdentifier') != bundle or info.get('StillWaterBuildMode') != MODE
            or info.get('CFBundleSupportedPlatforms') != ['iPhoneOS']
            or int(info.get('DTXcode', '0')) < 2600
            or not info.get('DTSDKName', '').startswith('iphoneos26')
            or not (app / 'Assets.car').is_file()
            or info.get('CFBundleIcons', {}).get('CFBundlePrimaryIcon', {}).get('CFBundleIconName') != 'AppIcon'):
        raise ValueError('Archive is not the expected iOS 26 SDK silent-preview device build with an app icon')
    privacy = plistlib.loads((app / 'PrivacyInfo.xcprivacy').read_bytes())
    reasons = {x['NSPrivacyAccessedAPIType']: x['NSPrivacyAccessedAPITypeReasons']
               for x in privacy['NSPrivacyAccessedAPITypes']}
    if (privacy.get('NSPrivacyTracking') is not False or privacy.get('NSPrivacyCollectedDataTypes') != []
            or reasons.get('NSPrivacyAccessedAPICategoryUserDefaults') != ['CA92.1']
            or reasons.get('NSPrivacyAccessedAPICategorySystemBootTime') != ['35F9.1']):
        raise ValueError('Preview privacy declarations missing or changed')
    evidence = {key: info[key] for key in ['CFBundleIdentifier', 'CFBundleShortVersionString', 'CFBundleVersion',
                                         'StillWaterBuildMode', 'DTXcode', 'DTSDKName', 'MinimumOSVersion']}
    evidence['source_commit'] = os.environ.get('GITHUB_SHA')
    evidence['signed'] = (app / '_CodeSignature/CodeResources').exists()
    evidence['uploaded'] = False
    evidence['binary_sha256'] = hashlib.sha256((app / 'StillWater').read_bytes()).hexdigest()
    (OUTPUT / 'archive-check.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
    print('Verified preview archive, SDK, icon and privacy manifest; upload has not occurred.')
    return app


def export_options(team, bundle, profile):
    return {'method': 'app-store-connect', 'destination': 'upload', 'teamID': team,
            'signingStyle': 'manual', 'signingCertificate': 'Apple Distribution',
            'provisioningProfiles': {bundle: profile}, 'manageAppVersionAndBuildNumber': False,
            'uploadSymbols': True, 'testFlightInternalTestingOnly': True}


def upload():
    team = value('APPLE_TEAM_ID', r'[A-Z0-9]{10}')
    bundle = value('APPLE_BUNDLE_ID', r'[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+')
    key_id = value('ASC_KEY_ID', r'[A-Z0-9]{10}')
    issuer = value('ASC_ISSUER_ID', r'[a-fA-F0-9-]{36}')
    p12 = base64.b64decode(value('APPLE_CERTIFICATE_P12_BASE64'), validate=True)
    profile_raw = base64.b64decode(value('APPLE_PROFILE_BASE64'), validate=True)
    password = value('APPLE_CERTIFICATE_PASSWORD', strip=False)
    key_raw = value('ASC_PRIVATE_KEY').encode()
    if b'-----BEGIN PRIVATE KEY-----' not in key_raw or len(key_raw) > 16384:
        raise ValueError('Invalid ASC_PRIVATE_KEY')
    temp_root = Path(value('RUNNER_TEMP')).resolve()
    profile_dest = None
    with tempfile.TemporaryDirectory(prefix='still-water-signing-', dir=temp_root) as folder:
        folder = Path(folder)
        keychain = folder / 'signing.keychain-db'
        keychain_password = secrets.token_urlsafe(32)
        old_keychains = subprocess.check_output(['security', 'list-keychains', '-d', 'user'], text=True)
        keychains = re.findall(r'"([^"\n]+)"', old_keychains)
        try:
            write_secret(folder / 'distribution.p12', p12)
            write_secret(folder / 'profile.mobileprovision', profile_raw)
            write_secret(folder / f'AuthKey_{key_id}.p8', key_raw)
            decoded = subprocess.check_output(['security', 'cms', '-D', '-i', str(folder / 'profile.mobileprovision')], stderr=subprocess.DEVNULL)
            profile = plistlib.loads(decoded)
            identifier = profile_identity(profile, team, bundle)
            profile_dir = Path.home() / 'Library/Developer/Xcode/UserData/Provisioning Profiles'
            profile_dir.mkdir(parents=True, exist_ok=True)
            candidate_path = profile_dir / (identifier + '.mobileprovision')
            # Never overwrite a profile on a reused host; this workflow uses hosted ephemeral runners.
            write_secret(candidate_path, profile_raw)
            profile_dest = candidate_path
            run('security', 'create-keychain', '-p', keychain_password, str(keychain), private=True)
            run('security', 'set-keychain-settings', '-lut', '3600', str(keychain), private=True)
            run('security', 'unlock-keychain', '-p', keychain_password, str(keychain), private=True)
            run('security', 'import', str(folder / 'distribution.p12'), '-k', str(keychain), '-P', password,
                '-T', '/usr/bin/codesign', '-T', '/usr/bin/security', private=True)
            run('security', 'set-key-partition-list', '-S', 'apple-tool:,apple:,codesign:', '-s', '-k', keychain_password, str(keychain), private=True)
            run('security', 'list-keychains', '-d', 'user', '-s', str(keychain), *keychains, private=True)
            app = archive(bundle, [f'DEVELOPMENT_TEAM={team}', 'CODE_SIGN_STYLE=Manual',
                                  'CODE_SIGN_IDENTITY=Apple Distribution', f'PROVISIONING_PROFILE_SPECIFIER={identifier}'])
            run('codesign', '--verify', '--deep', '--strict', str(app))
            options = folder / 'ExportOptions.plist'
            options.write_bytes(plistlib.dumps(export_options(team, bundle, identifier)))
            run('xcodebuild', '-exportArchive', '-archivePath', str(ARCHIVE), '-exportPath', str(OUTPUT / 'export'),
                '-exportOptionsPlist', str(options), '-allowProvisioningUpdates', '-authenticationKeyPath', str(folder / f'AuthKey_{key_id}.p8'),
                '-authenticationKeyID', key_id, '-authenticationKeyIssuerID', issuer)
            print('Upload command completed; confirm Apple processing and tester assignment in App Store Connect.')
        finally:
            subprocess.run(['security', 'list-keychains', '-d', 'user', '-s', *keychains], capture_output=True)
            if keychain.exists():
                subprocess.run(['security', 'delete-keychain', str(keychain)], capture_output=True)
            if profile_dest and profile_dest.exists():
                profile_dest.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('archive-check', 'upload'))
    args = parser.parse_args()
    try:
        if args.action == 'upload':
            upload()
        else:
            archive('com.ndx2.controller', ['CODE_SIGNING_ALLOWED=NO'])
    except (ValueError, RuntimeError) as error:
        raise SystemExit(str(error)) from None
