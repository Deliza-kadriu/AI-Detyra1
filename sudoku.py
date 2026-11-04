"""Sudoku using FIFO breadth-first search with constraint rejection."""

import argparse
from collections import deque
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import platform
from time import perf_counter

Board = tuple[tuple[int, ...], ...]
DIFFICULTIES = ("easy", "medium", "hard")
FIXTURES = Path(__file__).with_name("data") / "sudoku.json"


def validate_board_shape(board: Board) -> None:
    if (not isinstance(board, (list, tuple)) or len(board) != 9
            or any(not isinstance(row, (list, tuple)) or len(row) != 9 for row in board)):
        raise ValueError("Sudoku requires a 9 by 9 board.")
    if any(type(value) is not int or not 0 <= value <= 9
           for row in board for value in row):
        raise ValueError("Cells must be integers 0..9; zero means unassigned.")


def landscape(board: Board) -> int:
    """Raw complete assignments, before row/column/box constraints."""
    validate_board_shape(board)
    return 9 ** sum(value == 0 for row in board for value in row)


def _consistent(board: Board) -> bool:
    units = list(board) + [tuple(board[r][c] for r in range(9)) for c in range(9)]
    units += [tuple(board[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3))
              for br in (0, 3, 6) for bc in (0, 3, 6)]
    return all(len([v for v in unit if v]) == len({v for v in unit if v}) for unit in units)


@dataclass
class SudokuStats:
    expanded_nodes: int = 0  # Boards removed from the FIFO queue, including goal.
    generated_nodes: int = 0  # Boards enqueued, including the initial board.
    rejected_candidates: int = 0
    dead_ends: int = 0
    peak_frontier: int = 0
    max_depth: int = 0  # Initially empty cells assigned, not recursive call depth.
    elapsed_seconds: float = 0.0
    status: str = "pending"


class SudokuLimitReached(RuntimeError):
    """The resource budget was exhausted; feasibility remains unknown."""


def solve_bfs(board: Board, *, max_nodes: int | None = None,
              max_frontier: int | None = None, time_limit: float | None = None,
              stats: SudokuStats | None = None, trace=None) -> Board | None:
    """First solution, None after exhaustion, or SudokuLimitReached on a limit.

    Cells follow fixed row-major order and digits ascend 1..9. Every successor
    assigns exactly one cell. Independent immutable states allow failed branches
    to be discarded while alternatives remain in the FIFO queue.
    """
    validate_board_shape(board)
    board = tuple(tuple(row) for row in board)
    if not _consistent(board):
        raise ValueError("Initial clues conflict in a row, column or 3x3 box.")
    for name, limit in (("max_nodes", max_nodes), ("max_frontier", max_frontier)):
        if limit is not None and (type(limit) is not int or limit < 1):
            raise ValueError(f"{name} must be a positive integer.")
    if time_limit is not None and not 0 < time_limit < float("inf"):
        raise ValueError("time_limit must be positive and finite.")
    stats = stats if stats is not None else SudokuStats()
    for key, value in asdict(SudokuStats()).items():
        setattr(stats, key, value)
    stats.status = "running"
    empty = [(r, c) for r in range(9) for c in range(9) if board[r][c] == 0]
    queue = deque([(board, 0)])
    stats.generated_nodes = stats.peak_frontier = 1
    start = perf_counter()

    def check_time():
        if time_limit is not None and perf_counter() - start >= time_limit:
            raise SudokuLimitReached("Time limit reached; feasibility is unknown.")

    try:
        while queue:
            check_time()
            if max_nodes is not None and stats.expanded_nodes >= max_nodes:
                raise SudokuLimitReached("Node limit reached; feasibility is unknown.")
            state, depth = queue.popleft()
            stats.expanded_nodes += 1
            stats.max_depth = max(stats.max_depth, depth)
            if trace:
                trace({'message': f'DEQUEUE depth {depth}; {len(queue)} boards remain in FIFO queue',
                       'board': state, 'depth': depth})
            if depth == len(empty):
                stats.status = "solved"
                return state
            r, c = empty[depth]
            used = set(state[r]) | {state[i][c] for i in range(9)}
            used |= {state[i][j] for i in range(r // 3 * 3, r // 3 * 3 + 3)
                     for j in range(c // 3 * 3, c // 3 * 3 + 3)}
            children = 0
            for digit in range(1, 10):
                check_time()
                if digit in used:
                    stats.rejected_candidates += 1
                    continue
                if max_frontier is not None and len(queue) >= max_frontier:
                    raise SudokuLimitReached("Frontier limit reached; feasibility is unknown.")
                row = state[r][:c] + (digit,) + state[r][c + 1:]
                child = state[:r] + (row,) + state[r + 1:]
                queue.append((child, depth + 1))
                children += 1
                stats.generated_nodes += 1
                stats.peak_frontier = max(stats.peak_frontier, len(queue))
                if trace:
                    trace({'message': f'ENQUEUE r{r+1}c{c+1} = {digit}; depth {depth+1}',
                           'board': child, 'depth': depth+1, 'cell': [r, c]})
            if not children:
                stats.dead_ends += 1
                if trace:
                    trace({'message': 'DEAD END: no legal digit; discard this branch',
                           'board': state, 'depth': depth})
        stats.status = "infeasible"
        return None
    except SudokuLimitReached:
        stats.status = "resource_limit"
        raise
    finally:
        stats.elapsed_seconds = perf_counter() - start


def load_examples() -> dict:
    return json.loads(FIXTURES.read_text())["puzzles"]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument("--difficulty", choices=(*DIFFICULTIES, "all"), default="all")
    inputs.add_argument("--board-file", type=Path, help="JSON 9x9 array; zero means empty")
    parser.add_argument("--max-nodes", type=int, default=200_000)
    parser.add_argument("--max-frontier", type=int, default=50_000)
    parser.add_argument("--time-limit", type=float, default=10.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    from validate_sudoku import validate_solution
    try:
        if args.board_file:
            examples = {"custom": json.loads(args.board_file.read_text())}
        else:
            examples = load_examples()
            if args.difficulty != "all":
                examples = {args.difficulty: examples[args.difficulty]}
        runs = []
        for name, board in examples.items():
            stats = SudokuStats()
            solution = None
            try:
                solution = solve_bfs(board, max_nodes=args.max_nodes,
                                     max_frontier=args.max_frontier,
                                     time_limit=args.time_limit, stats=stats)
            except SudokuLimitReached as exc:
                print(f"{name}: {exc}")
            validation = validate_solution(board, solution) if solution is not None else None
            if validation is not None and not validation["valid"]:
                raise RuntimeError(f"Invalid solver output: {validation}")
            runs.append({"difficulty": name, "input": board,
                         "empty_cells": sum(v == 0 for row in board for v in row),
                         "landscape": landscape(board), "stats": asdict(stats),
                         "solution": solution, "validation": validation})
            print(f"{name}: {stats.status}; {stats.expanded_nodes} expanded; "
                  f"peak frontier {stats.peak_frontier}; {stats.elapsed_seconds:.4f}s")
            if solution is not None:
                for row in solution:
                    print(" ".join(map(str, row)))
                print("Independent validation: PASS")
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps({"algorithm": "FIFO BFS with constraint rejection",
                "python_version": platform.python_version(),
                "limits": {"max_nodes": args.max_nodes, "max_frontier": args.max_frontier,
                           "time_limit_seconds": args.time_limit}, "runs": runs}, indent=2) + "\n")
    except (ValueError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
