"""Bounded macOS simulator setup and Windows-readable XCTest evidence export.

This does not sign, archive, distribute, pair, or configure a live bridge.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess

OUTPUT = Path('local/ios-ci')


def command(*args):
    return subprocess.check_output(args, text=True)


def prepare():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    runtimes = json.loads(command('xcrun', 'simctl', 'list', 'runtimes', '-j'))['runtimes']
    candidates = [r for r in runtimes if r.get('isAvailable') and r['name'].startswith('iOS 18.')]
    if not candidates:
        raise SystemExit('No compatible iOS 18 runtime installed; inspect the pinned runner image.')
    runtime = max(candidates, key=lambda r: tuple(map(int, r['version'].split('.'))))
    kind = 'com.apple.CoreSimulator.SimDeviceType.iPhone-11'
    device = command('xcrun', 'simctl', 'create', 'Still Water iPhone 11', kind, runtime['identifier']).strip()
    metadata = {'xcode': command('xcodebuild', '-version').strip(), 'runtime': runtime['identifier'],
                'device_type': kind, 'device': device, 'fixture_only': True, 'signing': False}
    (OUTPUT / 'environment.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(metadata, indent=2))
    command('xcrun', 'simctl', 'boot', device)
    command('xcrun', 'simctl', 'bootstatus', device, '-b')
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as stream:
            stream.write(f'device={device}\n')


def export():
    result = OUTPUT / 'StillWater.xcresult'
    if not result.exists():
        print('No XCTest result bundle; inspect xcodebuild.log for a build/setup failure.')
        return
    summary = command('xcrun', 'xcresulttool', 'get', 'test-results', 'summary', '--path', str(result))
    (OUTPUT / 'test-summary.json').write_text(summary, encoding='utf-8')
    screenshots = OUTPUT / 'screenshots'
    screenshots.mkdir(exist_ok=True)
    subprocess.run(['xcrun', 'xcresulttool', 'export', 'attachments', '--path', str(result),
                    '--output-path', str(screenshots)], check=True)
    print('Exported native XCTest attachments and JSON summary; no .ipa was produced.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'export'))
    args = parser.parse_args()
    (prepare if args.action == 'prepare' else export)()
