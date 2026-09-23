"""Actual LVGL Play/Pause icon changes in standalone and paired silent fixtures."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
from PIL import Image,ImageChops
from m2_bridge import Contract,FixtureService,server
from m2_certificates import create
from m2_security import Pairing,Vault
ROOT=Path(__file__).resolve().parents[1]

def main(package=None):
    with tempfile.TemporaryDirectory() as temporary:
        root=Path(temporary); create(root/'tls'); vault=Vault(root/'bridge'); pairing=Pairing(vault)
        controller=Vault(root/'controller'); controller.update(lambda d:d.update(controller=pairing.pair(pairing.issue()))); controller.close()
        service=FixtureService(); bridge=server(Contract(service,vault),pairing,root/'tls/trust.pem',root/'tls/key.pem',port=0)
        worker=threading.Thread(target=bridge.serve_forever,daemon=True); worker.start()
        config=root/'desktop.json'; config.write_text(json.dumps({'url':'https://127.0.0.1:'+str(bridge.server_port),'trust':str(root/'tls/trust.pem'),'state':str(root/'controller')}))
        env=os.environ.copy(); env['SDL_VIDEODRIVER']='dummy'
        try:
            for mode in ('standalone','tls'):
                captures=ROOT/'local/m2/transport-captures'/mode; captures.mkdir(parents=True,exist_ok=True)
                command=[str((package or ROOT/'local/m2/desktop-verified')/'ndx_fixture.exe'),'--preferences',str(root/(mode+'-preferences.bin')),'--smoke',str(captures),'--transport-smoke']
                if mode=='tls': command+=['--bridge',str(package/'runtime/python.exe') if package else sys.executable,str(config)]
                result=subprocess.run(command,cwd=package or ROOT,env=env,capture_output=True,text=True,timeout=30,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
                if result.returncode: raise RuntimeError(result.stdout+result.stderr)
                pictures=[]
                for name in ('playing','paused','resumed'):
                    picture=Image.open(captures/(name+'.bmp')).convert('RGB'); picture.save(captures/(name+'.png'))
                    pictures.append(picture.crop((440,330,488,375)))
                assert ImageChops.difference(pictures[0],pictures[1]).getbbox()
                assert ImageChops.difference(pictures[0],pictures[2]).getbbox() is None
                for name in ('next','previous','previous-wrap','next-wrap'):
                    Image.open(captures/(name+'.bmp')).save(captures/(name+'.png'))
                print('PASS',mode,'native pointer taps: icon cycle and next/previous track identity')
            assert service.naim.calls==[('transport',c) for c in ('pause','resume','next','prev','prev','next')]
            print('PASS one command per tap: pause/resume, next/previous and wrap; no real audio or amplifier command')
        finally:
            bridge.shutdown(); bridge.server_close(); worker.join(); vault.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--package',type=Path)
    args=parser.parse_args(); main(args.package.resolve() if args.package else None)
