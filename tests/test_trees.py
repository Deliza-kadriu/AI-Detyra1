import copy
from itertools import product
import unittest

from search_trees.generate import build_tree, render_markdown
from search_trees.problems import workforce_error
from validate_trees import validate_path


class TreeTests(unittest.TestCase):
    def test_paths_and_node_links(self):
        for name, length in [('8-puzzle', 2), ('missionaries', 11), ('workforce', 6)]:
            tree = build_tree(name)
            self.assertTrue(validate_path(tree)['valid'])
            self.assertEqual(len(tree['solution_path']) - 1, length)
            for node in tree['nodes'][1:]:
                self.assertLess(node['parent'], node['id'])
                self.assertEqual(node['depth'], tree['nodes'][node['parent']]['depth'] + 1)
                if node['kind'] == 'repeated':
                    self.assertEqual(node['state'], tree['nodes'][node['repeat_of']]['state'])
            self.assertTrue(any(n['rejections'] for n in tree['nodes']))
        self.assertTrue(build_tree('8-puzzle')['truncated'])
        self.assertFalse(build_tree('workforce')['truncated'])
        self.assertTrue(any(n['kind'] == 'repeated' for n in build_tree('missionaries')['nodes']))

    def test_truncation_and_renderer(self):
        for limits in [{'max_depth': 0}, {'max_nodes': 1}, {'time_limit': 1e-12}]:
            tree = build_tree('8-puzzle', **limits)
            self.assertTrue(tree['truncated'])
            self.assertEqual(tree['solution_path'], [])
            self.assertFalse(validate_path(tree)['valid'])
            self.assertIn('No goal found', render_markdown([tree]))
        with self.assertRaises(ValueError):
            build_tree('workforce', max_nodes=0)

    def test_validator_rejects_broken_paths(self):
        for name in ['8-puzzle', 'missionaries', 'workforce']:
            tree = copy.deepcopy(build_tree(name))
            tree['nodes'][tree['solution_path'][-1]]['parent'] = None
            self.assertFalse(validate_path(tree)['valid'])

    def test_workforce_pruning_matches_complete_rosters(self):
        # Exhaustively compare all 729 base patterns against independent roster checks.
        for pattern in product(('D', 'N', 'O'), repeat=6):
            tree = {'problem': 'workforce', 'solution_path': list(range(7)),
                    'nodes': [{'id': d, 'parent': d-1 if d else None,
                               'depth': d, 'state': pattern[:d]} for d in range(7)]}
            independent = validate_path(tree)['valid']
            self.assertEqual(workforce_error(pattern) is None, independent)
            if independent:
                for depth in range(7):
                    self.assertIsNone(workforce_error(pattern[:depth]))
