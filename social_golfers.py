"""Deterministic Social Golfers DFS with reversible pair constraints."""

import argparse
from dataclasses import asdict, dataclass
import json
from math import factorial
from pathlib import Path
from time import perf_counter, sleep
from typing import Callable

Schedule = list[list[list[int]]]


@dataclass(frozen=True)
class GolfersProblem:
    groups: int = 8
    players_per_group: int = 4
    weeks: int = 2

    def __post_init__(self):
        if any(type(v) is not int or v < 1 for v in
               (self.groups, self.players_per_group, self.weeks)):
            raise ValueError("Groups, players per group and weeks must be positive integers.")

    @property
    def players(self) -> int:
        return self.groups * self.players_per_group

    def weekly_partitions(self) -> int:
        return factorial(self.players) // (
            factorial(self.players_per_group) ** self.groups * factorial(self.groups)
        )

    def landscape(self) -> int:
        return self.weekly_partitions() ** self.weeks

    def week_upper_bound(self) -> int | None:
        if self.players_per_group == 1:
            return None
        return (self.players - 1) // (self.players_per_group - 1)


@dataclass
class SearchStats:
    expanded_nodes: int = 0
    backtracks: int = 0
    max_depth: int = 0
    elapsed_seconds: float = 0.0
    status: str = "pending"


class SearchLimitReached(RuntimeError):
    """Search stopped before feasibility could be decided."""


def solve_dfs(problem: GolfersProblem, *, max_nodes: int | None = None,
              time_limit: float | None = None,
              stats: SearchStats | None = None,
              trace: Callable[[str], None] | None = None) -> Schedule | None:
    """Return a schedule, None for proven infeasibility, or raise on a limit.

    DFS adds players to groups in numeric order. Symmetry breaking fixes week
    one and makes each later group's first player the smallest unassigned ID.
    No heuristic ranking, randomized ordering or precomputed schedule is used.
    """
    if max_nodes is not None and (type(max_nodes) is not int or max_nodes < 1):
        raise ValueError("max_nodes must be a positive integer.")
    if time_limit is not None and not 0 < time_limit < float("inf"):
        raise ValueError("time_limit must be positive and finite.")
    stats = stats if stats is not None else SearchStats()
    stats.expanded_nodes = stats.backtracks = stats.max_depth = 0
    stats.elapsed_seconds = 0.0
    stats.status = "running"
    start = perf_counter()
    n, p = problem.players, problem.players_per_group
    schedule = [[list(range(i, i + p)) for i in range(0, n, p)]]
    # Each bit records a partner already encountered, including partial groups.
    met = [0] * n
    for group in schedule[0]:
        for a in group:
            for b in group:
                if a != b:
                    met[a] |= 1 << b

    def visit(depth: int) -> None:
        if max_nodes is not None and stats.expanded_nodes >= max_nodes:
            raise SearchLimitReached("Node limit reached; feasibility is unknown.")
        if time_limit is not None and perf_counter() - start >= time_limit:
            raise SearchLimitReached("Time limit reached; feasibility is unknown.")
        stats.expanded_nodes += 1
        stats.max_depth = max(stats.max_depth, depth)

    def week(depth: int) -> bool:
        visit(depth)
        if len(schedule) == problem.weeks:
            return True
        week_number = len(schedule) + 1
        groups: list[list[int]] = []

        def partition(remaining: tuple[int, ...], depth: int) -> bool:
            visit(depth)
            if not remaining:
                schedule.append([group[:] for group in groups])
                if trace:
                    trace(f"WEEK {week_number} complete: {groups}")
                if week(depth):
                    return True
                schedule.pop()
                stats.backtracks += 1
                if trace:
                    trace(f"BACKTRACK: undo week {week_number}; try another partition")
                return False
            group = [remaining[0]]
            group_number = len(groups) + 1
            if trace:
                trace(f"Week {week_number}, group {group_number}: start with player {group[0]}")

            def fill(candidates: tuple[int, ...], depth: int) -> bool:
                visit(depth)
                needed = p - len(group)
                if needed == 0:
                    groups.append(group[:])
                    used = set(group)
                    rest = tuple(a for a in remaining if a not in used)
                    if partition(rest, depth):
                        return True
                    groups.pop()
                    stats.backtracks += 1
                    return False
                for index, player in enumerate(candidates):
                    if len(candidates) - index < needed:
                        break
                    if any(met[player] & (1 << partner) for partner in group):
                        if trace:
                            trace(f"REJECT player {player} for {group}: a pair has already met")
                        continue
                    # Assign: all new edges are legal, so XOR precisely undoes them.
                    for partner in group:
                        met[player] |= 1 << partner
                        met[partner] |= 1 << player
                    group.append(player)
                    if trace:
                        trace(f"ASSIGN week {week_number}, group {group_number}: {group}")
                    if fill(candidates[index + 1:], depth + 1):
                        return True
                    group.pop()
                    for partner in group:
                        met[player] ^= 1 << partner
                        met[partner] ^= 1 << player
                    stats.backtracks += 1
                    if trace:
                        trace(f"BACKTRACK: remove player {player}; group is now {group}")
                return False

            return fill(remaining[1:], depth + 1)

        return partition(tuple(range(n)), depth)

    try:
        bound = problem.week_upper_bound()
        if bound is not None and problem.weeks > bound:
            if trace:
                trace(f"BOUND: each player has {n-1} possible partners and meets {p-1} "
                      f"per week; at most {bound} weeks. Requested {problem.weeks}; no search needed.")
            stats.status = "infeasible"
            return None
        if trace:
            trace(f"START: {n} players, {problem.groups} groups of {p}, target {problem.weeks} weeks")
            trace(f"FIX week 1 by symmetry: {schedule[0]}")
        if week(n):
            stats.status = "solved"
            if trace:
                trace(f"GOAL: all {problem.weeks} weeks complete")
            return schedule
        stats.status = "infeasible"
        if trace:
            trace("EXHAUSTED: all alternatives checked; no schedule exists")
        return None
    except SearchLimitReached:
        stats.status = "resource_limit"
        if trace:
            trace("STOP: resource limit reached; feasibility is unknown")
        raise
    finally:
        stats.elapsed_seconds = perf_counter() - start


