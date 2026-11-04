"""Run one UI experiment in an isolated process and emit JSON events."""

from dataclasses import asdict
import json
from pathlib import Path
import sys
from time import sleep


def number(params, key, default, low, high, integer=True):
    value = params.get(key, default)
    if type(value) not in (int, float) or (integer and type(value) is not int) or not low <= value <= high:
        raise ValueError(f'{key} must be {"an integer" if integer else "a number"} between {low} and {high}.')
    return value


def run_experiment(params, emit):
    if params.get('mode') == 'benchmark':
        from benchmarks import run_benchmark
        return run_benchmark(params, emit)
    from social_golfers import GolfersProblem, SearchStats, SearchLimitReached, solve_dfs
    from sudoku import SudokuStats, SudokuLimitReached, load_examples, solve_bfs
    from latin_square import LatinStats, LatinLimitReached, solve_iddfs
    from search_trees.generate import build_tree
    from validate_golfers import validate_schedule
    from validate_sudoku import validate_solution
    from validate_latin import validate_square
    from validate_trees import validate_path

    algorithm = params.get('algorithm', 'golfers')
    seconds = number(params, 'time_limit', 30, 0.01, 120, False)
    max_nodes = number(params, 'max_nodes', 200000, 1, 2000000)
    delay = number(params, 'delay', 0, 0, 0.5, False)
    traced = params.get('trace', True)
    if type(traced) is not bool:
        raise ValueError('trace must be true or false.')
    emit({'type': 'start', 'algorithm': algorithm, 'message': 'Experiment started'})
    runs = []

    trace_count = 0

    def callback(stats=None, context=None):
        if not traced:
            return None
        def trace(event):
            nonlocal trace_count
            trace_count += 1
            if trace_count > 5000:
                if trace_count == 5001:
                    emit({'type': 'trace', 'message': 'TRACE LIMIT: 5,000 steps shown; search continues without trace pauses.'})
                return
            payload = {'message': event} if isinstance(event, str) else dict(event)
            if stats:
                payload['stats'] = {key: value for key, value in vars(stats).items()
                                    if isinstance(value, (int, float, str))}
            emit({'type': 'trace', **(context or {}), **payload})
            if delay:
                sleep(delay)
        return trace

    if algorithm == 'golfers':
        g = number(params, 'groups', 3, 1, 16)
        p = number(params, 'players_per_group', 2, 1, 8)
        w = number(params, 'weeks', 5, 1, 20)
        if g*p > 64:
            raise ValueError('Use at most 64 players in the demonstration UI.')
        base = GolfersProblem(g, p, w)
        bound = base.week_upper_bound()
        target = min(w, bound) if bound is not None else w
        best = 0
        maximum = False
        for weeks in (range(1, target+1) if params.get('maximize', False) else [w]):
            stats = SearchStats()
            solution = None
            stop_reason = None
            try:
                solution = solve_dfs(GolfersProblem(g, p, weeks), max_nodes=max_nodes,
                                     time_limit=seconds, stats=stats, trace=callback(stats))
            except SearchLimitReached as exc:
                stop_reason = str(exc)
            validation = validate_schedule(solution, g, p, weeks) if solution is not None else None
            run = {'weeks': weeks, 'schedule': solution, 'stats': asdict(stats),
                   'stop_reason': stop_reason, 'validation': validation}
            runs.append(run)
            emit({'type': 'case', 'algorithm': algorithm, **run})
            if solution is not None:
                best = weeks
                maximum = bound is not None and weeks == bound
            else:
                maximum = bool(params.get('maximize') and best and stats.status == 'infeasible')
                break
        summary = {'best_weeks_found': best, 'pair_counting_upper_bound': bound,
                   'maximum_proven': maximum}
    elif algorithm == 'sudoku':
        examples = load_examples()
        level = params.get('difficulty', 'easy')
        if level == 'custom':
            selected = {'custom': params.get('board')}
        elif level == 'all':
            selected = examples
        elif level in examples:
            selected = {level: examples[level]}
        else:
            raise ValueError('Unknown Sudoku difficulty.')
        frontier = number(params, 'max_frontier', 50000, 1, 50000)
        for level, board in selected.items():
            emit({'type': 'case_start', 'algorithm': algorithm, 'name': level, 'input': board})
            stats = SudokuStats()
            solution = None
            stop_reason = None
            try:
                solution = solve_bfs(board, max_nodes=max_nodes, max_frontier=frontier,
                                     time_limit=seconds, stats=stats,
                                     trace=callback(stats, {'case': level}))
            except SudokuLimitReached as exc:
                stop_reason = str(exc)
            validation = validate_solution(board, solution) if solution is not None else None
            run = {'difficulty': level, 'input': board, 'solution': solution,
                   'stats': asdict(stats), 'stop_reason': stop_reason, 'validation': validation}
            runs.append(run)
            emit({'type': 'case', 'algorithm': algorithm, **run})
        summary = {'cases': len(runs)}
    elif algorithm == 'latin':
        n = number(params, 'size', 4, 1, 7)
        stats = LatinStats()
        solution = None
        stop_reason = None
        try:
            solution = solve_iddfs(n, max_nodes=max_nodes, time_limit=seconds, stats=stats,
                                  symmetry_breaking=params.get('symmetry', True),
                                  goal_depth_pruning=params.get('goal_depth_pruning', False),
                                  trace=callback(stats))
        except LatinLimitReached as exc:
            stop_reason = str(exc)
        validation = validate_square(solution, n) if solution is not None else None
        run = {'size': n, 'square': solution, 'stats': asdict(stats),
               'stop_reason': stop_reason, 'validation': validation}
        runs.append(run)
        emit({'type': 'case', 'algorithm': algorithm, **run})
        summary = {'size': n}
    elif algorithm == 'trees':
        choice = params.get('problem', '8-puzzle')
        if choice not in ('all', '8-puzzle', 'missionaries', 'workforce'):
            raise ValueError('Unknown tree problem.')
        depth = params.get('max_depth')
        if depth is not None:
            number(params, 'max_depth', 3, 0, 20)
        for name in (['8-puzzle', 'missionaries', 'workforce'] if choice == 'all' else [choice]):
            tree = build_tree(name, max_depth=depth, max_nodes=min(max_nodes, 5000),
                              time_limit=seconds,
                              trace=callback(context={'problem': name}))
            validation = validate_path(tree)
            tree['validation'] = validation
            run = {'tree': tree, 'stats': tree['stats'], 'validation': validation,
                   'status': 'solved' if tree['solution_path'] else 'no_goal_within_limits'}
            runs.append(run)
            emit({'type': 'case', 'algorithm': algorithm, **run})
        summary = {'cases': len(runs)}
    elif algorithm == 'reference':
        from golfers_reference import ROOT, verify_reference
        data = json.loads((ROOT / 'data/golfers-10-reference.json').read_text())
        checked = verify_reference(data)
        trace = callback()
        if trace:
            trace('REFERENCE: validate published schedule; this does not run DFS')
        run = {'schedule': data['schedule'], 'weeks': 10, 'validation': checked['validation'],
               'source_url': data['source_url'], 'stats': {'status': 'verified_reference'}}
        runs.append(run)
        emit({'type': 'case', 'algorithm': algorithm, **run})
        summary = checked
    else:
        raise ValueError('Unknown algorithm.')
    for run in runs:
        if run.get('validation') is not None and not run['validation']['valid']:
            if algorithm != 'trees' or run['tree']['solution_path']:
                raise RuntimeError('Independent result validation failed.')
    result = {'type': 'result', 'algorithm': algorithm, 'parameters': params,
              'runs': runs, 'summary': summary}
    emit(result)
    return result


def main():
    def emit(event):
        print(json.dumps(event), flush=True)
    try:
        params = json.loads(sys.stdin.readline())
        if not isinstance(params, dict):
            raise ValueError('Expected an experiment object.')
        run_experiment(params, emit)
    except Exception as exc:
        emit({'type': 'error', 'message': str(exc), 'status': 'error'})
        raise SystemExit(1)


if __name__ == '__main__':
    main()
