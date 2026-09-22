import concurrent.futures
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import ssl
import socket
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parents[1] / 'tools'))
from m2_security import Vault, Pairing, Renewal, Revoked
from m2_bridge import Contract, FixtureService, server, MAX_RESPONSE
from m2_client import Client, Controller
from m2_certificates import create
from m2_library import PersistentLibrary
from tidal_catalog import CatalogError


class LocalClient:
    def __init__(self, contract): self.contract, self.count = contract, 0
    def request(self, action, args=None):
        self.count += 1
        return self.contract.handle('device', {'version':1, 'request_id':f'request_{self.count:016d}',
                                             'action':action, 'args':args or {}})


class M2Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.vault = Vault(Path(self.temp.name) / 'vault')
        self.time = [100.0]
        self.service = FixtureService()
        self.contract = Contract(self.service, self.vault, lambda:self.time[0])
        self.client = LocalClient(self.contract)
    def tearDown(self):
        self.vault.close(); self.temp.cleanup()
    def req(self, action, args=None, rid='a'*32):
        return self.contract.handle('device', {'version':1,'request_id':rid,'action':action,'args':args or {}})
    def test_pair_expiry_single_use_revocation_restart(self):
        pairing = Pairing(self.vault, lambda:self.time[0])
        code=pairing.issue(); self.time[0]+=121
        with self.assertRaises(PermissionError): pairing.pair(code)
        code=pairing.issue(); result=pairing.pair(code)
        with self.assertRaises(PermissionError): pairing.pair(code)
        self.assertEqual(pairing.authenticate(result['credential']),result['device'])
        self.assertNotIn(result['credential'].encode(),self.vault.path.read_bytes())
        self.vault.close(); self.vault=Vault(Path(self.temp.name)/'vault')
        pairing=Pairing(self.vault)
        self.assertEqual(pairing.authenticate(result['credential']),result['device'])
        pairing.revoke(result['device'])
        with self.assertRaises(PermissionError): pairing.authenticate(result['credential'])
    def test_pair_attempt_budget(self):
        pairing=Pairing(self.vault); code=pairing.issue()
        for _ in range(5):
            with self.assertRaises(PermissionError): pairing.pair('wrong')
        with self.assertRaises(PermissionError): pairing.pair(code)
    def test_persistent_library_renewal_and_invalid_grant(self):
        self.vault.update(lambda d:d.update(refresh='synthetic-old'))
        calls=[]
        class Catalog:
            _client_id='synthetic-client'
            def _json(self, request):
                calls.append(request)
                if 'oauth2/token' in request.full_url:
                    return {'access_token':'synthetic-access','refresh_token':'synthetic-new',
                            'expires_in':100,'scope':'collection.read collection.write'}
                return {'data':[]}
        library=PersistentLibrary(Catalog(),self.vault,clock=lambda:self.time[0],sleep=lambda _:None)
        self.assertEqual(library.page('albums')['items'],[])
        self.assertEqual(self.vault.data['refresh'],'synthetic-new')
        self.assertTrue(library.connected)
        library.page('albums'); self.assertEqual(sum('oauth2/token' in r.full_url for r in calls),1)
        self.time[0]+=101
        def rejected(request): raise CatalogError('sanitized',400,oauth_error='invalid_grant')
        library.catalog._json=rejected
        with self.assertRaises(PermissionError): library.page('albums')
        self.assertFalse(library.connected); self.assertIsNone(self.vault.data['refresh'])
    def test_late_snapshot_discarded_and_freshness_expires(self):
        model=Controller(self.client,lambda:self.time[0]); model.reconnect(); model.touch(False)
        self.time[0]+=6; self.assertFalse(model.available)
        original=self.client.request
        def late(action,args=None):
            result=original(action,args); model.disconnect(); return result
        self.client.request=late
        self.assertFalse(model.reconnect()); self.assertFalse(model.online)
    def test_overlapping_amplifier_rejected(self):
        self.req('snapshot')
        entered=threading.Event(); release=threading.Event(); calls=[]
        def nudge(direction): calls.append(direction); entered.set(); release.wait(2)
        self.service.naim.amplifier_nudge=nudge
        worker=threading.Thread(target=lambda:self.req('amplifier',{'direction':'up'})); worker.start()
        self.assertTrue(entered.wait(2))
        self.assertEqual(self.req('amplifier',{'direction':'down'},'b'*32)['error']['code'],'BUSY')
        release.set(); worker.join(); self.assertEqual(calls,['up'])
    def test_rotation_single_flight_and_restart(self):
        self.vault.update(lambda d:d.update(refresh='synthetic-old'))
        calls=[]
        def exchange(old):
            calls.append(old); time.sleep(.02)
            return {'access_token':'synthetic-access','refresh_token':'synthetic-new','expires_in':300}
        renewal=Renewal(self.vault,exchange)
        with concurrent.futures.ThreadPoolExecutor(8) as pool:
            self.assertEqual(list(pool.map(lambda _:renewal.get(), range(16))),['synthetic-access']*16)
        self.assertEqual(calls,['synthetic-old'])
        self.vault.close(); self.vault=Vault(Path(self.temp.name)/'vault')
        self.assertEqual(self.vault.data['refresh'],'synthetic-new')
        if os.name=='nt': self.assertNotIn(b'synthetic-new',self.vault.path.read_bytes())
    def test_rotation_atomic_failure_no_access_published(self):
        self.vault.update(lambda d:d.update(refresh='old'))
        renewal=Renewal(self.vault,lambda _: {'access_token':'a','refresh_token':'new','expires_in':100})
        with patch('m2_security.os.replace',side_effect=OSError('disk full')):
            with self.assertRaises(RuntimeError): renewal.get()
        self.assertIsNone(renewal.access)
        self.assertEqual(self.vault.data['refresh'],'old')
        self.vault.close(); self.vault=Vault(Path(self.temp.name)/'vault')
        self.assertEqual(self.vault.data['refresh'],'old')
    def test_rotation_omitted_replacement_revoked_transient(self):
        self.vault.update(lambda d:d.update(refresh='old'))
        renewal=Renewal(self.vault,lambda _: {'access_token':'a','expires_in':100})
        renewal.get(); self.assertEqual(self.vault.data['refresh'],'old')
        def failed(_): raise TimeoutError()
        with self.assertRaises(RuntimeError): Renewal(self.vault,failed).get()
        self.assertEqual(self.vault.data['refresh'],'old')
        def revoked(_): raise Revoked()
        with self.assertRaises(PermissionError): Renewal(self.vault,revoked).get()
        self.assertIsNone(self.vault.data['refresh'])
    def test_duplicate_conflict_restart_and_unknown(self):
        self.req('snapshot')
        result=self.req('play',{'reference':'inputs/tidal/albums/1'})
        self.assertEqual(result['outcome'],'submitted')
        self.req('play',{'reference':'inputs/tidal/albums/1'})
        self.assertEqual(len(self.service.naim.calls),1)
        self.assertEqual(self.req('play',{'reference':'inputs/tidal/albums/2'})['error']['code'],'REQUEST_ID_CONFLICT')
        self.contract=Contract(self.service,self.vault)
        self.assertEqual(self.req('play',{'reference':'inputs/tidal/albums/1'})['outcome'],'submitted')
        self.req('snapshot')
        def timeout(*args): self.service.naim.calls.append('uncertain'); raise TimeoutError()
        self.service.naim.play=timeout
        self.assertEqual(self.req('play',{'reference':'inputs/tidal/albums/2'},rid='b'*32)['outcome'],'unknown')
        self.contract=Contract(self.service,self.vault)
        self.assertEqual(self.req('play',{'reference':'inputs/tidal/albums/2'},rid='b'*32)['outcome'],'unknown')
        self.assertEqual(len(self.service.naim.calls),2)
    def test_stale_and_unavailable_disable_mutations(self):
        self.assertEqual(self.req('amplifier',{'direction':'up'})['error']['code'],'STATE_STALE')
        self.req('snapshot'); self.time[0]+=6
        self.assertEqual(self.req('amplifier',{'direction':'down'})['outcome'],'rejected')
        self.assertFalse(self.service.naim.calls)
    def test_slow_snapshot_does_not_renew_old_player_state(self):
        original=self.service.naim.queue
        def slow(): self.time[0]+=6; return original()
        self.service.naim.queue=slow
        result=self.req('snapshot')
        self.assertEqual(result['data']['age_ms'],6000)
        self.assertEqual(result['data']['valid_for_ms'],0)
        self.assertEqual(self.req('amplifier',{'direction':'up'})['error']['code'],'STATE_STALE')
    def test_sanitized_provider_failure(self):
        def failure(): raise RuntimeError('SYNTHETIC_PRIVATE_SECRET')
        self.service.naim.status=failure
        response=self.req('snapshot')
        self.assertEqual(response['error']['code'],'SERVICE_UNAVAILABLE')
        self.assertNotIn('SYNTHETIC_PRIVATE_SECRET',json.dumps(response))
    def test_wal_precedes_dispatch_and_disk_failure_blocks(self):
        self.req('snapshot')
        with patch.object(self.vault,'update',side_effect=OSError()):
            self.assertEqual(self.req('amplifier',{'direction':'up'})['outcome'],'rejected')
        self.assertFalse(self.service.naim.calls)
        def crash(*args): raise KeyboardInterrupt()
        self.service.naim.play=crash
        with self.assertRaises(KeyboardInterrupt): self.req('play',{'reference':'inputs/tidal/albums/1'})
        self.contract=Contract(self.service,self.vault)
        self.assertEqual(self.req('play',{'reference':'inputs/tidal/albums/1'})['outcome'],'unknown')
    def test_bounded_pages_and_validation(self):
        first=self.req('search',{'query':'silent','kind':'albums'})
        self.assertEqual(len(first['data']['items']),12)
        self.assertEqual(first['data']['next_offset'],12)
        second=self.req('search',{'query':'silent','kind':'albums','offset':12})
        self.assertNotEqual(first['data']['items'][0],second['data']['items'][0])
        self.assertLess(len(json.dumps(second).encode()),MAX_RESPONSE)
        self.assertEqual(self.req('search',{'query':'x'*257})['outcome'],'rejected')
        self.assertEqual(self.req('play',{'reference':'x','placement':'last'})['outcome'],'rejected')
        self.assertEqual(self.req('queue',{'offset':True})['outcome'],'rejected')
    def test_vertical_slice_back_wake_queue_collection_voice(self):
        model=Controller(self.client,lambda:self.time[0])
        self.assertTrue(model.reconnect()); self.assertFalse(model.available)
        self.assertFalse(model.touch(True)); self.assertFalse(model.touch(False)); self.assertTrue(model.touch(True))
        model.search('quiet','albums'); model.more(); model.context['scroll']=.4
        previous=copy.deepcopy(model.context)
        model.details(model.context['items'][0]); model.back()
        self.assertEqual(model.context,previous)
        model.details(model.context['items'][0])
        ref=model.selected['item']['reference']
        self.assertEqual(model.mutate('play',{'reference':ref}),'submitted')
        self.assertEqual(model.snapshot['player']['title'],'Silent track')
        self.assertEqual(model.snapshot['queue'][0]['title'],'Silent track')
        self.assertEqual(model.read('library_state',{'reference':ref})['saved_state'],'unknown')
        model.mutate('library_save',{'reference':ref,'saved':True})
        self.assertEqual(model.read('library_state',{'reference':ref})['saved_state'],'saved')
        model.mutate('library_save',{'reference':ref,'saved':False})
        self.assertEqual(model.read('library_state',{'reference':ref})['saved_state'],'unsaved')
        count=len(self.service.naim.calls)
        model.record(); self.time[0]+=30; model.tick(); self.assertEqual(model.voice,'stopped')
        model.submit_voice(); self.assertEqual(len(self.service.naim.calls),count)
        model.reconnect(); model.record(); model.disconnect(); self.assertEqual(model.voice,'idle')
        model.context['scroll']=.6; model.pending='amplifier'; model.wake()
        self.assertEqual(model.outcome,'unknown'); self.assertEqual(model.context['scroll'],.6)
        self.assertIsNone(model.pending); self.assertFalse(model.available)
        model.touch(False); self.assertTrue(model.available)
    def test_voice_limit_restart_exit_and_explicit_search(self):
        model=Controller(self.client,lambda:self.time[0]); model.reconnect(); model.touch(False)
        model.push('voice'); self.assertEqual(model.voice,'recording_fixture')
        count=self.client.count; self.time[0]+=30; model.tick()
        self.assertEqual(model.voice,'stopped'); self.assertEqual(self.client.count,count)
        self.assertEqual(model.transcript,'')
        model.reconnect(); model.record(); self.assertEqual(model.record_deadline,self.time[0]+30)
        model.back(); self.assertEqual(model.voice,'idle')
        model.push('voice'); model.submit_voice()
        self.assertEqual(model.context['screen'],'find'); self.assertIn('quiet',model.context['query'])
        self.assertEqual(self.service.naim.calls,[])

    def test_artist_track_membership_and_collection_are_independent(self):
        artist='inputs/tidal/artists/1'; track='inputs/tidal/tracks/101'; album='inputs/tidal/albums/1'
        self.assertEqual(self.client.request('browse',{'reference':artist})['data']['item']['kind'],'artists')
        self.client.request('snapshot')
        self.assertEqual(self.client.request('library_save',{'reference':artist,'saved':True})['outcome'],'submitted')
        self.assertEqual(self.client.request('library_state',{'reference':artist})['data']['saved_state'],'saved')
        self.assertEqual(self.client.request('library_state',{'reference':track})['data']['saved_state'],'unsaved')
        self.assertEqual(self.client.request('library_state',{'reference':album})['data']['saved_state'],'unknown')
        page=self.client.request('library_page',{'kind':'artists'})['data']
        self.assertEqual(page['items'][0]['reference'],artist); self.assertLessEqual(len(page['items']),12)
        self.assertEqual(self.client.request('library_page',{'kind':'invalid'})['outcome'],'rejected')
        self.assertEqual(self.service.naim.calls,[])

    def test_snapshot_links_are_exact_and_missing_metadata_stays_absent(self):
        result=self.client.request('snapshot')['data']
        self.assertEqual(result['current_item']['artist_reference'],'inputs/tidal/artists/1')
        self.assertEqual(result['current_item']['album_reference'],'inputs/tidal/albums/1')
        self.assertIsNone(result['player']['bitrate'])
        original=self.service.request
        def unavailable(action,args):
            if action in ('related','current_item'): raise RuntimeError('PRIVATE')
            return original(action,args)
        self.service.request=unavailable
        result=self.client.request('snapshot')
        self.assertIsNone(result['data']['current_item']); self.assertNotIn('PRIVATE',json.dumps(result))

    def test_timeout_client_never_replays(self):
        model=Controller(self.client); model.reconnect(); model.touch(False)
        count=[]
        def timeout(*args): count.append(args); raise TimeoutError()
        self.client.request=timeout
        self.assertEqual(model.mutate('play',{'reference':'inputs/tidal/albums/1'}),'unknown')
        self.assertEqual(len(count),1); self.assertFalse(model.online)