def run_case(problem: GolfersProblem, time_limit: float, max_nodes: int,
             trace: Callable[[str], None] | None = None) -> dict:
    # Validator deliberately reconstructs all pairs rather than using DFS state.
    from validate_golfers import validate_schedule
    stats = SearchStats()
    schedule = None
    try:
        schedule = solve_dfs(problem, time_limit=time_limit, max_nodes=max_nodes,
                             stats=stats, trace=trace)
    except SearchLimitReached:
        pass
    validation = validate_schedule(schedule, problem.groups, problem.players_per_group,
                                   problem.weeks) if schedule is not None else None
    if validation is not None and not validation["valid"]:
        raise RuntimeError(f"Solver returned an invalid schedule: {validation}")
    return {"problem": asdict(problem), "algorithm": "DFS with backtracking",
            "stats": asdict(stats), "schedule": schedule, "validation": validation}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--groups", type=int, default=8)
    parser.add_argument("--players-per-group", type=int, default=4)
    parser.add_argument("--weeks", type=int, default=2)
    parser.add_argument("--time-limit", type=float, default=5.0, help="seconds per case")
    parser.add_argument("--max-nodes", type=int, default=1_000_000)
    parser.add_argument("--maximize", action="store_true",
                        help="try increasing weeks up to --weeks or the pair bound")
    parser.add_argument("--output", type=Path, help="save actual runs as JSON")
    parser.add_argument("--trace", action="store_true", help="print DFS choices and backtracking live")
    parser.add_argument("--delay", type=float, default=0,
                        help="seconds between trace lines; requires --trace; counts toward time limit")
    args = parser.parse_args(argv)
    try:
        if not 0 <= args.delay < float("inf"):
            raise ValueError("delay must be nonnegative and finite.")
        if args.delay and not args.trace:
            raise ValueError("--delay requires --trace.")

        def show_trace(message: str) -> None:
            print(message, flush=True)
            if args.delay:
                sleep(args.delay)

        problem = GolfersProblem(args.groups, args.players_per_group, args.weeks)
        bound = problem.week_upper_bound()
        target = min(args.weeks, bound) if bound is not None else args.weeks
        weeks = range(1, target + 1) if args.maximize else [args.weeks]
        runs = []
        best = 0
        for w in weeks:
            run = run_case(GolfersProblem(args.groups, args.players_per_group, w),
                           args.time_limit, args.max_nodes,
                           trace=show_trace if args.trace else None)
            runs.append(run)
            stats = run["stats"]
            print(f"{w} weeks: {stats['status']}; {stats['expanded_nodes']} nodes; "
                  f"{stats['elapsed_seconds']:.4f}s; {stats['backtracks']} backtracks")
            if run["schedule"] is not None:
                best = w
                for index, groups in enumerate(run["schedule"], 1):
                    print(f"  Week {index}: " + " | ".join(
                        ",".join(map(str, group)) for group in groups))
                print("  Independent validation: PASS; repeated-pair objective: 0")
            else:
                break  # Feasibility is monotone in weeks; a limit proves nothing.
        summary = {"best_weeks_found": best, "pair_counting_upper_bound": bound,
                   "maximum_proven": bool(best and bound is not None and best == bound)
                   or bool(args.maximize and best and runs[-1]["stats"]["status"] == "infeasible")}
        print(json.dumps(summary))
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps({"summary": summary, "runs": runs}, indent=2) + "\n")
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
