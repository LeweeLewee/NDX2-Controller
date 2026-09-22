"""Silent same-CA renewal and explicit CA change; no live certificate operations."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
from unittest.mock import patch
from m2_bridge import Contract, FixtureService, server
from m2_provisioning import Enrollment, EnrollmentError
from m2_security import Pairing, Vault
from m2_tls_fixture import authority, leaf
import m2_setup


def main():
    with tempfile.TemporaryDirectory() as temporary:
        root=Path(temporary)
        ca=authority(root/'ca'); other=authority(root/'other')
        for name,issuer,expired,wrong in [('first',ca,False,False),('renewed',ca,False,False),
            ('expired',ca,True,False),('wrong',ca,False,True),('rotated',other,False,False)]:
            leaf(root/name,issuer,expired,wrong)
        vault=Vault(root/'bridge'); pairing=Pairing(vault); service=FixtureService(); contract=Contract(service,vault)
        controller=Vault(root/'controller'); httpd=None; worker=None; port=0
        def restart(name):
            nonlocal httpd,worker,port
            if httpd:
                httpd.shutdown(); worker.join(); httpd.server_close()
            httpd=server(contract,pairing,root/name/'trust.pem',root/name/'key.pem',port=port)
            port=httpd.server_port; worker=threading.Thread(target=httpd.serve_forever,daemon=True); worker.start()
        try:
            restart('first'); url='https://127.0.0.1:'+str(port); trust=root/'ca/trust.pem'
            flow=Enrollment(controller,url,trust); device=flow.pair(pairing.issue())['device']
            credential=controller.data['controller']['credential']; old_digest=controller.data['controller']['trust_sha256']
            assert flow.verify()['state']=='connected'
            restart('renewed'); assert flow.verify()['state']=='connected'
            assert pairing.devices()==[device]
            print('PASS renewed leaf certificate under unchanged CA preserves pairing')
            for name in ('expired','wrong','rotated'):
                restart(name)
                try: flow.verify()
                except EnrollmentError: pass
                else: raise AssertionError('Invalid/unexpected certificate accepted')
                assert controller.data['controller']['trust_sha256']==old_digest
            print('PASS expired, wrong-host and unexpected-CA certificates rejected; old binding retained')
            new_trust=root/'other/trust.pem'; controller.close()
            config=root/'desktop.json'; config.write_text(json.dumps({'url':url,'trust':str(new_trust),'state':str(root/'controller')}))
            captured=io.StringIO()
            with contextlib.redirect_stdout(captured), patch.object(sys.stdin,'isatty',return_value=True), patch('builtins.input',return_value='cancel'):
                assert m2_setup.main(['--config',str(config),'trust-update'])==1
            controller=Vault(root/'controller'); assert controller.data['controller']['trust_sha256']==old_digest; controller.close()
            with contextlib.redirect_stdout(captured), patch.object(sys.stdin,'isatty',return_value=True), patch('builtins.input',return_value='UPDATE TRUST'):
                assert m2_setup.main(['--config',str(config),'trust-update'])==0
            controller=Vault(root/'controller'); flow=Enrollment(controller,url,new_trust)
            assert flow.verify()['state']=='connected'
            assert controller.data['controller']['credential']==credential and pairing.devices()==[device]
            try: Enrollment(controller,url,trust).verify()
            except EnrollmentError: pass
            else: raise AssertionError('Old binding accepted after explicit replacement')
            assert service.naim.calls==[] and credential not in captured.getvalue()
            print('PASS cancelled/approved operator trust update, durable reopen and old-binding rejection')
            print('PASS same credential retained; zero playback, volume or re-pair requests')
        finally:
            controller.close()
            if httpd: httpd.shutdown(); worker.join(); httpd.server_close()
            vault.close()

if __name__=='__main__': main()
