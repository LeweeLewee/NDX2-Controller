"""Executable silent acceptance scenario over authenticated, verified localhost TLS."""
from pathlib import Path
import tempfile
import threading
from m2_bridge import Contract, FixtureService, server
from m2_certificates import create
from m2_client import Client, Controller
from m2_security import Pairing, Vault


def main():
    with tempfile.TemporaryDirectory() as temporary:
        root=Path(temporary); create(root/'tls'); vault=Vault(root/'vault')
        pairing=Pairing(vault); service=FixtureService()
        bridge=server(Contract(service,vault),pairing,root/'tls/trust.pem',root/'tls/key.pem',port=0)
        worker=threading.Thread(target=bridge.serve_forever,daemon=True); worker.start()
        try:
            client=Client('https://127.0.0.1:'+str(bridge.server_port),root/'tls/trust.pem')
            client.pair(pairing.issue()); model=Controller(client)
            assert model.reconnect(); assert not model.touch(True); assert not model.touch(False)
            print('PASS boot / provisioned trust / pair / authoritative Now Playing')
            model.search('quiet','albums'); model.more(); model.context['scroll']=.4
            before=dict(model.context); model.details(model.context['items'][0]); model.back()
            assert model.context==before
            print('PASS paginated search / album detail / Back restores query, filter, page and scroll')
            model.details(model.context['items'][0]); reference=model.selected['item']['reference']
            assert model.mutate('play',{'reference':reference})=='submitted'
            assert model.snapshot['player']['title']=='A Still Morning'
            assert len(service.naim.calls)==1
            print('PASS native resolution / single play request / refreshed player and queue (SILENT FIXTURE)')
            assert model.read('library_state',{'reference':reference})['saved_state']=='unknown'
            for saved in (True,False):
                assert model.mutate('library_save',{'reference':reference,'saved':saved})=='submitted'
                assert model.read('library_state',{'reference':reference})['saved_state']==('saved' if saved else 'unsaved')
            model.record(); model.stop_recording(); assert model.voice=='stopped'; model.cancel_voice()
            model.record(); model.stop_recording(); model.submit_voice(); assert len(service.naim.calls)==1
            print('PASS saved / unsaved / unknown; voice stop / cancel / search-only submission')
            model.pending='play'; model.wake(); assert model.outcome=='unknown'; assert not model.available
            model.touch(False); assert model.available; assert len(service.naim.calls)==1
            print('PASS wake contact consumed / pending command discarded / no replay')
        finally:
            bridge.shutdown(); bridge.server_close(); worker.join(); vault.close()


if __name__=='__main__': main()
