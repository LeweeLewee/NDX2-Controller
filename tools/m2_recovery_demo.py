"""Silent recovery faults through the real native desktop worker, helper and TLS."""
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import tempfile
import threading
import time
from m2_bridge import Contract, FixtureService, server
from m2_certificates import create
from m2_security import Pairing, Vault

ROOT=Path(__file__).resolve().parents[1]

class Faults:
    def __init__(self, contract):
        self.contract=contract
        self.delays=[]
        self.requests=[]

    def handle(self, device, request):
        self.requests.append(request['action'])
        response=self.contract.handle(device,request)
        if self.delays:
            action,delay=self.delays.pop(0)
            assert request['action']==action, request['action']
            time.sleep(delay)  # Execute first, then lose/delay the reply.
        return response


def main():
    with tempfile.TemporaryDirectory() as temporary:
        root=Path(temporary); create(root/'tls')
        vault=Vault(root/'bridge'); pairing=Pairing(vault)
        controller=Vault(root/'controller')
        controller.update(lambda data:data.update(controller=pairing.pair(pairing.issue())))
        controller.close()
        service=FixtureService(); faults=Faults(Contract(service,vault))
        httpd=server(faults,pairing,root/'tls/trust.pem',root/'tls/key.pem',port=0)
        # Expected writes to timed-out TLS clients are deliberately discarded.
        httpd.handle_error=lambda *_:None
        worker=threading.Thread(target=httpd.serve_forever,daemon=True)
        config=root/'desktop.json'
        config.write_text(json.dumps({'url':'https://127.0.0.1:'+str(httpd.server_port),
            'trust':str(root/'tls/trust.pem'),'state':str(root/'controller')}))
        process=subprocess.Popen([str(ROOT/'local/m2/desktop-verified/desktop_transport_test.exe'),
            sys.executable,str(config)],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,text=True,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        lines=queue.Queue()
        def reader():
            for line in process.stdout: lines.put(line.rstrip())
            lines.put(None)
        reader_thread=threading.Thread(target=reader,daemon=True); reader_thread.start()
        expected=iter(('START','DELAY_READ','DELAY_PLAY','DELAY_AMPLIFIER','RESTART'))
        phases=0; passed=False
        try:
            while True:
                line=lines.get(timeout=25)
                if line is None: break
                print(line)
                if line.startswith('PASS '): passed=True; continue
                assert line==next(expected),line
                phases+=1
                if line=='START': worker.start()
                elif line=='DELAY_READ': faults.delays=[('snapshot',6)]
                elif line=='DELAY_PLAY': faults.delays=[('snapshot',4),('play',4)]
                elif line=='DELAY_AMPLIFIER': faults.delays=[('snapshot',0),('amplifier',6)]
                elif line=='RESTART': faults.contract=Contract(service,vault)
                process.stdin.write('go\n'); process.stdin.flush()
            assert process.wait(timeout=5)==0 and passed and phases==5
            assert [call[0] for call in service.naim.calls]==['play','amplifier'],service.naim.calls
            assert faults.requests.count('play')==faults.requests.count('amplifier')==1
            assert not faults.delays
            print('PASS exactly one silent play and one amplifier call; no replay after timeout or restart')
        finally:
            if process.poll() is None: process.kill(); process.wait()
            process.stdin.close(); reader_thread.join(timeout=2); process.stdout.close()
            if worker.is_alive(): httpd.shutdown(); worker.join()
            httpd.server_close(); vault.close()

if __name__=='__main__': main()
