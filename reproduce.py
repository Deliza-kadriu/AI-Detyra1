"""Regenerate assignment outputs and verify them using only the standard library."""

from pathlib import Path
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parent
    commands = [
        ['social_golfers.py', '--maximize', '--weeks', '10', '--time-limit', '3',
         '--max-nodes', '1000000', '--output', 'results/golfers-32.json'],
        ['sudoku.py', '--output', 'results/sudoku.json'],
        ['latin_square.py', '--size', '5', '--output', 'results/latin-5.json'],
        ['latin_square.py', '--size', '3', '--literal-deepening',
         '--output', 'results/latin-3-classic.json'],
        ['-m', 'search_trees.generate'],
        ['golfers_reference.py'],
        ['social_golfers.py', '--strategy', 'structured', '--weeks', '10', '--max-nodes', '100000',
         '--time-limit', '3', '--output', 'results/golfers-explore-32.json'],
        ['social_golfers.py', '--strategy', 'structured', '--weeks', '9', '--max-nodes', '100000',
         '--time-limit', '3', '--output', 'results/golfers-structured-9.json'],
        ['social_golfers.py', '--strategy', 'restarts', '--weeks', '10', '--max-nodes', '100000',
         '--time-limit', '3', '--output', 'results/golfers-restarts-32.json'],
        ['benchmarks.py', '--algorithm', 'sudoku', '--from', '25', '--to', '65', '--step', '10',
         '--samples', '3', '--seconds', '0.5', '--total-seconds', '10', '--output', 'results/benchmark-sudoku.json'],
        ['benchmarks.py', '--algorithm', 'golfers', '--from', '1', '--to', '7', '--step', '1',
         '--samples', '1', '--seconds', '0.5', '--total-seconds', '5', '--output', 'results/benchmark-golfers.json'],
        ['benchmarks.py', '--algorithm', 'latin', '--from', '1', '--to', '6', '--step', '1',
         '--samples', '1', '--seconds', '0.5', '--total-seconds', '5', '--output', 'results/benchmark-latin.json'],
        ['benchmarks.py', '--algorithm', 'trees', '--from', '0', '--to', '8', '--step', '2',
         '--samples', '1', '--seconds', '0.5', '--total-seconds', '5', '--output', 'results/benchmark-trees.json'],
        ['verify_results.py'],
        ['-m', 'unittest', 'discover', '-s', 'tests', '-v'],
    ]
    for command in commands:
        print('\nRunning: python3 ' + ' '.join(command), flush=True)
        subprocess.run([sys.executable, *command], cwd=root, check=True)


if __name__ == '__main__':
    main()
