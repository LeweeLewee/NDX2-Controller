"""Read-only enrollment/revocation acceptance over silent loopback TLS."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import urllib.error
from m2_bridge import Contract, FixtureService, server
from m2_certificates import create
from m2_client import Client
from m2_provisioning import Enrollment, EnrollmentError
from m2_security import Pairing, Vault

ROOT=Path(__file__).resolve().parents[1]

def main():
    with tempfile.TemporaryDirectory() as temporary:
        root=Path(temporary); create(root/'tls')
        bridge_vault=Vault(root/'bridge'); pairing=Pairing(bridge_vault); service=FixtureService()
        httpd=server(Contract(service,bridge_vault),pairing,root/'tls/trust.pem',root/'tls/key.pem',port=0)
        worker=threading.Thread(target=httpd.serve_forever,daemon=True); worker.start()
        url='https://127.0.0.1:'+str(httpd.server_port); trust=root/'tls/trust.pem'
        controller=Vault(root/'controller')
        try:
            flow=Enrollment(controller,url,trust)
            enrolled=flow.pair(pairing.issue()); device=enrolled['device']
            assert flow.verify()['state']=='connected'
            # Keep a synthetic old credential only to prove it stays revoked.
            old=Client(url,trust,controller.data['controller']['credential'])
            controller.close(); controller=Vault(root/'controller'); flow=Enrollment(controller,url,trust)
            assert flow.status()==enrolled and flow.verify()['state']=='connected'
            print('PASS trusted enrollment, protected persistence and read-only verification after reopen')
            config=root/'desktop.json'; config.write_text(json.dumps({'url':url,'trust':str(trust),'state':str(root/'controller')}))
            controller.close()
            result=subprocess.run([sys.executable,str(ROOT/'tools/m2_pipe.py'),str(config)],cwd=ROOT,
                input=json.dumps({'version':1,'request_id':'enrollment_fixture_0001','action':'snapshot','args':{}})+'\n',
                capture_output=True,text=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
            assert result.returncode==0 and json.loads(result.stdout)['outcome']=='observed'
            controller=Vault(root/'controller'); flow=Enrollment(controller,url,trust)
            pairing.revoke(device)
            try: flow.verify()
            except EnrollmentError as exc: assert str(exc)=='AUTHORIZATION_REQUIRED'
            else: raise AssertionError('Revoked controller accepted')
            assert flow.status()['state']=='authorization_required'
            controller.close(); controller=Vault(root/'controller'); flow=Enrollment(controller,url,trust)
            assert flow.status()['state']=='authorization_required'
            assert pairing.devices()==[]
            print('PASS bound desktop helper, local revocation and durable authorization-required state')
            flow.forget(); replacement=flow.pair(pairing.issue())
            assert replacement['device']!=device and flow.verify()['state']=='connected'
            try: old.request('snapshot')
            except urllib.error.HTTPError as exc: assert exc.code==401
            else: raise AssertionError('Old credential revived')
            assert pairing.devices()==[replacement['device']] and service.naim.calls==[]
            print('PASS explicit re-pair, old credential remains revoked, zero playback or amplifier calls')
        finally:
            controller.close(); httpd.shutdown(); httpd.server_close(); worker.join(); bridge_vault.close()

if __name__=='__main__': main()
