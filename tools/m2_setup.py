"""Local host enrollment console. No secret arguments, hardware or playback actions."""
import argparse
import getpass
import json
from pathlib import Path
import sys
import warnings
from m2_provisioning import Enrollment, EnrollmentError
from m2_security import Vault

STATES={
    'unpaired':'Not paired. Verify bridge trust, then use pair.',
    'paired':'Pairing saved. Use verify to check the connection.',
    'legacy':'Legacy pairing. Plan explicit revocation and re-enrollment before deployment.',
    'outcome_unknown':'Pairing outcome unknown. Inspect bridge devices; revoke an identified orphan before forgetting locally.',
    'authorization_required':'Authorization required. Resolve bridge revocation, then explicitly forget and pair with a new code.',
    'storage_uncertain':'Storage uncertain. Close setup and inspect/reopen protected storage before continuing.',
    'recovery_required':'Unsupported or damaged enrollment. Inspect local storage; do not overwrite it automatically.'}
ERRORS={
    'PAIRING_OUTCOME_UNKNOWN':STATES['outcome_unknown'],
    'STORAGE_UNCERTAIN':STATES['storage_uncertain'],
    'LOCAL_RECOVERY_REQUIRED':'Existing enrollment needs recovery. Use status; no new pairing was sent.',
    'INVALID_SETUP_CODE':'Invalid setup code. Request a fresh code at the bridge console.',
    'TRUST_CHANGED':'Trust changed during setup. Stop and verify the intended bridge again.',
    'ENROLLMENT_REQUIRED':'Enrollment or bridge binding needs recovery. Use status and inspect the intended bridge trust.',
    'AUTHORIZATION_REQUIRED':STATES['authorization_required'],
    'BRIDGE_UNAVAILABLE':'Bridge unavailable. Saved pairing is retained; try verify later.',
    'TRUST_VERIFICATION_FAILED':'New trust could not verify the bridge. The saved binding was not changed.',
    'INVALID_ORIGIN':'A verified HTTPS bridge origin is required.'}

class Parser(argparse.ArgumentParser):
    def error(self, message):
        # Do not echo unexpected arguments, which could contain a pasted secret.
        self.print_usage(sys.stderr)
        self.exit(2,'Invalid setup arguments. Use --help; setup codes are entered privately, never as arguments.\n')


def configuration(path):
    with Path(path).open('rb') as stream: raw=stream.read(16385)
    if len(raw)>16384: raise ValueError()
    data=json.loads(raw)
    if (not isinstance(data,dict) or set(data)-{'url','trust','state','allow_live'} or
        any(not isinstance(data.get(k),str) or not data[k] for k in ('url','trust','state')) or
        not Path(data['trust']).is_absolute() or not Path(data['state']).is_absolute() or
        ('allow_live' in data and type(data['allow_live']) is not bool)):
        raise ValueError()
    return data


def private_code():
    # getpass may otherwise fall back to echoing stdin. Fail before that fallback.
    if not sys.stdin.isatty() or not sys.stderr.isatty(): raise EnrollmentError('PRIVATE_TERMINAL_REQUIRED')
    with warnings.catch_warnings():
        warnings.simplefilter('error',getpass.GetPassWarning)
        return getpass.getpass('Single-use setup code (hidden): ')


def show_status(flow):
    result=flow.status()
    print(STATES.get(result['state'],STATES['recovery_required']))
    if result.get('device'): print('Controller ID:',result['device'])
    if result.get('trust_sha256'): print('Saved trust SHA-256:',result['trust_sha256'])


def main(argv=None):
    parser=Parser(description='Host setup: local status, private pairing, read-only verification, explicit trust update and local forgetting.')
    parser.add_argument('--config',required=True,help='Public desktop JSON with url and absolute trust/state paths')
    parser.add_argument('action',choices=('status','pair','verify','forget','trust-update'))
    args=parser.parse_args(argv)
    vault=None
    try:
        config=configuration(args.config)
        vault=Vault(config['state'])
        if args.action in ('status','forget'):
            flow=Enrollment(vault)  # Local recovery works even when trust is missing.
        else: flow=Enrollment(vault,config['url'],config['trust'])
        if args.action=='status': show_status(flow)
        elif args.action=='pair':
            if flow.status()['state']!='unpaired':
                show_status(flow); return 1
            if not sys.stdin.isatty() or not sys.stderr.isatty():
                raise EnrollmentError('PRIVATE_TERMINAL_REQUIRED')
            print('Bridge:',flow.target['origin'])
            print('Trust file SHA-256:',flow.target['trust_sha256'])
            print('Compare these with the bridge administrator through a trusted channel.')
            if input('Type PAIR after verifying this bridge and trust: ')!='PAIR':
                print('Cancelled. No pairing request sent.'); return 1
            code=private_code()
            try: flow.pair(code)
            finally: code=None
            show_status(flow)
            print('Next: run verify. No verification or playback command was sent automatically.')
        elif args.action=='trust-update':
            if flow.status()['state']!='paired':
                show_status(flow); return 1
            record=vault.data.get('controller',{})
            if record.get('origin')!=flow.target['origin']:
                raise EnrollmentError('ENROLLMENT_REQUIRED')
            if not sys.stdin.isatty(): raise EnrollmentError('INTERACTIVE_TERMINAL_REQUIRED')
            print('Bridge:',flow.target['origin'])
            print('Saved trust SHA-256:',record.get('trust_sha256','unavailable'))
            print('Proposed trust SHA-256:',flow.target['trust_sha256'])
            print('Verify the new trust with the bridge administrator through an independent trusted channel.')
            print('This permits the existing credential to authenticate with the approved new trust.')
            if input('Type UPDATE TRUST to verify and save this trust change: ')!='UPDATE TRUST':
                print('Cancelled. Saved trust retained.'); return 1
            flow.update_trust()
            print('Trust binding saved after a read-only snapshot. Pairing retained; use this configuration with the controller.')
        elif args.action=='verify':
            result=flow.verify()
            print('Connected to the silent fixture.' if result['fixture'] else 'Connected to the bridge.')
            print('Read-only snapshot verified. No playback or volume command sent.')
        else:
            show_status(flow)
            print('Forgetting removes this local pairing only. It does not revoke access at the bridge.')
            print('First revoke the known controller ID there; resolve any unknown pairing outcome locally.')
            if not sys.stdin.isatty(): raise EnrollmentError('INTERACTIVE_TERMINAL_REQUIRED')
            if input('Type FORGET to remove only the local enrollment: ')!='FORGET':
                print('Cancelled. Local enrollment retained.'); return 1
            flow.forget(); print('Local enrollment removed. No bridge authorization was changed.')
        return 0
    except (KeyboardInterrupt,EOFError):
        print('Interrupted. Run status before retrying; an in-flight pairing may have an unknown outcome.'); return 1
    except EnrollmentError as exc:
        messages={**ERRORS,'PRIVATE_TERMINAL_REQUIRED':'Pairing requires a private interactive terminal with hidden input.',
            'INTERACTIVE_TERMINAL_REQUIRED':'This recovery action requires interactive confirmation.'}
        print(messages.get(str(exc),'Setup unavailable. Inspect local configuration and protected storage.')); return 1
    except Exception:
        print('Setup unavailable. Check the public configuration, verified trust and protected storage; close other clients first.'); return 1
    finally:
        if vault is not None: vault.close()

if __name__=='__main__': sys.exit(main())
