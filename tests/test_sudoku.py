import copy
import unittest

from sudoku import (SudokuLimitReached, SudokuStats, landscape, load_examples,
                    solve_bfs, validate_board_shape)
from validate_sudoku import validate_solution


class SudokuTests(unittest.TestCase):
    def test_examples_preserve_clues_and_input(self):
        for name, board in load_examples().items():
            with self.subTest(difficulty=name):
                original = copy.deepcopy(board)
                stats = SudokuStats()
                solution = solve_bfs(board, max_nodes=100_000, stats=stats)
                checked = validate_solution(board, solution)
                self.assertTrue(checked['valid'], checked)
                self.assertEqual(checked['objective'], 0)
                self.assertEqual(board, original)
                self.assertEqual(stats.status, 'solved')
                self.assertEqual(stats.max_depth, sum(v == 0 for row in board for v in row))
                self.assertGreater(stats.peak_frontier, 1)
                self.assertGreater(stats.dead_ends, 0)

    def test_solved_board_and_one_empty_cell(self):
        solved = solve_bfs(load_examples()['easy'])
        stats = SudokuStats()
        self.assertEqual(solve_bfs(solved, max_nodes=1, stats=stats), solved)
        self.assertEqual(stats.expanded_nodes, 1)
        self.assertEqual(stats.max_depth, 0)
        partial = [list(row) for row in solved]
        partial[8][8] = 0
        self.assertEqual(solve_bfs(partial), solved)
        self.assertEqual(landscape(partial), 9)

    def test_consistent_but_impossible_board(self):
        board = [[0] * 9 for _ in range(9)]
        board[0] = [1, 2, 3, 4, 5, 6, 7, 8, 0]
        board[1][8] = 9  # No duplicate clues; first empty cell has no legal digit.
        stats = SudokuStats()
        self.assertIsNone(solve_bfs(board, stats=stats))
        self.assertEqual(stats.status, 'infeasible')
        self.assertEqual(stats.dead_ends, 1)

    def test_conflicting_clues(self):
        for first, second in [((0, 0), (0, 8)), ((0, 0), (8, 0)), ((0, 0), (1, 1))]:
            board = [[0] * 9 for _ in range(9)]
            for r, c in (first, second):
                board[r][c] = 1
            with self.assertRaises(ValueError):
                solve_bfs(board)

    def test_limits_are_not_infeasibility(self):
        for limits in ({'max_nodes': 1}, {'max_frontier': 1}, {'time_limit': 1e-12}):
            stats = SudokuStats()
            with self.assertRaises(SudokuLimitReached):
                solve_bfs(load_examples()['hard'], stats=stats, **limits)
            self.assertEqual(stats.status, 'resource_limit')

    def test_malformed_inputs_and_limits(self):
        for board in (None, [], [[0] * 8] * 9, [[True] * 9] * 9,
                      [[10] * 9] * 9, [['0'] * 9] * 9):
            with self.assertRaises(ValueError):
                validate_board_shape(board)
        for limits in ({'max_nodes': 0}, {'max_frontier': True}, {'time_limit': float('nan')}):
            with self.assertRaises(ValueError):
                solve_bfs(load_examples()['easy'], **limits)

    def test_validator_detects_boxes_clue_changes_and_incomplete_boards(self):
        empty = [[0] * 9 for _ in range(9)]
        latin = [[(r + c) % 9 + 1 for c in range(9)] for r in range(9)]
        result = validate_solution(empty, latin)
        self.assertFalse(result['valid'])
        self.assertTrue(any('Box' in error for error in result['errors']))
        board = load_examples()['easy']
        solved = solve_bfs(board)
        shifted = [[v % 9 + 1 for v in row] for row in solved]
        self.assertIn('A fixed clue was changed.', validate_solution(board, shifted)['errors'])
        self.assertFalse(validate_solution(board, board)['valid'])
        self.assertFalse(validate_solution(board, None)['valid'])


if __name__ == '__main__':
    unittest.main()
