"""Packaged setup keeps private state outside the replaceable installation."""
import sys
from m2_launcher import ROOT, external, verify_package
from m2_setup import Parser, configuration, main as setup

def main(argv=None):
    argv=sys.argv[1:] if argv is None else argv
    if argv==['--help']: return setup(argv)
    parser=Parser(add_help=False); parser.add_argument('--config',required=True)
    args,_=parser.parse_known_args(argv)
    try:
        verify_package(ROOT); external(args.config); config=configuration(args.config)
        external(config['state']); external(config['trust'])
    except Exception:
        print('Use an intact package and keep configuration, trust and pairing outside the installation folder.'); return 1
    return setup(argv)

if __name__=='__main__': sys.exit(main())
