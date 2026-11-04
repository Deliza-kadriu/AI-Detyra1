"""Explicit small instances chosen for the assignment's three search trees."""

PUZZLE_START = (1, 2, 3, 4, 5, 6, 0, 7, 8)
PUZZLE_GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)
SHIFTS = ('D', 'N', 'O')


def puzzle_actions(state):
    blank = state.index(0)
    r, c = divmod(blank, 3)
    for name, dr, dc in [('Up', -1, 0), ('Down', 1, 0), ('Left', 0, -1), ('Right', 0, 1)]:
        nr, nc = r + dr, c + dc
        if not (0 <= nr < 3 and 0 <= nc < 3):
            yield name, None, 'Blank would leave the board.'
            continue
        child = list(state)
        target = nr * 3 + nc
        child[blank], child[target] = child[target], child[blank]
        yield name, tuple(child), None


def river_actions(state):
    m, c, bank = state  # 0 = boat on left; 1 = boat on right.
    for dm, dc in [(1, 0), (0, 1), (2, 0), (1, 1), (0, 2)]:
        name = f'{dm}M,{dc}C ' + ('L->R' if bank == 0 else 'R->L')
        sign = -1 if bank == 0 else 1
        nm, nc = m + sign * dm, c + sign * dc
        if not (0 <= nm <= 3 and 0 <= nc <= 3):
            yield name, None, 'Passengers unavailable on departure bank.'
        elif (nm > 0 and nc > nm) or (3 - nm > 0 and 3 - nc > 3 - nm):
            yield name, None, 'Cannibals outnumber missionaries on a bank.'
        else:
            yield name, (nm, nc, 1 - bank), None


def workforce_error(base):
    # Worker w follows the base pattern shifted by 2*w days in a 6-day cycle.
    for shift in SHIFTS:
        if base.count(shift) > 2:
            return 'A worker would exceed two days of a shift.'
    for i in range(len(base) - 1):
        if base[i:i + 2] == ('N', 'D'):
            return 'Night cannot be followed by Day.'
    for i in range(len(base) - 2):
        if all(v != 'O' for v in base[i:i + 3]):
            return 'More than two consecutive working days.'
    for day in range(6):
        indices = [(day - 2 * worker) % 6 for worker in range(3)]
        known = [base[i] for i in indices if i < len(base)]
        if len(known) != len(set(known)):
            return 'Daily coverage requires one Day, one Night and one Off.'
    if len(base) == 6:
        for day in range(6):
            if base[day] == 'N' and base[(day + 1) % 6] == 'D':
                return 'Night-to-Day violation across cycle boundary.'
            if all(base[(day + k) % 6] != 'O' for k in range(3)):
                return 'Consecutive-work violation across cycle boundary.'
    return None


def workforce_actions(state):
    for shift in SHIFTS:
        child = state + (shift,)
        yield f'Base day {len(child)} = {shift}', child, workforce_error(child)


PROBLEMS = {
    '8-puzzle': {'start': PUZZLE_START, 'goal': lambda s: s == PUZZLE_GOAL,
                 'actions': puzzle_actions, 'depth': 3,
                 'description': '3x3 board, 0=blank; start 123/456/078; goal 123/456/780. Order: Up, Down, Left, Right.'},
    'missionaries': {'start': (3, 3, 0), 'goal': lambda s: s == (0, 0, 1),
                     'actions': river_actions, 'depth': 12,
                     'description': '3 missionaries, 3 cannibals, capacity 2; boat carries 1 or 2 people. State (M left, C left, boat bank); 0=left, 1=right. Both banks must be safe.'},
    'workforce': {'start': (), 'goal': lambda s: len(s) == 6,
                  'actions': workforce_actions, 'depth': 6,
                  'description': '3 workers; 6-day repeating cycle; shifts D=Day, N=Night, O=Off. Worker w follows base[(day-2*w) mod 6]. Exactly one D/N/O per day, two of each shift per worker, at most two consecutive working days, no N->D, including cycle boundary. State is a base-pattern prefix; order D,N,O.'},
}
