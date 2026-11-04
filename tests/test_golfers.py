import unittest

from social_golfers import GolfersProblem, SearchLimitReached, SearchStats, solve_dfs
from validate_golfers import validate_schedule


class GolfersTests(unittest.TestCase):
    def test_trace_reports_search_and_does_not_change_result(self):
        messages = []
        problem = GolfersProblem(3, 2, 5)
        self.assertEqual(solve_dfs(problem, trace=messages.append), solve_dfs(problem))
        for event in ("ASSIGN", "REJECT", "BACKTRACK", "GOAL"):
            self.assertTrue(any(message.startswith(event) for message in messages), event)
        messages.clear()
        self.assertIsNone(solve_dfs(GolfersProblem(2, 2, 7), trace=messages.append))
        self.assertEqual(len(messages), 1)
        self.assertTrue(messages[0].startswith("BOUND"))

    def test_feasible_cases(self):
        for g, p, w in [(2, 2, 3), (3, 2, 5), (3, 3, 4), (8, 4, 2), (2, 1, 5), (1, 4, 1)]:
            with self.subTest(g=g, p=p, w=w):
                stats = SearchStats()
                result = solve_dfs(GolfersProblem(g, p, w), max_nodes=500_000, stats=stats)
                self.assertTrue(validate_schedule(result, g, p, w)["valid"])
                self.assertEqual(stats.status, "solved")
                if (g, p, w) == (3, 2, 5):
                    self.assertGreater(stats.backtracks, 0)

    def test_exhaustion_below_pair_bound(self):
        # Two triples cannot be repartitioned without repeating a pair.
        stats = SearchStats()
        self.assertIsNone(solve_dfs(GolfersProblem(2, 3, 2), stats=stats))
        self.assertEqual(stats.status, "infeasible")
        self.assertGreater(stats.backtracks, 0)

    def test_bound_and_limit_are_distinct(self):
        self.assertIsNone(solve_dfs(GolfersProblem(8, 4, 11)))
        stats = SearchStats()
        with self.assertRaises(SearchLimitReached):
            solve_dfs(GolfersProblem(), max_nodes=1, stats=stats)
        self.assertEqual(stats.status, "resource_limit")

    def test_validator_rejects_corrupt_schedules(self):
        valid = solve_dfs(GolfersProblem(2, 2, 3))
        self.assertFalse(validate_schedule([valid[0]] * 3, 2, 2, 3)["valid"])
        valid[0][0][0] = valid[0][0][1]
        self.assertFalse(validate_schedule(valid, 2, 2, 3)["valid"])
        self.assertFalse(validate_schedule(None, 2, 2, 3)["valid"])

    def test_parameters_and_landscape(self):
        for params in [(0, 4, 2), (2, -1, 2), (True, 4, 2), (2, 2, 1.5)]:
            with self.assertRaises(ValueError):
                GolfersProblem(*params)
        self.assertEqual(GolfersProblem(2, 2, 2).landscape(), 9)
        self.assertIsNone(GolfersProblem(2, 1, 5).week_upper_bound())
        with self.assertRaises(ValueError):
            solve_dfs(GolfersProblem(), time_limit=0)


if __name__ == "__main__":
    unittest.main()
