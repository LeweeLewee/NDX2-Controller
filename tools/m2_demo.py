"""Executable silent acceptance scenario over authenticated, verified localhost TLS."""
from pathlib import Path
import tempfile
import threading
import time
from m2_bridge import Contract, FixtureService, server
from m2_certificates import create
from m2_client import Client, Controller
from m2_security import Pairing, Vault


def main():
    with tempfile.TemporaryDirectory() as temporary:
        root=Path(temporary); create(root/'tls'); vault=Vault(root/'vault')
        pairing=Pairing(vault); service=FixtureService()
        fixture_time = [0.0]
        contract = Contract(service, vault, lambda: time.monotonic() + fixture_time[0])
        bridge=server(contract,pairing,root/'tls/trust.pem',root/'tls/key.pem',port=0)
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
            cover = client.request('snapshot')['data']['player']['artwork']
            assert len(client.request('artwork', {'reference': cover})['data']['pixels']) == 25600
            image_ids, count, offset = set(), 0, 0
            while offset is not None:
                chunk = client.request('artwork', {'reference': cover, 'side': 320, 'pixel_offset': offset})['data']
                assert chunk['available'] and chunk['offset'] == offset
                image_ids.add(chunk['image_id']); count += len(chunk['pixels']) // 4
                offset = chunk['next_offset']
            assert count == 320 * 320 and len(image_ids) == 1
            artist = client.request('artist_bio', {'reference': 'inputs/tidal/artists/1'})['data']
            assert artist['available'] and artist['biography']
            assert client.request('artwork', {'reference': artist['artwork'], 'side': 320})['data']['available']
            assert client.request('charge?')['data'] == {'charge': 'no', 'reason': 'none'}
            for level, charging, expected in ((34, False, 'yes'), (50, True, 'yes'), (75, True, 'no')):
                assert client.request('battery_report', {'level': level, 'charging': charging,
                                                        'client_id': 'fixture-display'})['data']['accepted']
                assert client.request('charge?')['data'] == {'charge': expected, 'reason': 'window'}
            assert len(service.naim.calls) == 1
            fixture_time[0] += 3600
            assert client.request('charge?')['data'] == {'charge': 'no', 'reason': 'stale'}
            assert len(service.naim.calls) == 1
            print('PASS 80/320 artwork / artist biography and portrait / bounded chunks / battery report / charge window and reasons (SILENT FIXTURE)')
        finally:
            bridge.shutdown(); bridge.server_close(); worker.join(); vault.close()


if __name__=='__main__': main()
