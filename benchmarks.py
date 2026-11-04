"""Reproducible bounded measurements; empirical successes are not general limits."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import random
from statistics import median
from time import perf_counter

ROOT = Path(__file__).resolve().parent


def sudoku_with_blanks(blanks, seed=2026):
    if type(blanks) is not int or not 0 <= blanks <= 81:
        raise ValueError('Sudoku blanks must be an integer between 0 and 81.')
    board = [[(3*r + r//3 + c) % 9 + 1 for c in range(9)] for r in range(9)]
    for cell in random.Random(seed).sample(range(81), blanks):
        board[cell//9][cell%9] = 0
    return board


def saved_baselines():
    """Read prior measured cases, never convert them into runtime predictions."""
    result = {}
    for algorithm, filename in [('sudoku', 'sudoku.json'), ('golfers', 'golfers-32.json')]:
        content = json.loads((ROOT / 'results' / filename).read_text())
        result[algorithm] = [dict(value=run.get('empty_cells', run.get('problem', {}).get('weeks')),
                                  **run['stats'])
                             for run in content['runs']]
    result['latin'] = []
    for name in ['latin-3-classic.json', 'latin-5.json']:
        run = json.loads((ROOT / 'results' / name).read_text())
        result['latin'].append({'value': run['size'], 'symmetry_breaking': run['symmetry_breaking'],
                                **run['stats']})
    result['trees'] = [{'problem': tree['problem'], 'value': tree['max_depth'],
                        'truncated': tree['truncated'], **tree['stats']}
                       for tree in json.loads((ROOT / 'results/search-trees.json').read_text())]
    return result


def run_benchmark(params, emit):
    from demo_runner import number, run_experiment
    algorithm = params.get('algorithm', 'sudoku')
    limits = {'sudoku': (0, 81, 25, 65, 10, 'empty cells'),
              'golfers': (1, 20, 1, 7, 1, 'weeks'),
              'latin': (1, 7, 1, 6, 1, 'square size'),
              'trees': (0, 20, 0, 8, 2, 'depth limit')}
    if algorithm not in limits:
        raise ValueError('Choose a search algorithm to benchmark; reference verification is not search.')
    low, high, default_start, default_end, default_step, axis = limits[algorithm]
    first = number(params, 'bench_from', default_start, low, high)
    last = number(params, 'bench_to', default_end, low, high)
    step = number(params, 'bench_step', default_step, 1, 81)
    samples = number(params, 'bench_samples', 3 if algorithm == 'sudoku' else 1, 1, 5)
    seed = number(params, 'bench_seed', 2026, 0, 1000000)
    per_case = number(params, 'bench_seconds', 1, 0.01, 10, False)
    total_budget = number(params, 'bench_total_seconds', 20, 0.01, 100, False)
    if first > last:
        raise ValueError('The benchmark start must not exceed its end.')
    values = list(range(first, last+1, step))
    if values[-1] != last:
        values.append(last)
    if len(values)*samples > 60:
        raise ValueError('Use at most 60 trials. Increase the step or reduce the samples.')
    if algorithm == 'trees' and params.get('problem', '8-puzzle') == 'all':
        raise ValueError('Choose one tree problem when comparing depth limits.')
    start = perf_counter()
    runs = []
    rows = []
    emit({'type': 'start', 'algorithm': algorithm, 'message': 'Benchmark: tracing and animation disabled'})
    for value in values:
        observed = []
        for sample in range(samples):
            remaining = total_budget - (perf_counter()-start)
            if remaining < 0.01:
                break
            case = dict(params, mode='single', trace=False, delay=0, maximize=False,
                        time_limit=min(per_case, remaining))
            label = f'{value} {axis} · sample {sample+1}/{samples}'
            emit({'type': 'benchmark_progress', 'message': f'Measuring {label}',
                  'value': value, 'completed': len(runs), 'planned': len(values)*samples})
            if algorithm == 'sudoku':
                case.update(difficulty='custom', board=sudoku_with_blanks(value, seed+sample))
            elif algorithm == 'golfers':
                case['weeks'] = value
            elif algorithm == 'latin':
                case['size'] = value
            else:
                case['max_depth'] = value
            raw = run_experiment(case, lambda event: None)['runs'][0]
            stats = raw['stats']
            status = stats.get('status', raw.get('status'))
            if algorithm == 'trees':
                budget_hit = any(n['kind'] in ('time_limit', 'node_limit') for n in raw['tree']['nodes'])
                status = 'resource_limit' if budget_hit else 'completed_depth'
                success = not budget_hit
            else:
                success = status == 'solved' and bool(raw['validation'] and raw['validation']['valid'])
            measured = {'value': value, 'sample': sample+1, 'seed': seed+sample if algorithm == 'sudoku' else None,
                        'status': status, 'success': success,
                        'elapsed_seconds': stats['elapsed_seconds'],
                        'expanded_nodes': stats['expanded_nodes'],
                        'peak_frontier': stats.get('peak_frontier'),
                        'backtracks': stats.get('backtracks'),
                        'goal_found': bool(raw.get('tree', {}).get('solution_path')) if algorithm == 'trees' else success,
                        'effective_time_limit': case['time_limit'], 'result': raw}
            measured['stop_reason'] = raw.get('stop_reason')
            if algorithm == 'trees' and budget_hit:
                measured['stop_reason'] = 'Time limit reached.' if any(
                    n['kind'] == 'time_limit' for n in raw['tree']['nodes']) else 'Node limit reached.'
            observed.append(measured)
            runs.append(measured)
            emit({'type': 'benchmark_case', **{key: val for key, val in measured.items() if key != 'result'}})
        successful = [case for case in observed if case['success']]
        row = {'value': value, 'requested': samples, 'tested': len(observed), 'successful': len(successful),
               'budget_stops': sum(case['status'] == 'resource_limit' for case in observed),
               'stop_reasons': dict(Counter(case['stop_reason'] for case in observed if case['stop_reason'])),
               'infeasible': sum(case['status'] == 'infeasible' for case in observed),
               'goals_found': sum(case['goal_found'] for case in observed),
               'median_solved_seconds': median(case['elapsed_seconds'] for case in successful) if successful else None,
               'max_solved_seconds': max((case['elapsed_seconds'] for case in successful), default=None),
               'median_observed_seconds': median(case['elapsed_seconds'] for case in observed) if observed else None,
               'median_nodes': median(case['expanded_nodes'] for case in observed) if observed else None,
               'peak_frontier': max((case['peak_frontier'] or 0 for case in observed), default=0)}
        rows.append(row)
        emit({'type': 'benchmark_row', 'row': row, 'axis': axis})
    summary = {'largest_observed_success': max((row['value'] for row in rows if row['successful']), default=None),
               'largest_all_samples_successful': max((row['value'] for row in rows
                   if row['successful'] == row['requested']), default=None),
               'completed_trials': len(runs), 'planned_trials': len(values)*samples,
               'total_budget_exhausted': len(runs) < len(values)*samples,
               'wall_seconds': perf_counter()-start,
               'claim': 'Observed successes for these instances and budgets only; not a universal maximum or runtime prediction.'}
    result = {'type': 'result', 'mode': 'benchmark', 'algorithm': algorithm, 'axis': axis,
              'parameters': params, 'trace_enabled': False,
              'measurement': {'python': platform.python_version(), 'system': platform.system(),
                              'architecture': platform.machine(), 'checked_at_utc': datetime.now(timezone.utc).isoformat(),
                              'seconds_per_case': per_case, 'total_budget_seconds': total_budget,
                              'sudoku_generator': 'cyclic solved grid; sample blanks with random.Random(seed + sample_index)',
                              'uniqueness_tested': False},
              'rows': rows, 'runs': runs, 'summary': summary}
    emit(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--algorithm', choices=['sudoku','golfers','latin','trees'], default='sudoku')
    parser.add_argument('--from', dest='first', type=int)
    parser.add_argument('--to', dest='last', type=int)
    parser.add_argument('--step', type=int)
    parser.add_argument('--samples', type=int, default=3)
    parser.add_argument('--seconds', type=float, default=1)
    parser.add_argument('--total-seconds', type=float, default=20)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    params = {'algorithm': args.algorithm, 'bench_samples': args.samples,
              'bench_seconds': args.seconds, 'bench_total_seconds': args.total_seconds,
              'groups': 8, 'players_per_group': 4}
    for key, value in [('bench_from', args.first), ('bench_to', args.last), ('bench_step', args.step)]:
        if value is not None:
            params[key] = value
    def emit(event):
        if event['type'] == 'benchmark_row':
            row = event['row']
            print(f"{row['value']} {event['axis']}: {row['successful']}/{row['tested']} within budget; "
                  f"median successful time={row['median_solved_seconds']}", flush=True)
    try:
        result = run_benchmark(params, emit)
        print(json.dumps(result['summary'], indent=2))
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2)+'\n')
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
