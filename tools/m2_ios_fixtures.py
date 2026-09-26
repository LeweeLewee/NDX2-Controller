"""Generate public synthetic iOS conformance vectors from the real v1 Contract.

No vault, sockets, device configuration, credentials or live adapter are used.
"""
import argparse
import json
from pathlib import Path
from m2_bridge import Contract, FixtureService
from ios_fixture_art import sleeve, portrait


class MemoryVault:
    def __init__(self): self.data = {'commands': {}}
    def update(self, change): change(self.data)


class IOSFixtureService(FixtureService):
    """Extra metadata shapes for iOS screens; the wire protocol is unchanged."""
    def __init__(self):
        super().__init__()
        self.screen_state = 'playing'
        original = list(self.fixture_images)
        self.fixture_images[original[0]] = sleeve(0)
        self.fixture_images[original[1]] = sleeve(1)
        self.fixture_images[original[2]] = portrait()
        self.sleeves = [original[0], original[1]]
        for index in range(2,6):
            ref = self.cover(f'https://resources.tidal.com/images/fixture/sleeve-{index}.jpg')
            self.fixture_images[ref] = sleeve(index); self.sleeves.append(ref)

    def request(self, action, args):
        data = super().request(action, args)
        if action == 'status':
            if self.screen_state in ('paused', 'stopped'): data['state'] = self.screen_state
            if self.screen_state == 'longtitle': data['title'] = 'An Exceptionally Long Track Title for the Seated Listening Trial'
            if self.screen_state == 'noart': data['artwork'] = None
        if action == 'queue':
            data['items'] = [{'reference': f'inputs/tidal/tracks/{101+i}', 'title': title,
                              'artist': 'River Stone Ensemble', 'kind': 'tracks'}
                             for i, title in enumerate(('A Still Morning', 'Soft Light', 'Quiet Hours', 'Low Tide',
                                                         'Slow Rooms', 'Harbour Lights', 'Last Light', 'Far Shore'))]
        return data


def vectors():
    service = IOSFixtureService()
    clock = [100.0]
    contract = Contract(service, MemoryVault(), clock=lambda: clock[0])
    contract.boot = '1' * 32
    samples = {}

    def record(name, action, args=None):
        request = {'version': 1, 'request_id': 'fixture_request_0001', 'action': action, 'args': args or {}}
        samples[name] = {'request': request, 'reply': contract.handle('fixture', request)}
        return samples[name]['reply']

    for state in ('playing', 'paused', 'stopped', 'longtitle', 'noart'):
        service.screen_state = state
        record('snapshot-' + state, 'snapshot')
    service.screen_state = 'playing'
    reference = record('snapshot', 'snapshot')['data']['player']['artwork']
    record('queue', 'queue')
    for kind in ('albums', 'tracks', 'artists', 'playlists'):
        record('search-' + kind, 'search', {'query': 'quiet', 'kind': kind})
        record('library-' + kind, 'library_page', {'kind': kind})
        record('browse-' + kind, 'browse', {'reference': f'inputs/tidal/{kind}/1'})
    portrait = record('artist-bio', 'artist_bio', {'reference': 'inputs/tidal/artists/1'})['data']['artwork']
    record('portrait-80', 'artwork', {'reference': portrait})
    for offset in range(0, 320 * 320, 6400):
        record('portrait-' + str(offset), 'artwork', {'reference': portrait, 'side': 320, 'pixel_offset': offset})
    record('search-more', 'search', {'query': 'quiet', 'kind': 'albums', 'offset': 12})
    for state, ref in [('unknown', 'inputs/tidal/albums/1'), ('unsaved', 'inputs/tidal/artists/1')]:
        record('membership-' + state, 'library_state', {'reference': ref})
    service.saved['inputs/tidal/albums/1'] = True
    record('membership-saved', 'library_state', {'reference': 'inputs/tidal/albums/1'})
    record('artwork-80', 'artwork', {'reference': reference})
    for offset in range(0, 320 * 320, 6400):
        record('artwork-' + str(offset), 'artwork', {'reference': reference, 'side': 320, 'pixel_offset': offset})
    for index, ref in enumerate(service.sleeves):
        contract.artwork.register(ref)
        record(f'sleeve-{index}-80', 'artwork', {'reference': ref})
        for offset in range(0,320*320,6400):
            record(f'sleeve-{index}-{offset}', 'artwork', {'reference':ref,'side':320,'pixel_offset':offset})
    record('voice', 'voice_review', {'fixture': 'silent'})
    record('charge-none', 'charge?')
    record('battery', 'battery_report', {'level': 34, 'charging': False, 'client_id': 'silent-display'})
    record('charge-window', 'charge?')
    clock[0] += 3600
    record('charge-stale', 'charge?')
    record('battery-full', 'battery_report', {'level': 75, 'charging': True, 'client_id': 'silent-display'})
    record('charge-window-no', 'charge?')
    assert not service.naim.calls
    return samples


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    path = Path(__file__).resolve().parents[1] / 'ios/StillWater/Resources/BridgeFixtures.json'
    raw = json.dumps(vectors(), indent=2, ensure_ascii=False) + '\n'
    if args.check:
        if path.read_text(encoding='utf-8') != raw: raise SystemExit('iOS fixture vectors differ from the bridge')
        print('PASS iOS wire fixtures match Python Contract; zero NDX calls')
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(raw, encoding='utf-8')
        print('Wrote synthetic iOS wire fixtures')


if __name__ == '__main__': main()
