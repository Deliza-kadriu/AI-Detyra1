"""Optional enhanced DFS: restarts, forward checking and explicit candidate ordering.

The coursework's plain numeric DFS remains in social_golfers.py. Structured
ordering generates preferences from finite-field arithmetic; it never reads a
published schedule or stored result. These modes are extra search experiments.
"""

from dataclasses import dataclass
import random
from time import perf_counter

from social_golfers import GolfersProblem, SearchStats


@dataclass
class ExploreStats(SearchStats):
    attempts: int = 0
    restarts: int = 0
    best_weeks: int = 0
    stop_reason: str | None = None


def _gf8_mul(a, b):
    """GF(8) multiplication, polynomial x^3+x+1 (binary 1011)."""
    result = 0
    while b:
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & 8:
            a ^= 11
    return result


def _preferred_group(player, week):
    x, y = player % 4, player // 4
    if week < 8:
        return y ^ _gf8_mul(week, x)
    return 2*x + y//4


def solve_explore(problem: GolfersProblem, *, strategy='restarts', seed=2026,
                  restart_nodes=10000, max_nodes=1000000, time_limit=10,
                  stats=None, trace=None, on_best=None):
    """Return the longest complete valid prefix found, including on budget stop.

    stats.status='solved' means the requested target was reached. A nonempty
    result with status='resource_limit' is a partial achievement, not a solution
    of the requested target. Global budgets include every restart.
    """
    if strategy not in ('restarts', 'structured'):
        raise ValueError('Unknown enhanced DFS strategy.')
    if strategy == 'structured' and (problem.groups, problem.players_per_group) != (8, 4):
        raise ValueError('Structured ordering is available for eight groups of four players.')
    for name, value in [('seed',seed),('restart_nodes',restart_nodes),('max_nodes',max_nodes)]:
        if type(value) is not int or value < (0 if name == 'seed' else 1):
            raise ValueError(f'{name} must be a {"nonnegative" if name == "seed" else "positive"} integer.')
    if not 0 < time_limit < float('inf'):
        raise ValueError('time_limit must be positive and finite.')
    stats = stats if stats is not None else ExploreStats()
    fresh = ExploreStats()
    for key, value in vars(fresh).items():
        setattr(stats,key,value)
    stats.status = 'running'
    start = perf_counter()
    n, p = problem.players, problem.players_per_group
    best = []

    class Restart(Exception):
        pass

    class Budget(Exception):
        pass

    def say(message):
        if trace:
            trace(message)

    bound = problem.week_upper_bound()
    if bound is not None and problem.weeks > bound:
        stats.status = 'infeasible'
        stats.stop_reason = f'Target exceeds the pair-counting bound of {bound} weeks.'
        stats.elapsed_seconds = perf_counter()-start
        say('BOUND: '+stats.stop_reason)
        return None
    say(f'START enhanced DFS ({strategy}); target {problem.weeks}; seed {seed}')
    try:
        while True:
            if stats.expanded_nodes >= max_nodes:
                raise Budget('Node limit reached across all attempts.')
            if perf_counter()-start >= time_limit:
                raise Budget('Time limit reached across all attempts.')
            stats.attempts += 1
            rng = random.Random(seed+stats.attempts-1)
            orders = []
            for _ in range(problem.weeks):
                order = list(range(n))
                rng.shuffle(order)
                orders.append(order)
            # Structured preferences are used on the first attempt. Later restarts
            # explore different orders rather than replaying the same construction.
            structured = strategy == 'structured' and stats.attempts == 1
            schedule = [[list(range(i,i+p)) for i in range(0,n,p)]]
            met = [0]*n
            for group in schedule[0]:
                mask = sum(1 << player for player in group)
                for player in group:
                    met[player] = mask ^ (1 << player)
            attempt_nodes = 0
            say(f'ATTEMPT {stats.attempts}: fix week one; retain best={stats.best_weeks}')

            def visit(depth):
                nonlocal attempt_nodes
                if stats.expanded_nodes >= max_nodes:
                    raise Budget('Node limit reached across all attempts.')
                if perf_counter()-start >= time_limit:
                    raise Budget('Time limit reached across all attempts.')
                if attempt_nodes >= restart_nodes:
                    raise Restart()
                stats.expanded_nodes += 1
                stats.max_depth = max(stats.max_depth,depth)
                attempt_nodes += 1

            def week():
                nonlocal best
                visit(len(schedule)*n)
                if len(schedule) > stats.best_weeks:
                    best = [[group[:] for group in w] for w in schedule]
                    stats.best_weeks = len(best)
                    if on_best:
                        on_best([[group[:] for group in w] for w in best])
                    say(f'BEST: {len(best)} complete weeks found; {stats.expanded_nodes} nodes')
                if len(schedule) == problem.weeks:
                    return True
                week_index = len(schedule)
                groups = []

                def partition(remaining):
                    visit(week_index*n+len(groups)*p)
                    if not remaining:
                        schedule.append([group[:] for group in groups])
                        say(f'WEEK {len(schedule)} complete: {groups}')
                        if week():
                            return True
                        schedule.pop()
                        stats.backtracks += 1
                        return False
                    mask = sum(1 << a for a in remaining)
                    degrees = {a:(mask & ~(met[a] | (1 << a))).bit_count() for a in remaining}
                    anchor = min(remaining,key=degrees.get)
                    if degrees[anchor] < p-1:
                        say('PRUNE: a remaining player has too few compatible partners')
                        return False
                    group = [anchor]
                    allowed = [b for b in remaining if b != anchor and not (met[anchor] >> b & 1)]
                    # Most constrained first; seeded order breaks equal-degree ties.
                    if structured and week_index <= 8:
                        preferred = _preferred_group(anchor,week_index)
                        allowed.sort(key=lambda b:(_preferred_group(b,week_index) != preferred,degrees[b]))
                    else:
                        allowed.sort(key=degrees.get)

                    def fill(candidates):
                        visit(week_index*n+len(groups)*p+len(group))
                        needed = p-len(group)
                        if not needed:
                            pair_mask = sum(1 << a for a in group)
                            for a in group:
                                met[a] |= pair_mask ^ (1 << a)
                            groups.append(group[:])
                            chosen = set(group)
                            if partition([a for a in remaining if a not in chosen]):
                                return True
                            groups.pop()
                            for a in group:
                                met[a] ^= pair_mask ^ (1 << a)
                            stats.backtracks += 1
                            return False
                        if len(candidates) < needed:
                            return False
                        for index, player in enumerate(candidates):
                            if len(candidates)-index < needed:
                                break
                            group.append(player)
                            say(f'ASSIGN week {week_index+1}, group {len(groups)+1}: {group}')
                            # Keep only values compatible with every current member.
                            tail = [b for b in candidates[index+1:] if not (met[player] >> b & 1)]
                            if fill(tail):
                                return True
                            group.pop()
                            stats.backtracks += 1
                            say(f'BACKTRACK: remove player {player}; group now {group}')
                        return False

                    return fill(allowed)

                return partition(orders[week_index])

            try:
                if week():
                    stats.status = 'solved'
                    say(f'GOAL: reached {problem.weeks} weeks')
                    return best
                stats.status = 'infeasible'
                stats.stop_reason = 'Exhaustive DFS proved the requested target infeasible.'
                return best or None
            except Restart:
                stats.restarts += 1
                say(f'RESTART after {attempt_nodes} nodes; preserve {stats.best_weeks} complete weeks')
    except Budget as exc:
        stats.status = 'resource_limit'
        stats.stop_reason = str(exc)
        say(f'STOP: {exc} Best retained: {stats.best_weeks} weeks; target unresolved.')
        return best or None
    finally:
        stats.elapsed_seconds = perf_counter()-start
