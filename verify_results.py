"""Revalidate every saved solution using independent constraint checkers."""

import json
from pathlib import Path
from golfers_reference import verify_reference

from validate_golfers import validate_schedule
from validate_latin import validate_square
from validate_sudoku import validate_solution
from validate_trees import validate_path


def main():
    results = Path(__file__).with_name('results')
    count = 0

    def check(label, result):
        nonlocal count
        if not result['valid']:
            raise ValueError(f'{label}: {result}')
        count += 1
        print(f'{label}: PASS')

    golf = json.loads((results / 'golfers-32.json').read_text())
    for run in golf['runs']:
        p = run['problem']
        if run['schedule'] is not None:
            check(f"Golfers {p['weeks']} weeks", validate_schedule(
                run['schedule'], p['groups'], p['players_per_group'], p['weeks']))
        else:
            print(f"Golfers {p['weeks']} weeks: {run['stats']['status']} (no solution to validate)")
    for run in json.loads((results / 'sudoku.json').read_text())['runs']:
        check(f"Sudoku {run['difficulty']}", validate_solution(run['input'], run['solution']))
    for filename in ['latin-5.json', 'latin-3-classic.json']:
        run = json.loads((results / filename).read_text())
        check(filename, validate_square(run['square'], run['size']))
    for tree in json.loads((results / 'search-trees.json').read_text()):
        check(tree['problem'], validate_path(tree))
    reference = json.loads((results.parent / 'data/golfers-10-reference.json').read_text())
    certificate = verify_reference(reference)
    saved_certificate = json.loads((results / 'golfers-optimality.json').read_text())
    if certificate != saved_certificate:
        raise ValueError('Saved optimality certificate differs from independent recomputation.')
    check('Published ten-week golfers witness', certificate['validation'])
    for path in sorted(results.glob('benchmark-*.json')):
        benchmark = json.loads(path.read_text())
        algorithm = benchmark['algorithm']
        successful_values = []
        for trial in benchmark['runs']:
            raw = trial['result']
            validation = None
            if algorithm == 'sudoku' and raw['solution'] is not None:
                validation = validate_solution(raw['input'], raw['solution'])
            elif algorithm == 'golfers' and raw['schedule'] is not None:
                params = benchmark['parameters']
                validation = validate_schedule(raw['schedule'], params.get('groups', 3),
                                               params.get('players_per_group', 2), trial['value'])
            elif algorithm == 'latin' and raw['square'] is not None:
                validation = validate_square(raw['square'], trial['value'])
            elif algorithm == 'trees' and raw['tree']['solution_path']:
                validation = validate_path(raw['tree'])
            if validation is not None:
                check(f"{path.stem}: {trial['value']}, sample {trial['sample']}", validation)
            if algorithm == 'trees':
                expected_success = not any(n['kind'] in ('time_limit', 'node_limit')
                                           for n in raw['tree']['nodes'])
            else:
                expected_success = bool(validation and validation['valid']
                                        and raw['stats']['status'] == 'solved')
            if trial['success'] != expected_success:
                raise ValueError(f'{path.name}: inconsistent benchmark success flag.')
            if trial['success']:
                successful_values.append(trial['value'])
        if benchmark['summary']['largest_observed_success'] != max(successful_values, default=None):
            raise ValueError(f'{path.name}: inconsistent empirical summary.')
        print(f'{path.stem}: empirical summary checked (not a universal maximum).')
    print(f'{count} saved solutions independently validated; published witness proves maximum = 10.')
    print('The local DFS experiment is separate and found five weeks within its budget.')


if __name__ == '__main__':
    main()
