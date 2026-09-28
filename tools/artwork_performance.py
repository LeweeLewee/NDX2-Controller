"""Explicit read-only artwork assessment; fixture mode is the default. No player writes."""
import argparse
import io
import json
import statistics
import time
from unittest.mock import patch
from m2_bridge import Contract, FixtureService
from controller_service import Bridge
from naim_client import NaimClient
from m2_artwork import normalize, CHUNK_PIXELS


def assess(service, rounds=2, requester=None, encoding="rgb565be-hex"):
    class Vault:
        data = {'commands': {}}
    contract = Contract(service, Vault())
    def request(action, args=None):
        return contract.handle('performance-read', {'version': 1, 'request_id': 'p'*32,
                              'action': action, 'args': args or {}})
    if requester is not None: request = requester
    snapshots = []
    for _ in range(5):
        start = time.perf_counter(); response = request('snapshot')
        snapshots.append((time.perf_counter()-start)*1000)
        if response['outcome'] != 'observed': raise RuntimeError('Snapshot unavailable')
    ref = response['data']['player']['artwork']
    if not ref: raise RuntimeError('No current artwork')
    queue = request('queue')['data']['items']
    report = {'snapshot_ms': snapshots, 'snapshot_median_ms': statistics.median(snapshots),
              'queue_items': len(queue), 'queue_distinct_covers': len({i.get('artwork') for i in queue if i.get('artwork')}),
              'exact_album_link': bool((response['data'].get('current_item') or {}).get('album_reference')),
              'exact_artist_link': bool((response['data'].get('current_item') or {}).get('artist_reference')),
              'account': response['data']['account'], 'covers': []}
    original = service.image
    fetches = []
    def timed_image(reference):
        started = time.perf_counter(); raw = original(reference)
        fetches.append((time.perf_counter()-started)*1000)
        return raw
    with patch.object(service, 'image', side_effect=timed_image):
        for _ in range(rounds):
            chunk_times=[]; total=0; calls=len(fetches); begin=time.perf_counter()
            for offset in ([0] if encoding == 'jpeg-base64' else range(0,320*320,CHUNK_PIXELS)):
                start=time.perf_counter(); reply=request('artwork',{'reference':ref,'side':320,'pixel_offset':offset,'encoding':encoding})
                chunk_times.append((time.perf_counter()-start)*1000)
                if not (reply.get('data') or {}).get('available'): raise RuntimeError('Artwork unavailable')
                total+=len(json.dumps(reply).encode())
            report['covers'].append({'total_ms':(time.perf_counter()-begin)*1000,'chunk_ms':chunk_times,
                                     'json_bytes':total,'source_fetches':len(fetches)-calls})
    report['source_fetch_ms']=fetches
    report['encoding']=encoding
    # Isolated format experiment only: not a production codec or protocol change.
    from PIL import Image
    raw=original(ref); start=time.perf_counter(); normalize(raw,320,0,with_digest=True)
    report['one_decode_resize_chunk_ms']=(time.perf_counter()-start)*1000
    with Image.open(io.BytesIO(raw)) as image:
        small=image.convert('RGB').resize((320,320),Image.Resampling.LANCZOS)
        output=io.BytesIO();small.save(output,format='JPEG',quality=80,optimize=True)
    report['experimental_jpeg_bytes']=len(output.getvalue())
    report['experimental_base64_bytes']=4*((len(output.getvalue())+2)//3)
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ndx',help='Explicitly enable read-only native/CDN assessment at this private IPv4 address')
    parser.add_argument('--tls',action='store_true',help='Use an isolated authenticated loopback TLS bridge; never changes the running bridge or enrollment')
    parser.add_argument('--output',required=True)
    parser.add_argument('--encoding', choices=('rgb565be-hex','jpeg-base64'), default='rgb565be-hex')
    args=parser.parse_args()
    service=Bridge(NaimClient(args.ndx,timeout=3)) if args.ndx else FixtureService()
    if args.tls:
        import tempfile, threading
        from pathlib import Path
        from m2_bridge import server
        from m2_certificates import create
        from m2_client import Client
        from m2_security import Pairing, Vault
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);create(root/'tls');vault=Vault(root/'vault')
            pairing=Pairing(vault);contract=Contract(service,vault)
            host=server(contract,pairing,root/'tls/trust.pem',root/'tls/key.pem',port=0)
            worker=threading.Thread(target=host.serve_forever,daemon=True);worker.start()
            try:
                client=Client('https://127.0.0.1:'+str(host.server_port),root/'tls/trust.pem')
                client.pair(pairing.issue())
                result=assess(service,requester=client.request,encoding=args.encoding)
            finally:
                host.shutdown();host.server_close();worker.join();vault.close()
    else:
        result=assess(service,encoding=args.encoding)
    result['mode']='live-native-read-only' if args.ndx else 'offline-fixture'
    result['transport']='authenticated-loopback-TLS' if args.tls else 'in-process'
    from pathlib import Path
    Path(args.output).write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('covers','source_fetch_ms','snapshot_ms')}))
    print('cover_ms:',[round(c['total_ms'],1) for c in result['covers']], 'source_fetches:',[c['source_fetches'] for c in result['covers']])

if __name__=='__main__': main()
