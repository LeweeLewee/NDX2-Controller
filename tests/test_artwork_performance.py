import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).parents[1]/'tools'))
from artwork_performance import assess
from m2_bridge import FixtureService, MAX_RESPONSE

class PerformanceDiagnosticTests(unittest.TestCase):
    def test_default_assessment_is_offline_read_only_and_counts_whole_cover(self):
        service=FixtureService()
        result=assess(service,rounds=1)
        self.assertEqual(service.naim.calls,[])
        self.assertEqual(len(result['snapshot_ms']),5)
        self.assertEqual(len(result['covers']),1)
        cover=result['covers'][0]
        self.assertEqual(len(cover['chunk_ms']),16)
        self.assertEqual(cover['source_fetches'],16)
        self.assertLess(cover['json_bytes'],16*MAX_RESPONSE)
        self.assertGreater(cover['json_bytes'],409600)
        self.assertGreater(result['experimental_jpeg_bytes'],0)
        self.assertGreater(result['experimental_base64_bytes'],result['experimental_jpeg_bytes'])
