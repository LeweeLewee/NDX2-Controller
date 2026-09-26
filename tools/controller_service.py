"""Reviewed feasibility service; transport-independent metadata/control only."""
import urllib.parse
import hashlib
from collections import OrderedDict
from naim_client import NaimClient, native_ref, playback_state
from tidal_catalog import TidalCatalog, CatalogError, ordered_items
from music_discovery import MusicDiscovery, DiscoveryError, read_key
from artwork_cache import ArtworkCache, validate_artwork_url
from tidal_library import TidalLibrary, LibraryError


def native_item(data):
    reference = str(data.get('ussi', '')).strip('/')
    return {'reference': reference, 'title': str(data.get('title') or data.get('name') or 'Untitled'),
            'artist': str(data.get('artist') or data.get('artistName') or ''),
            'kind': reference.split('/')[2] if reference.startswith('inputs/tidal/') else 'tracks'}


class Bridge:
    def __init__(self, naim=None, catalog=None, ai=None):
        self.naim, self.catalog = naim, catalog
        self.ai = ai
        self.library = None
        self.resolved = set()
        self.artwork = ArtworkCache()
        self.artwork_refs = OrderedDict()

    def cover(self, value):
        try:
            url = validate_artwork_url(value)
        except ValueError:
            return None
        path = '/artwork/' + hashlib.sha256(url.encode()).hexdigest() + '.jpg'
        self.artwork_refs[path] = url
        self.artwork_refs.move_to_end(path)
        while len(self.artwork_refs) > 32:
            self.artwork_refs.popitem(last=False)
        return path

    def image(self, path):
        # Only URLs previously returned by the Naim metadata can be fetched.
        if path not in self.artwork_refs:
            raise ValueError('Unknown artwork')
        return self.artwork.get(self.artwork_refs[path])

    def request(self, action, args):
        if not isinstance(action, str):
            raise ValueError('Expected an action')
        if self.catalog and self.library is None:
            self.library = TidalLibrary(self.catalog)
        if action == 'config':
            return {'live': self.naim is not None, 'catalog': self.catalog is not None, 'ai': self.ai is not None,
                    'library': bool(self.library and self.library.connected)}
        if action.startswith('library_'):
            if not self.library:
                raise LibraryError('Configure this project’s TIDAL app before connecting your library.')
            if action == 'library_connect':
                return {'url': self.library.begin(self.oauth_redirect)}
            if action == 'library_disconnect':
                self.library.disconnect()
                return {'message': 'TIDAL library disconnected from this controller session.'}
            if action == 'library_page':
                return self.library.page(args.get('kind', 'albums'), args.get('cursor'))
            if action == 'library_state':
                return {'saved': self.library.contains(args.get('reference'), args.get('fresh', False))}
            if action == 'library_save':
                return self.library.save(args.get('reference'), args.get('saved'))
            raise ValueError('Unknown collection action')
        if action == 'discover':
            if not self.ai:
                raise DiscoveryError('AI search is not configured on this server.')
            return self.ai.discover(args.get('prompt'), args.get('context', ''))
        if action == 'related':
            if not self.catalog:
                raise LibraryError('TIDAL catalogue access is needed for album and artist links.')
            return {'items': self.catalog.related(args.get('reference'))}
        if action == 'artist_bio':
            from artist_metadata import plain_biography
            from tidal_catalog import candidate_reference
            reference = args.get('reference')
            parts = reference.split('/') if isinstance(reference, str) else []
            if len(parts) != 4 or parts[2] != 'artists' or candidate_reference('artists', parts[3]) != reference:
                raise ValueError('Expected a TIDAL artist reference')
            metadata = self.catalog.artist_metadata(reference) if self.catalog else {}
            biography = plain_biography(metadata.get('biography'))
            return {'reference': reference, 'available': biography is not None,
                    'biography': biography, 'artwork': self.cover(metadata.get('portrait'))}
        if action == 'search':
            if not self.catalog:
                raise ValueError('Catalogue credentials are not configured')
            kind = args.get('kind', 'tracks')
            result_id = args.get('result_id')
            if not result_id:
                data = self.catalog.search(args.get('query', ''), kind).get('data', [])
                if isinstance(data, dict):
                    data = [data]
                if not data:
                    return {'items': [], 'cursor': None}
                result_id = data[0]['id']
            page = self.catalog.page(result_id, kind, args.get('cursor'))
            link = page.get('links', {}).get('next')
            if isinstance(link, dict):
                link = link.get('href')
            cursor = urllib.parse.parse_qs(urllib.parse.urlsplit(link or '').query).get('page[cursor]', [None])[0]
            return {'items': [{'reference': i['candidate_native_reference'], 'title': i['title'] or i['id'],
                               'artist': '', 'kind': kind} for i in ordered_items(page, kind)],
                    'result_id': result_id, 'cursor': cursor}
        if not self.naim:
            raise ValueError('NDX is not configured; use the on-screen demo')
        if action == 'status':
            data = self.naim.status()
            fields = ('title', 'artist', 'artistName', 'duration', 'transportPosition', 'sourceDetail', 'bitDepth', 'sampleRate', 'bitrate')
            return {**{key: data.get(key) for key in fields}, 'album': data.get('album') or data.get('albumName'),
                    'artwork': self.cover(data.get('artwork')), 'state': playback_state(data)}
        if action == 'queue':
            return {'items': [native_item(i) for i in self.naim.queue().get('children', [])]}
        if action == 'current_item':
            data = self.naim.queue()
            current = next((i for i in data.get('children', []) if i.get('ussi') == data.get('current')), {})
            if current.get('class') != 'object.track.tidal' or current.get('serverId') != 'tidal':
                raise LibraryError('The current item has no verified TIDAL track reference.')
            from tidal_catalog import candidate_reference
            reference = candidate_reference('tracks', str(current.get('track', '')))
            if not reference:
                raise LibraryError('The current track has no TIDAL identifier.')
            return {'reference': reference, 'kind': 'tracks', 'title': current.get('name', '')}
        if action == 'browse':
            reference = args.get('reference', 'inputs/tidal/favourites')
            self.resolved.discard(reference)
            data = self.naim.browse(reference, args.get('offset', 0))
            # Only a matching native object grants a play capability. Children do not.
            item = native_item(data)
            item['artwork'] = self.cover(data.get('artwork'))
            try:
                native_ref(reference)
                expected_class = {'tracks': 'object.tidalTrack', 'albums': 'object.tidalAlbum',
                                  'playlists': 'object.tidalPlaylist'}.get(reference.split('/')[2])
                playable = item['reference'] == reference and data.get('class') == expected_class
            except ValueError:
                playable = False
            if playable:
                self.resolved.add(reference)
            return {'item': item, 'playable': playable,
                    'items': [native_item(i) for i in data.get('children', [])], 'total': data.get('totalCount')}
        if action == 'play':
            reference = args.get('reference')
            if reference not in self.resolved:
                raise ValueError('Resolve this item through Naim before playing')
            # Read before every mutation; do not silently proceed if the player is unreachable.
            self.naim.status()
            self.naim.play(reference, args.get('placement', 'replace'))
            return {'message': 'Request sent. Check now playing or queue for the resulting state.'}
        if action == 'transport':
            command = args.get('command')
            if command not in ('pause', 'resume', 'stop', 'next', 'prev'):
                raise ValueError('Unsupported transport command')
            self.naim.status()
            self.naim.transport(command)
            return {'message': 'Request sent. Waiting for player state.'}
        if action == 'amplifier':
            if set(args) != {'direction'} or args.get('direction') not in ('down', 'up'):
                raise ValueError('Expected one amplifier direction: down or up')
            self.naim.amplifier_nudge(args['direction'])
            return {'message': 'Amplifier volume ' + args['direction'] + ' request sent.'}
        raise ValueError('Unknown action')
