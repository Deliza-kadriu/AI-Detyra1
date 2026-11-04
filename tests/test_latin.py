import unittest

from latin_square import LatinLimitReached, LatinStats, landscape, solve_iddfs
from validate_latin import validate_square


class LatinTests(unittest.TestCase):
    def test_sizes_and_classic_deepening(self):
        for n, prune in [(1, False), (2, False), (3, False), (4, True), (5, True)]:
            stats = LatinStats()
            square = solve_iddfs(n, symmetry_breaking=prune, max_nodes=100_000, stats=stats)
            self.assertTrue(validate_square(square, n)['valid'])
            depth = (n-1)**2 if prune else n*n
            self.assertEqual([i['limit'] for i in stats.iterations], list(range(depth+1)))
            self.assertEqual(stats.max_depth, depth)
            self.assertEqual(stats.status, 'solved')
            if not prune and n > 1:
                self.assertGreater(stats.iterations[-2]['nodes'], 1)
                self.assertGreater(stats.backtracks, 0)

    def test_shortcut_preserves_solution(self):
        a, b = LatinStats(), LatinStats()
        self.assertEqual(solve_iddfs(3, goal_depth_pruning=True, stats=a), solve_iddfs(3, stats=b))
        self.assertLess(a.expanded_nodes, b.expanded_nodes)

    def test_limits_and_inputs(self):
        for limits in [{'max_nodes': 1}, {'time_limit': 1e-12}]:
            stats = LatinStats()
            with self.assertRaises(LatinLimitReached):
                solve_iddfs(5, stats=stats, **limits)
            self.assertEqual(stats.status, 'resource_limit')
        for size in [0, -1, True, 1.5]:
            with self.assertRaises(ValueError):
                landscape(size)
        self.assertEqual(landscape(5), 298023223876953125)

    def test_validator_rejects_corruption(self):
        self.assertFalse(validate_square([[1, 1], [2, 2]], 2)['valid'])
        self.assertFalse(validate_square([[1, 2], [1, 2]], 2)['valid'])
        self.assertFalse(validate_square(None, 2)['valid'])
