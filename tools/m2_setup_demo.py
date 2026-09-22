"""Exercise host setup against silent TLS; private input is synthetic/injected."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
from unittest.mock import patch
from m2_bridge import Contract, FixtureService, server
from m2_certificates import create
from m2_security import Pairing, Vault
import m2_setup

ROOT=Path(__file__).resolve().parents[1]

def main():
    with tempfile.TemporaryDirectory() as temporary:
        root=Path(temporary); create(root/'tls')
        vault=Vault(root/'bridge'); pairing=Pairing(vault); service=FixtureService()
        bridge=server(Contract(service,vault),pairing,root/'tls/trust.pem',root/'tls/key.pem',port=0)
        worker=threading.Thread(target=bridge.serve_forever,daemon=True); worker.start()
        config=root/'desktop.json'; trust=root/'tls/trust.pem'
        config.write_text(json.dumps({'url':'https://127.0.0.1:'+str(bridge.server_port),
                                     'trust':str(trust),'state':str(root/'controller')}))
        captured=[]; secrets=[]
        def interactive(action, confirmation, code=''):
            output=io.StringIO()
            with contextlib.redirect_stdout(output), patch.object(sys.stdin,'isatty',return_value=True), \
                 patch.object(sys.stderr,'isatty',return_value=True), patch('builtins.input',return_value=confirmation), \
                 patch.object(m2_setup.getpass,'getpass',return_value=code):
                result=m2_setup.main(['--config',str(config),action])
            captured.append(output.getvalue()); return result
        def process(action, expected):
            result=subprocess.run([sys.executable,str(ROOT/'tools/m2_setup.py'),'--config',str(config),action],
                input='',capture_output=True,text=True,cwd=ROOT,timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
            captured.extend((result.stdout,result.stderr)); assert result.returncode==expected
            return result.stdout
        try:
            assert 'Not paired' in process('status',0)
            process('pair',1); assert pairing.devices()==[]  # Piped input cannot provision.
            code=pairing.issue(); secrets.append(code)
            assert interactive('pair','PAIR',code)==0
            controller=Vault(root/'controller')
            try:
                first=controller.data['controller']['device']; secrets.append(controller.data['controller']['credential'])
            finally: controller.close()
            assert pairing.devices()==[first]
            assert 'Pairing saved' in process('status',0)
            assert 'silent fixture' in process('verify',0)
            pairing.revoke(first)
            assert 'Authorization required' in process('verify',1)
            assert 'Authorization required' in process('status',0)
            # Local recovery remains possible with missing trust; no network needed.
            saved_trust=root/'tls/saved-trust.pem'; trust.rename(saved_trust)
            assert 'Authorization required' in process('status',0)
            assert interactive('forget','no')==1
            assert interactive('forget','FORGET')==0
            saved_trust.rename(trust)
            code=pairing.issue(); secrets.append(code)
            assert interactive('pair','PAIR',code)==0
            assert 'silent fixture' in process('verify',0)
            assert len(pairing.devices())==1 and pairing.devices()[0]!=first
            controller=Vault(root/'controller')
            try: secrets.append(controller.data['controller']['credential'])
            finally: controller.close()
            assert service.naim.calls==[]
            assert all(secret not in ''.join(captured) for secret in secrets)
            print('PASS setup console: pair, fresh-process status/verify, revoke, missing-trust recovery and explicit re-pair')
            print('PASS noninteractive pairing refused, secrets absent from output, zero playback or volume calls')
            print('Hidden entry supplied by a test double; physical terminal echo behavior remains a manual host check.')
        finally:
            bridge.shutdown(); bridge.server_close(); worker.join(); vault.close()

if __name__=='__main__': main()
