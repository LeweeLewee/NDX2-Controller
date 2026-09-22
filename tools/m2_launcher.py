"""Portable desktop entry point; application files and user state stay separate."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from m2_setup import configuration, Parser
from m2_provisioning import Enrollment, EnrollmentError
from m2_security import Vault

ROOT=Path(__file__).resolve().parents[1]


def verify_package(root):
    manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('format')!=1: raise ValueError()
    for name,digest in manifest['files'].items():
        path=(root/name).resolve()
        if not path.is_relative_to(root.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            raise ValueError()
    return manifest


def external(path):
    if Path(path).resolve().is_relative_to(ROOT): raise ValueError('State must be outside installation')


def main(argv=None):
    parser=Parser(description='NDX2 desktop launcher; no automatic playback or setup.')
    parser.add_argument('--config'); parser.add_argument('--fixture',action='store_true')
    parser.add_argument('--check',action='store_true'); parser.add_argument('--preferences')
    args=parser.parse_args(argv)
    try:
        verify_package(ROOT)
        command=[str(ROOT/'ndx_fixture.exe')]
        if args.preferences:
            external(args.preferences); command+=['--preferences',str(Path(args.preferences).resolve())]
        if args.fixture and args.config: raise ValueError()
        if args.config:
            external(args.config); config=configuration(args.config)
            external(config['state']); external(config['trust'])
            vault=Vault(config['state'])
            try:
                flow=Enrollment(vault,config['url'],config['trust'])
                if flow.status()['state']!='paired':
                    print('Setup required. Close the controller and use Setup.cmd with this configuration.'); return 1
                try: flow.verify()
                except EnrollmentError as exc:
                    if str(exc)!='BRIDGE_UNAVAILABLE': raise
                    print('Bridge unavailable. Pairing is retained; the controller will reconnect without replaying commands.')
                    if args.check: return 1
            finally: vault.close()
            command+=['--bridge',str(ROOT/'runtime/python.exe'),str(Path(args.config).resolve())]
        elif not args.fixture:
            print('Package verified. Choose --fixture for the silent demo, or --config with an external paired configuration.')
            return 0 if args.check else 1
        if args.check:
            print('Package and selected setup checks passed.'); return 0
        # The working directory locates the bundled helper, independent of launch location.
        return subprocess.run(command,cwd=ROOT).returncode
    except EnrollmentError:
        print('Pairing or trust needs attention. Use Setup.cmd status/verify; no setup was changed.'); return 1
    except Exception:
        print('Cannot launch. Check the package files and external configuration; close any other controller first.'); return 1

if __name__=='__main__': sys.exit(main())
