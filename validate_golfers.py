"""Independent schedule checks; does not import the search implementation."""

from collections import Counter
from itertools import combinations


def validate_schedule(schedule, groups: int, players_per_group: int, weeks: int) -> dict:
    errors = []
    pair_counts = Counter()
    players = set(range(groups * players_per_group))
    if not isinstance(schedule, list) or len(schedule) != weeks:
        return {"valid": False, "objective": None, "errors": ["Wrong number of weeks."]}
    for week_index, week in enumerate(schedule, 1):
        if not isinstance(week, list) or len(week) != groups:
            errors.append(f"Week {week_index}: wrong group count.")
            continue
        seen = []
        for group in week:
            if (not isinstance(group, list) or len(group) != players_per_group
                    or any(type(a) is not int or a not in players for a in group)):
                errors.append(f"Week {week_index}: malformed group.")
                continue
            seen.extend(group)
            pair_counts.update(combinations(sorted(group), 2))
        if len(seen) != len(players) or set(seen) != players:
            errors.append(f"Week {week_index}: players must each appear exactly once.")
    objective = sum(max(0, count - 1) for count in pair_counts.values())
    if objective:
        errors.append(f"Repeated pairs: objective={objective}.")
    return {"valid": not errors, "objective": objective, "errors": errors}
