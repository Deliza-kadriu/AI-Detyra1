"""Exercise the same experiment dispatcher used by the browser UI."""

import copy
import unittest

from demo_runner import run_experiment
from sudoku import load_examples


class DemoTests(unittest.TestCase):
    def run_demo(self, **params):
        events = []
        result = run_experiment({'trace': True, 'delay': 0, **params},
                                lambda event: events.append(copy.deepcopy(event)))
        self.assertEqual(events[-1], result)
        return result, events

    def test_all_experiment_types_and_validation(self):
        for params in [
            {'algorithm': 'golfers', 'groups': 3, 'players_per_group': 2, 'weeks': 5},
            {'algorithm': 'sudoku', 'difficulty': 'all'},
            {'algorithm': 'latin', 'size': 3, 'symmetry': False},
            {'algorithm': 'trees', 'problem': 'all'},
            {'algorithm': 'reference'},
        ]:
            with self.subTest(algorithm=params['algorithm']):
                result, events = self.run_demo(**params)
                self.assertTrue(all(run['validation']['valid'] for run in result['runs']))
                self.assertTrue(any(e['type'] == 'trace' for e in events))

    def test_trace_does_not_change_results_and_snapshots_are_live(self):
        for algorithm, field in [('sudoku', 'solution'), ('latin', 'square')]:
            traced, events = self.run_demo(algorithm=algorithm)
            plain = run_experiment({'algorithm': algorithm, 'trace': False}, lambda e: None)
            self.assertEqual(traced['runs'][0][field], plain['runs'][0][field])
            snapshots = [e['board'] for e in events if 'board' in e]
            self.assertGreater(len(snapshots), 1)
            self.assertNotEqual(snapshots[0], snapshots[-1])

    def test_limits_and_bound_statuses(self):
        result, _ = self.run_demo(algorithm='golfers', groups=2, players_per_group=2, weeks=7)
        self.assertEqual(result['runs'][0]['stats']['status'], 'infeasible')
        self.assertEqual(result['runs'][0]['stats']['expanded_nodes'], 0)
        result, _ = self.run_demo(algorithm='sudoku', max_nodes=1)
        self.assertEqual(result['runs'][0]['stats']['status'], 'resource_limit')
        self.assertIsNone(result['runs'][0]['validation'])

    def test_custom_board_and_invalid_input(self):
        result, _ = self.run_demo(algorithm='sudoku', difficulty='custom', board=load_examples()['easy'])
        self.assertTrue(result['runs'][0]['validation']['valid'])
        for params in [{'algorithm': 'unknown'}, {'algorithm': 'latin', 'size': 0},
                       {'algorithm': 'sudoku', 'difficulty': 'custom', 'board': []},
                       {'time_limit': float('nan')}, {'delay': -1}]:
            with self.assertRaises(ValueError):
                run_experiment(params, lambda e: None)
