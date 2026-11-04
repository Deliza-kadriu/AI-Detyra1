"""Validate an attributed published optimal witness, separately from local DFS."""

import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path

from validate_golfers import validate_schedule

ROOT = Path(__file__).resolve().parent


def verify_reference(data):
    alphabet = 'ABCDEFGHIJKLMNOPabcdefghijklmnop'
    mapped = [[[alphabet.index(label) for label in group] for group in week]
              for week in data['labelled_weeks']]
    if mapped != data['schedule']:
        raise ValueError('Label transcription does not match the numeric schedule.')
    checked = validate_schedule(mapped, 8, 4, 10)
    if not checked['valid']:
        raise ValueError(checked)
    meetings = Counter(pair for week in mapped for group in week
                       for pair in combinations(sorted(group), 2))
    partners = {player: set() for player in range(32)}
    for a, b in meetings:
        partners[a].add(b)
        partners[b].add(a)
    missing = [list(pair) for pair in combinations(range(32), 2) if pair not in meetings]
    upper = (32 - 1) // (4 - 1)
    if len(meetings) != 480 or any(len(others) != 30 for others in partners.values()):
        raise ValueError('Unexpected pair or partner counts.')
    return {'evidence_kind': 'independently validated published witness, not local DFS output',
            'source_url': data['source_url'], 'problem': {'groups': 8, 'players_per_group': 4},
            'verified_feasible_weeks': len(mapped), 'pair_counting_upper_bound': upper,
            'maximum_proven': len(mapped) == upper, 'optimal_weeks': upper,
            'distinct_pairs_met': len(meetings), 'partners_per_player': 30,
            'unmet_pairs': missing, 'validation': checked}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'results')
    args = parser.parse_args(argv)
    data = json.loads((ROOT / 'data/golfers-10-reference.json').read_text())
    certificate = verify_reference(data)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / 'golfers-optimality.json').write_text(json.dumps(certificate, indent=2) + '\n')
    lines = ['# Ten-week reference schedule and optimality check', '',
             '**This is a published reference witness, not a result found by our DFS.**', '',
             f"Source: [{data['source_title']}]({data['source_url']}).",
             f"Located via [CSPLib results]({data['discovery_url']}).", '',
             data['transformation'], '',
             '| Week | Group 1 | Group 2 | Group 3 | Group 4 | Group 5 | Group 6 | Group 7 | Group 8 |',
             '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for week, groups in enumerate(data['schedule'], 1):
        lines.append(f'| {week} | ' + ' | '.join(','.join(map(str, group)) for group in groups) + ' |')
    lines += ['', '## Independent checks', '',
              '- Exactly 32 players, partitioned into eight groups of four every week.',
              '- No repeated pair; duplicate-excess objective is zero.',
              '- 480 distinct pairs meet; each player meets 30 different partners.',
              '- The 16 unmet pairs are disjoint: each player misses one partner.', '',
              '## Why ten is the maximum', '',
              'Each player meets three new partners per week and has only 31 possible partners.',
              'Thus 3*w <= 31, so w <= floor(31/3) = 10. The independently validated',
              'ten-week witness attains this bound, proving that the maximum is ten.', '',
              'The saved local DFS experiment still found five weeks and hit its node',
              'budget while searching for six. This reference resolves the mathematical',
              'question without claiming that the local DFS discovered the optimum.', '']
    (args.output_dir / 'golfers-optimality.md').write_text('\n'.join(lines))
    print('Published witness: PASS; 480 distinct pairs; optimal maximum = 10 weeks.')
    print('Local DFS result remains five weeks within the saved search budget.')


if __name__ == '__main__':
    main()
