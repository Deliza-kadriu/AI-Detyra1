import copy
import json
from pathlib import Path
import unittest

from golfers_reference import verify_reference


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((Path(__file__).resolve().parents[1] /
                                'data/golfers-10-reference.json').read_text())

    def test_witness_attains_upper_bound(self):
        result = verify_reference(self.data)
        self.assertTrue(result['maximum_proven'])
        self.assertEqual(result['optimal_weeks'], 10)
        self.assertEqual(len(result['unmet_pairs']), 16)
        self.assertEqual(sorted(p for pair in result['unmet_pairs'] for p in pair), list(range(32)))

    def test_repeated_week_is_rejected(self):
        corrupted = copy.deepcopy(self.data)
        corrupted['schedule'][1] = corrupted['schedule'][0]
        corrupted['labelled_weeks'][1] = corrupted['labelled_weeks'][0]
        with self.assertRaises(ValueError):
            verify_reference(corrupted)

    def test_transcription_mismatch_is_rejected(self):
        self.data['schedule'][0][0][0] = 31
        with self.assertRaises(ValueError):
            verify_reference(self.data)
