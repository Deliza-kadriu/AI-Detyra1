import unittest
from unittest.mock import patch

from benchmarks import run_benchmark, saved_baselines, sudoku_with_blanks
from demo_runner import run_experiment
from validate_sudoku import validate_solution


class BenchmarkTests(unittest.TestCase):
    def test_total_budget_does_not_claim_untested_values(self):
        times = iter([0, 1, 2, 3])
        with patch('benchmarks.perf_counter', side_effect=lambda: next(times, 10)):
            result = run_benchmark({'algorithm':'sudoku','bench_from':25,'bench_to':35,
                                    'bench_step':10,'bench_total_seconds':0.01},lambda e:None)
        self.assertEqual(result['summary']['completed_trials'], 0)
        self.assertTrue(result['summary']['total_budget_exhausted'])
        self.assertIsNone(result['summary']['largest_observed_success'])
        self.assertTrue(all(row['tested'] == 0 for row in result['rows']))

    def test_generation_counts_reproducibility_and_known_completion(self):
        solved = sudoku_with_blanks(0)
        for blanks in (0, 25, 45, 64, 81):
            board = sudoku_with_blanks(blanks, 2026)
            self.assertEqual(sum(v == 0 for row in board for v in row), blanks)
            self.assertEqual(board, sudoku_with_blanks(blanks, 2026))
            self.assertTrue(validate_solution(board, solved)['valid'])
        self.assertNotEqual(sudoku_with_blanks(45, 2026), sudoku_with_blanks(45, 2027))

    def test_benchmark_ignores_animation_and_reports_measured_rows(self):
        events = []
        result = run_experiment({'mode':'benchmark', 'algorithm':'sudoku',
            'bench_from':25, 'bench_to':45, 'bench_step':20, 'bench_samples':2,
            'trace':True, 'delay':0.5}, events.append)
        self.assertFalse(result['trace_enabled'])
        self.assertEqual(len(result['runs']), 4)
        self.assertEqual(result['summary']['largest_observed_success'], 45)
        self.assertTrue(all(row['successful'] == 2 for row in result['rows']))
        self.assertFalse(any(event['type'] == 'trace' for event in events))
        self.assertEqual(events[-1], result)

    def test_limits_are_observations_and_include_the_cause(self):
        result = run_benchmark({'algorithm':'sudoku','bench_from':45,'bench_to':45,
                               'bench_samples':1,'max_nodes':1}, lambda e: None)
        self.assertIsNone(result['summary']['largest_observed_success'])
        self.assertEqual(result['rows'][0]['budget_stops'], 1)
        self.assertIn('Node limit', result['runs'][0]['stop_reason'])
        self.assertEqual(result['rows'][0]['infeasible'], 0)

    def test_other_algorithms_and_single_tree_goal_distinction(self):
        for algorithm, first, last in [('golfers',1,3),('latin',1,3),('trees',0,3)]:
            result=run_benchmark({'algorithm':algorithm,'bench_from':first,'bench_to':last,
                'bench_step':2,'bench_samples':1,'groups':2,'players_per_group':2},lambda e:None)
            self.assertTrue(all(row['successful'] == 1 for row in result['rows']))
            if algorithm == 'trees':
                self.assertEqual(result['rows'][0]['goals_found'], 0)
                self.assertEqual(result['rows'][-1]['goals_found'], 1)

    def test_ranges_baselines_and_invalid_inputs(self):
        self.assertEqual(set(saved_baselines()), {'golfers','sudoku','latin','trees'})
        for params in [{'algorithm':'reference'}, {'algorithm':'sudoku','bench_from':50,'bench_to':40},
                       {'algorithm':'sudoku','bench_from':0,'bench_to':81,'bench_step':1},
                       {'algorithm':'trees','problem':'all'}, {'bench_seconds':float('nan')}]:
            with self.assertRaises(ValueError):
                run_benchmark(params,lambda e:None)
