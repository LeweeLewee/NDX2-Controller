"""Run the compiled shared LVGL UI against a silent authenticated TLS bridge."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
from m2_bridge import Contract, FixtureService, server
from m2_certificates import create
from m2_security import Pairing, Vault

ROOT=Path(__file__).resolve().parents[1]


def main():
    captures=ROOT/'local/m2/native-captures'; captures.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        root=Path(temporary); create(root/'tls')
        bridge_vault=Vault(root/'bridge'); pairing=Pairing(bridge_vault)
        controller=Vault(root/'controller')
        controller.update(lambda data:data.update(controller=pairing.pair(pairing.issue())))
        controller.close()
        service=FixtureService(); contract=Contract(service,bridge_vault)
        httpd=server(contract,pairing,root/'tls/trust.pem',root/'tls/key.pem',port=0)
        worker=threading.Thread(target=httpd.serve_forever,daemon=True); worker.start()
        config=root/'desktop.json'
        config.write_text(json.dumps({'url':'https://127.0.0.1:'+str(httpd.server_port),
            'trust':str(root/'tls/trust.pem'),'state':str(root/'controller')}))
        env=os.environ.copy(); env['SDL_VIDEODRIVER']='dummy'
        try:
            result=subprocess.run([str(ROOT/'local/m2/desktop-verified/ndx_fixture.exe'),'--bridge',sys.executable,
                str(config),'--smoke',str(captures)],cwd=ROOT,env=env,timeout=45,capture_output=True,text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
            print(result.stdout)
            if result.returncode:
                print(result.stderr); raise RuntimeError('Compiled native UI smoke failed')
            assert len(service.naim.calls)==1 and service.naim.calls[0][0]=='play',service.naim.calls
            assert all((captures/name).is_file() for name in ('01-now.bmp','02-find.bmp','03-details.bmp','04-playing.bmp','05-recording.bmp','06-voice-search.bmp','07-settings.bmp','08-display.bmp','09-artist.bmp','10-following.bmp','11-track.bmp','12-voice-limit.bmp','13-wake-restored.bmp'))
            print('PASS actual LVGL pixels, paired TLS, native resolution simulation, one silent command and refreshed state')
            print('Captures:',captures)
        finally:
            httpd.shutdown(); httpd.server_close(); worker.join(); bridge_vault.close()


if __name__=='__main__': main()