class TLSTests(unittest.TestCase):
    def test_auth_wrong_trust_revocation_and_https_slice(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); create(root/'tls'); create(root/'wrong')
            vault=Vault(root/'vault'); pairing=Pairing(vault)
            contract=Contract(FixtureService(),vault)
            httpd=server(contract,pairing,root/'tls/trust.pem',root/'tls/key.pem',port=0)
            thread=threading.Thread(target=httpd.serve_forever,daemon=True); thread.start()
            try:
                url='https://127.0.0.1:'+str(httpd.server_port)
                client=Client(url,root/'tls/trust.pem')
                with self.assertRaises(urllib.error.HTTPError) as unauth: client.request('snapshot')
                self.assertEqual(unauth.exception.code,401)
                wrong=Client(url,root/'wrong/trust.pem')
                with self.assertRaises(urllib.error.URLError) as wrong_trust: wrong.pair(pairing.issue())
                self.assertIsInstance(wrong_trust.exception.reason,ssl.SSLCertVerificationError)
                context=ssl.create_default_context(cafile=str(root/'tls/trust.pem'))
                with socket.create_connection(('127.0.0.1',httpd.server_port),timeout=2) as connection:
                    with self.assertRaises(ssl.SSLCertVerificationError):
                        context.wrap_socket(connection,server_hostname='wrong.invalid')
                auth=client.pair(pairing.issue())
                model=Controller(client); self.assertTrue(model.reconnect()); model.touch(False)
                model.search('quiet','albums'); model.details(model.context['items'][0])
                self.assertEqual(model.mutate('play',{'reference':model.selected['item']['reference']}),'submitted')
                self.assertEqual(model.snapshot['player']['title'],'Silent track')
                pairing.revoke(auth['device']); self.assertFalse(model.reconnect())
            finally:
                httpd.shutdown(); httpd.server_close(); thread.join(); vault.close()


if __name__=='__main__': unittest.main()
