"""Offline contract vectors and Xcode build-input integrity; not an iOS build."""
import hashlib
import json
from pathlib import Path
import plistlib
import struct
import sys
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from m2_ios_fixtures import vectors
from generate_ios_project import generate


class IOSProjectTests(unittest.TestCase):
    def test_bundled_vectors_match_real_contract_without_network(self):
        with patch('socket.socket', side_effect=AssertionError('offline fixture opened a socket')):
            actual = vectors()
        stored = json.loads((ROOT / 'ios/StillWater/Resources/BridgeFixtures.json').read_text(encoding='utf-8'))
        self.assertEqual(stored, actual)
        for name, value in stored.items():
            with self.subTest(name=name):
                reply = value['reply']
                self.assertEqual(reply['outcome'], 'observed')
                self.assertTrue(reply['fixture'])
                self.assertLessEqual(len(json.dumps(reply).encode()), 32768)
                self.assertLessEqual(len(reply['data'].get('items', [])), 12)

    def test_preview_chunks_and_charge_boundary_vectors(self):
        v = vectors()
        chunks = [v[f'artwork-{offset}']['reply']['data'] for offset in range(0, 102400, 6400)]
        self.assertEqual(len({c['image_id'] for c in chunks}), 1)
        self.assertEqual(sum(len(bytes.fromhex(c['pixels'])) for c in chunks), 204800)
        self.assertEqual(chunks[-1]['next_offset'], None)
        for name, charge, reason in [('charge-none', 'no', 'none'), ('charge-stale', 'no', 'stale'),
                                     ('charge-window', 'yes', 'window'), ('charge-window-no', 'no', 'window')]:
            self.assertEqual(v[name]['reply']['data'], {'charge': charge, 'reason': reason})
        for state in ('playing', 'paused', 'stopped'):
            self.assertEqual(v[f'snapshot-{state}']['reply']['data']['player']['state'], state)

    def test_build_graph_covers_all_sources_and_bundled_resources(self):
        objects = generate(check=True)
        targets = [o for o in objects.values() if o['isa'] == 'PBXNativeTarget']
        self.assertEqual({t['name'] for t in targets}, {'StillWater', 'StillWaterTests', 'StillWaterUITests'})
        for target in targets:
            with self.subTest(target=target['name']):
                phases = [objects[i] for i in target['buildPhases']]
                built = [objects[objects[i]['fileRef']]['path'] for p in phases for i in p['files']]
                expected = {p.relative_to(ROOT / 'ios').as_posix()
                            for p in (ROOT / 'ios' / target['name']).rglob('*')
                            if (p.suffix == '.xcassets' or (p.is_file() and p.suffix in ('.swift', '.json', '.ttf', '.txt', '.xcprivacy')))
                            and not any(parent.suffix == '.xcassets' for parent in p.parents)}
                self.assertEqual(set(built), expected)
                self.assertEqual(len(built), len(set(built)))
                if target['name'] != 'StillWater':
                    self.assertEqual(len(target['dependencies']), 1)
                    dependency = objects[target['dependencies'][0]]
                    self.assertEqual(objects[dependency['target']]['name'], 'StillWater')
        scheme = ET.parse(ROOT / 'ios/StillWater.xcodeproj/xcshareddata/xcschemes/StillWater.xcscheme')
        self.assertEqual(len(scheme.findall('.//TestableReference')), 2)
        self.assertEqual(scheme.find('.//TestAction/EnvironmentVariables/EnvironmentVariable').attrib,
                         {'key': 'STILL_WATER_FIXTURE', 'value': '1', 'isEnabled': 'YES'})
        for reference in scheme.findall('.//BuildableReference'):
            self.assertEqual(objects[reference.attrib['BlueprintIdentifier']]['name'], reference.attrib['BlueprintName'])

    def test_configuration_and_font_identity(self):
        info = plistlib.loads((ROOT / 'ios/StillWater/Info.plist').read_bytes())
        self.assertEqual(info['UIBackgroundModes'], ['processing'])
        self.assertEqual(info['UISupportedInterfaceOrientations'], ['UIInterfaceOrientationLandscapeRight'])
        self.assertEqual(info['NSAppTransportSecurity'], {'NSAllowsLocalNetworking': True})
        for key in ('NSMicrophoneUsageDescription', 'NSSpeechRecognitionUsageDescription', 'NSLocalNetworkUsageDescription'):
            self.assertTrue(info[key])
        folder = ROOT / 'ios/StillWater/Resources/Fonts'
        manifest = json.loads((folder / 'sources.json').read_text(encoding='utf-8'))
        for name, source in manifest.items():
            raw = (folder / name).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), source['sha256'])
            if name.endswith('.txt'):
                self.assertIn(b'SIL OPEN FONT LICENSE', raw)
        for filename in info['UIAppFonts']:
            raw = (folder / filename).read_bytes()
            count = struct.unpack_from('>H', raw, 4)[0]
            tables = {raw[12+i*16:16+i*16]: struct.unpack_from('>II', raw, 20+i*16) for i in range(count)}
            offset, size = tables[b'name']
            names = raw[offset:offset+size]
            _, count, strings = struct.unpack_from('>HHH', names)
            postscript = set()
            for i in range(count):
                platform, encoding, language, kind, length, position = struct.unpack_from('>HHHHHH', names, 6+i*12)
                if kind == 6 and platform in (0, 3):
                    postscript.add(names[strings+position:strings+position+length].decode('utf-16-be'))
            self.assertEqual(postscript, {Path(filename).stem})


if __name__ == '__main__':
    unittest.main()
