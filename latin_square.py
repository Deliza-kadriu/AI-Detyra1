"""Latin Square using iterative deepening and depth-limited backtracking."""

import argparse
from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from time import perf_counter

Square = tuple[tuple[int, ...], ...]


def landscape(size: int) -> int:
    if type(size) is not int or size < 1:
        raise ValueError("Square size must be a positive integer.")
    return size ** (size * size)


@dataclass
class LatinStats:
    expanded_nodes: int = 0
    backtracks: int = 0
    max_depth: int = 0
    elapsed_seconds: float = 0.0
    status: str = "pending"
    iterations: list = field(default_factory=list)


class LatinLimitReached(RuntimeError):
    pass


def solve_iddfs(size: int, *, max_nodes: int | None = None,
                time_limit: float | None = None, goal_depth_pruning: bool = False,
                symmetry_breaking: bool = True,
                stats: LatinStats | None = None, trace=None) -> Square | None:
    """Try increasing depth limits with a fresh depth-limited DFS each time.

    Set goal_depth_pruning=False to demonstrate classic IDDFS's repeated work.
    By default, fix the first row and column to 1..n by symmetry. Disable this
    to explore all n*n cells. Optional goal-depth pruning skips shallow trees.
    """
    landscape(size)
    if max_nodes is not None and (type(max_nodes) is not int or max_nodes < 1):
        raise ValueError("max_nodes must be a positive integer.")
    if time_limit is not None and not 0 < time_limit < float('inf'):
        raise ValueError("time_limit must be positive and finite.")
    stats = stats if stats is not None else LatinStats()
    stats.expanded_nodes = stats.backtracks = stats.max_depth = 0
    stats.iterations = []
    stats.status = 'running'
    start = perf_counter()
    try:
        for limit in range(size * size + 1):
            board = [[0] * size for _ in range(size)]
            rows = [set() for _ in range(size)]
            cols = [set() for _ in range(size)]
            if symmetry_breaking:
                for r in range(size):
                    for c in range(size):
                        if r == 0 or c == 0:
                            board[r][c] = r + c + 1
                            rows[r].add(board[r][c])
                            cols[c].add(board[r][c])
            cells = [(r, c) for r in range(size) for c in range(size) if not board[r][c]]
            if limit > len(cells):
                break
            iteration = {'limit': limit, 'nodes': 0, 'outcome': 'running'}
            stats.iterations.append(iteration)
            if trace:
                trace({'message': f'ITERATION: restart depth-limited DFS with limit {limit}',
                       'board': board, 'depth': 0, 'limit': limit})

            def dls(depth):
                if max_nodes is not None and stats.expanded_nodes >= max_nodes:
                    raise LatinLimitReached('Node limit reached; search unfinished.')
                if time_limit is not None and perf_counter() - start >= time_limit:
                    raise LatinLimitReached('Time limit reached; search unfinished.')
                stats.expanded_nodes += 1
                iteration['nodes'] += 1
                stats.max_depth = max(stats.max_depth, depth)
                if depth == len(cells):
                    return True
                if depth == limit or (goal_depth_pruning and limit < len(cells)):
                    return False
                r, c = cells[depth]
                for digit in range(1, size + 1):
                    if digit in rows[r] or digit in cols[c]:
                        continue
                    board[r][c] = digit
                    rows[r].add(digit)
                    cols[c].add(digit)
                    if trace:
                        trace({'message': f'ASSIGN r{r+1}c{c+1} = {digit}; depth {depth+1}/{limit}',
                               'board': board, 'cell': [r, c], 'depth': depth+1, 'limit': limit})
                    if dls(depth + 1):
                        return True
                    board[r][c] = 0
                    rows[r].remove(digit)
                    cols[c].remove(digit)
                    stats.backtracks += 1
                    if trace:
                        trace({'message': f'BACKTRACK: clear r{r+1}c{c+1}',
                               'board': board, 'cell': [r, c], 'depth': depth, 'limit': limit})
                return False

            if dls(0):
                iteration['outcome'] = 'solved'
                stats.status = 'solved'
                return tuple(tuple(row) for row in board)
            iteration['outcome'] = 'cutoff' if limit < len(cells) else 'exhausted'
        stats.status = 'infeasible'
        return None
    except LatinLimitReached:
        stats.status = 'resource_limit'
        if stats.iterations:
            stats.iterations[-1]['outcome'] = 'resource_limit'
        raise
    finally:
        stats.elapsed_seconds = perf_counter() - start


def main(argv=None):
    from validate_latin import validate_square
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--size', type=int, default=5)
    parser.add_argument('--literal-deepening', action='store_true',
                        help='disable symmetry reduction and explore all cells; use small n')
    parser.add_argument('--goal-depth-pruning', action='store_true',
                        help='optionally skip trees too shallow to contain a complete square')
    parser.add_argument('--max-nodes', type=int, default=1_000_000)
    parser.add_argument('--time-limit', type=float, default=10)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    stats = LatinStats()
    square = None
    try:
        try:
            square = solve_iddfs(args.size, max_nodes=args.max_nodes,
                                 time_limit=args.time_limit,
                                 goal_depth_pruning=args.goal_depth_pruning,
                                 symmetry_breaking=not args.literal_deepening, stats=stats)
        except LatinLimitReached as exc:
            print(exc)
        validation = validate_square(square, args.size) if square is not None else None
        if validation is not None and not validation['valid']:
            raise RuntimeError(validation)
        print(f'{stats.status}: {stats.expanded_nodes} nodes; {stats.backtracks} backtracks')
        if square is not None:
            for row in square:
                print(' '.join(map(str, row)))
            print('Independent validation: PASS')
        result = {'size': args.size, 'algorithm': 'IDDFS with backtracking',
                  'goal_depth_pruning': args.goal_depth_pruning,
                  'symmetry_breaking': not args.literal_deepening,
                  'limits': {'max_nodes': args.max_nodes, 'time_limit': args.time_limit},
                  'landscape': landscape(args.size), 'stats': asdict(stats),
                  'square': square, 'validation': validation}
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2) + '\n')
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
