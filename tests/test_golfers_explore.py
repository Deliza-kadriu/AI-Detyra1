import unittest

from demo_runner import run_experiment
from golfers_explore import ExploreStats, solve_explore
from social_golfers import GolfersProblem
from validate_golfers import validate_schedule


class ExploreTests(unittest.TestCase):
    def test_structured_reaches_nine_without_loading_reference(self):
        # No fixture/result file is available to the algorithm; all choices are generated.
        from unittest.mock import patch
        with patch('pathlib.Path.read_text',side_effect=AssertionError('Must not load a schedule')):
            stats=ExploreStats()
            result=solve_explore(GolfersProblem(8,4,9),strategy='structured',max_nodes=5000,stats=stats)
        self.assertEqual(stats.status,'solved')
        self.assertEqual(len(result),9)
        self.assertTrue(validate_schedule(result,8,4,9)['valid'])

    def test_partial_best_is_preserved_and_target_not_claimed(self):
        events=[]
        result=run_experiment({'algorithm':'golfers','groups':8,'players_per_group':4,
            'weeks':10,'strategy':'structured','max_nodes':10000,'trace':False},events.append)
        run=result['runs'][0]
        self.assertEqual(run['weeks'],9)
        self.assertFalse(run['target_reached'])
        self.assertEqual(run['stats']['status'],'resource_limit')
        self.assertEqual(result['summary']['best_weeks_found'],9)
        self.assertFalse(result['summary']['maximum_proven'])
        best_events=[e for e in events if e['type']=='best']
        self.assertEqual([e['weeks'] for e in best_events],list(range(1,10)))
        for event in best_events:
            self.assertTrue(validate_schedule(event['schedule'],8,4,event['weeks'])['valid'])

    def test_restart_mode_solves_small_cases_and_exhausts_impossible_target(self):
        for g,p,w in [(2,2,3),(3,2,5),(2,1,4)]:
            stats=ExploreStats()
            result=solve_explore(GolfersProblem(g,p,w),stats=stats)
            self.assertTrue(validate_schedule(result,g,p,w)['valid'])
            self.assertEqual(stats.status,'solved')
        stats=ExploreStats()
        result=solve_explore(GolfersProblem(2,3,2),stats=stats)
        self.assertEqual(stats.status,'infeasible')
        self.assertTrue(validate_schedule(result,2,3,1)['valid'])

    def test_global_budget_and_reproducibility(self):
        results=[]
        for _ in range(2):
            stats=ExploreStats()
            results.append(solve_explore(GolfersProblem(8,4,10),max_nodes=1000,restart_nodes=100,stats=stats))
            self.assertEqual(stats.expanded_nodes,1000)
            self.assertGreater(stats.restarts,0)
            self.assertTrue(validate_schedule(results[-1],8,4,len(results[-1]))['valid'])
        self.assertEqual(results[0],results[1])

    def test_invalid_options_and_bound(self):
        for options in [{'strategy':'unknown'},{'seed':-1},{'restart_nodes':0},{'time_limit':0}]:
            with self.assertRaises(ValueError):
                solve_explore(GolfersProblem(),**options)
        with self.assertRaises(ValueError):
            solve_explore(GolfersProblem(2,2,3),strategy='structured')
        stats=ExploreStats()
        self.assertIsNone(solve_explore(GolfersProblem(8,4,11),stats=stats))
        self.assertEqual(stats.status,'infeasible')
