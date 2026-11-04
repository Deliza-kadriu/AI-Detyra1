"""Independent checks of the three example solution paths."""


def validate_path(tree):
    path = tree.get('solution_path', [])
    if not path:
        return {'valid': False, 'errors': ['No solution path found within limits.']}
    errors = []
    nodes = tree['nodes']
    steps = [nodes[i] for i in path]
    if path[0] != 0:
        errors.append('Path must start at root.')
    for before, after in zip(steps, steps[1:]):
        if after['parent'] != before['id'] or after['depth'] != before['depth'] + 1:
            errors.append('Broken parent or depth link.')
    states = [tuple(step['state']) for step in steps]
    name = tree['problem']
    if name == '8-puzzle':
        if states[0] != (1, 2, 3, 4, 5, 6, 0, 7, 8) or states[-1] != tuple(range(1, 9)) + (0,):
            errors.append('Wrong start or goal board.')
        for board in states:
            if sorted(board) != list(range(9)):
                errors.append('Invalid tile inventory.')
        for a, b in zip(states, states[1:]):
            changed = [i for i in range(9) if a[i] != b[i]]
            ia, ib = a.index(0), b.index(0)
            distance = abs(ia // 3 - ib // 3) + abs(ia % 3 - ib % 3)
            if sorted(changed) != sorted([ia, ib]) or distance != 1 or a[ib] != b[ia]:
                errors.append('Illegal blank move.')
    elif name == 'missionaries':
        if states[0] != (3, 3, 0) or states[-1] != (0, 0, 1):
            errors.append('Wrong river start or goal.')
        for m, c, bank in states:
            if not (0 <= m <= 3 and 0 <= c <= 3 and bank in (0, 1)):
                errors.append('Invalid population or boat bank.')
            if (m and c > m) or (3-m and 3-c > 3-m):
                errors.append('Unsafe bank.')
        for a, b in zip(states, states[1:]):
            direction = 1 if a[2] == 0 else -1
            dm, dc = (a[0] - b[0]) * direction, (a[1] - b[1]) * direction
            if b[2] != 1-a[2] or dm < 0 or dc < 0 or not 1 <= dm+dc <= 2:
                errors.append('Illegal boat crossing.')
    elif name == 'workforce':
        if states[0] != () or len(states[-1]) != 6:
            errors.append('Wrong workforce start or goal.')
        for a, b in zip(states, states[1:]):
            if b[:-1] != a or b[-1] not in ('D', 'N', 'O'):
                errors.append('Illegal base-pattern extension.')
        base = states[-1]
        if len(base) == 6:
            roster = [[base[(d-2*w) % 6] for d in range(6)] for w in range(3)]
            for d in range(6):
                if sorted(row[d] for row in roster) != ['D', 'N', 'O']:
                    errors.append('Daily coverage violation.')
            for row in roster:
                if any(row.count(s) != 2 for s in ('D', 'N', 'O')):
                    errors.append('Shift-count violation.')
                for d in range(6):
                    if row[d] == 'N' and row[(d+1) % 6] == 'D':
                        errors.append('Night-to-Day violation, including cycle boundary.')
                    if all(row[(d+k) % 6] != 'O' for k in range(3)):
                        errors.append('Consecutive-work violation, including cycle boundary.')
    else:
        errors.append('Unknown problem.')
    return {'valid': not errors, 'errors': errors}
