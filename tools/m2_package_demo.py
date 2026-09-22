"""Extracted-package and side-by-side upgrade acceptance; silent TLS only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import threading
import zipfile
import zlib
from m2_bridge import Contract, FixtureService, server
from m2_certificates import create
from m2_provisioning import Enrollment
from m2_security import Pairing, Vault


def main(archive):
    with tempfile.TemporaryDirectory() as temporary:
        root=Path(temporary); first=root/'first install'; second=root/'upgrade install'
        for directory in (first,second):
            directory.mkdir()
            with zipfile.ZipFile(archive) as bundle: bundle.extractall(directory)
        create(root/'tls'); bridge_vault=Vault(root/'bridge'); pairing=Pairing(bridge_vault); service=FixtureService()
        bridge=server(Contract(service,bridge_vault),pairing,root/'tls/trust.pem',root/'tls/key.pem',port=0)
        worker=threading.Thread(target=bridge.serve_forever,daemon=True); worker.start()
        url='https://127.0.0.1:'+str(bridge.server_port)
        controller=Vault(root/'controller')
        Enrollment(controller,url,root/'tls/trust.pem').pair(pairing.issue()); device=controller.data['controller']['device']; controller.close()
        config=root/'desktop.json'; config.write_text(json.dumps({'url':url,'trust':str(root/'tls/trust.pem'),'state':str(root/'controller')}))
        preferences=root/'preferences.bin'; payload=b'NDPF'+bytes((1,1,65,5)); preferences.write_bytes(payload+struct.pack('<I',zlib.crc32(payload)))
        pairing_before=hashlib.sha256((root/'controller/authorization.bin').read_bytes()).hexdigest(); prefs_before=preferences.read_bytes()
        env=os.environ.copy(); env['SDL_VIDEODRIVER']='dummy'; env['PYTHONHOME']='invalid-host-home'; env['PYTHONPATH']='invalid-host-packages'
        def run(command,timeout=45,cwd=None):
            result=subprocess.run([str(x) for x in command],cwd=cwd or root,env=env,capture_output=True,text=True,timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
            if result.returncode: raise RuntimeError(result.stdout+result.stderr)
            return result.stdout
        try:
            for directory in (first,second):
                python=directory/'runtime/python.exe'
                info=run([python,'-B','-c','import sys; print(sys.prefix); print(sys.path)'])
                assert str(directory) in info and 'invalid-host' not in info and 'site-packages' not in info
                run([python,'-B',directory/'tools/m2_launcher.py','--config',config,'--check'])
                run([python,'-B',directory/'tools/m2_package_setup.py','--config',config,'status'])
            captures=root/'captures'; captures.mkdir()
            run([first/'ndx_fixture.exe','--bridge',first/'runtime/python.exe',config,'--preferences',preferences,'--smoke',captures],cwd=first)
            from PIL import Image
            image=Image.open(captures/'04-playing.bmp'); assert image.size==(800,480)
            assert image.getpixel((40,90))[2]>image.getpixel((40,90))[1]
            run([second/'ndx_fixture.exe','--preferences',preferences,'--preferences-smoke','check','--smoke',captures],cwd=second)
            assert preferences.read_bytes()==prefs_before
            assert hashlib.sha256((root/'controller/authorization.bin').read_bytes()).hexdigest()==pairing_before
            assert pairing.devices()==[device]
            assert [call[0] for call in service.naim.calls]==['play']  # Only the explicit native smoke action.
            assert not (first/'tools/m2_bridge.py').exists()
            assert not (first/'runtime/Lib/site-packages').exists()
            print('PASS extracted package: isolated bundled Python, paired TLS, actual LVGL artwork and no repository working directory')
            print('PASS side-by-side upgrade retains byte-identical pairing/preferences; no command replay')
        finally:
            bridge.shutdown(); bridge.server_close(); worker.join(); bridge_vault.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('archive'); main(Path(parser.parse_args().archive).resolve())
