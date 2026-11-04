# Detyra 1 — Uninformed Search

New assignment workspace, separate from the existing `detyra1-*-sample`
demonstration projects. Python 3.10+; no external packages required.

All four assignment sections are implemented: Social Golfers (DFS/backtracking),
Sudoku (FIFO BFS), Latin Square (IDDFS/backtracking), and three search trees.
The Social Golfers maximum is ten weeks, established by an independently
validated, attributed published schedule. The local DFS found five weeks within
its recorded budget; it did not discover the published optimum.

## Local demonstration UI

```sh
python3 ui_server.py
```

This opens **Search Lab** at `http://127.0.0.1:8765`. It runs locally with the
Python standard library; no installation, accounts or internet are needed.
Select the problem to reveal its inputs, then click **Run experiment**.

- **Social Golfers:** group count, players per group, weeks, increasing-week
  search, node/time budgets, live trace and speed. Start with the Small example
  preset to demonstrate real backtracking; use 32 players for the larger case.
- **Sudoku:** Easy/Medium/Hard, all examples, or an editable custom 9x9 grid.
  The board updates with real FIFO queue steps. Use a zero-millisecond pause for
  Hard to avoid spending the time budget on animation.
- **Latin Square:** n, canonical-border symmetry, optional goal-depth shortcut,
  budgets and actual assignment/undo traces. Try n=3 with symmetry unchecked to
  demonstrate the complete sequence of depth-limited searches.
- **Search trees:** choose the problem or all three, adjust depth/node budgets,
  and inspect states, rejected actions, repeated states and the solution path.
- **Published schedule:** independently verify the attributed ten-week witness;
  this is explicitly separate from running DFS.

**Stop** terminates the experiment process. Completed cases display independent
validation, and **Download JSON** exports the run without modifying saved
coursework outputs. A trace shows at most 5,000 steps; after that search continues
without trace pauses. The on-screen console keeps the latest 400 lines. Tracing
and animation count toward solver time limits. The UI permits one experiment at
once, with an overall 125-second cap; resource limits do not prove infeasibility.

The UI uses bounded demonstration inputs (at most 64 golfers and n<=7 for Latin
Square). Larger inputs can still use the CLI. Change the local port with
`python3 ui_server.py --port 8766`, or use `--no-browser` to open the page manually.
Keep the terminal running during the demonstration; Ctrl+C shuts down the server.

Suggested presentation: small Golfers example → Easy Sudoku → n=3 Latin Square
without symmetry → the three trees. Explain the state, constraints, search order
and stopping condition before running each example.

## Run

From this directory:

```sh
python3 main.py
python3 main.py --landscape
python3 main.py golfers --weeks 5
python3 main.py golfers --maximize --weeks 10 --output results/golfers-32.json
python3 main.py sudoku --difficulty all --output results/sudoku.json
python3 main.py sudoku --difficulty hard
python3 main.py latin --size 5 --output results/latin-5.json
python3 main.py latin --size 3 --literal-deepening --output results/latin-3-classic.json
python3 main.py trees
python3 -m unittest discover -s tests -v
python3 verify_results.py
python3 main.py golfers-reference
```

The first command prints project status. `--landscape` calculates the initial
search-space bounds from `report.md`. The golfers commands solve one instance
or try increasing week counts. Run `python3 main.py golfers --help` for options.
The default limits are five seconds and one million entered search nodes per
case. A resource limit leaves feasibility unknown.

## Assignment requirements

Official brief: [Detyra1.md](https://github.com/adrianymeri/Artificial-Intelligence-2026/blob/main/Detyra1.md).
Course overview: [repository](https://github.com/adrianymeri/Artificial-Intelligence-2026).
The upstream repository contains the course README, assignment brief and MIT license;
it does not supply an application to extend.

| Problem | Required work | File |
| --- | --- | --- |
| Social Golfers | Model, representation, objective, landscape, DFS with backtracking | `social_golfers.py` |
| Sudoku | Model, representation, objective, landscape, BFS with backtracking; Easy/Medium/Hard | `sudoku.py` |
| Latin Square | Model, representation, objective, landscape, IDDFS with backtracking | `latin_square.py` |
| Search trees | 8-Puzzle, Missionaries and Cannibals, Rotating Workforce Scheduling | `search_trees/README.md` |

`docs/Detyra1.md` preserves an existing local transcription of the brief;
see `docs/SOURCES.md` for provenance. `report.md` documents models, algorithms, measurements and limitations.
`results/` is reserved for outputs from actual runs.

## Implementation checklist

- [x] Review the upstream repository and map all four assignment sections.
- [x] Create separate modules, source notes and initial report.
- [x] Add reproducible landscape calculations for the initial models.
- [x] Implement and validate Social Golfers DFS/backtracking, starting with small instances.
- [x] Demonstrate five weeks for 32 players and run a bounded investigation of six weeks.
- [x] Resolve the exact maximum for 32 players using an attributed published ten-week witness and the matching upper bound.
- [x] Implement Sudoku BFS and document how invalid partial assignments are rejected.
- [x] Add and solve Easy, Medium and Hard Sudoku instances; document difficulty labels.
- [x] Implement Latin Square IDDFS with depth-limited backtracking.
- [x] Define the three search-tree instances and generate their trees.
- [x] Independently validate solutions and record time, expanded nodes and peak frontier.
- [x] Complete the report with measured results and limitations.

Keep numeric candidate order deterministic for the initial uninformed solvers.
Do not use heuristic solvers as substitutes for the algorithms requested above.

## Social Golfers results

`results/golfers-32.json` contains actual runs for weeks 1 through 6, with a
three-second / one-million-node limit per case. Weeks 1 through 5 were solved
and independently validated; week 6 reached the node limit. Five weeks is a
feasible result from this DFS run, not its proven maximum. A separate published
ten-week witness now attains the pair-counting upper bound; see below.

`validate_golfers.py` checks every weekly partition and counts every pair from
scratch, independently of the solver's bit masks. `tests/test_golfers.py` covers
feasible instances, backtracking, exhaustive infeasibility below the pair bound,
resource limits, malformed inputs and corrupted schedules.

## Sudoku usage and results

```sh
python3 main.py sudoku --difficulty easy
python3 main.py sudoku --difficulty medium
python3 main.py sudoku --difficulty hard
python3 main.py sudoku --difficulty all --output results/sudoku.json
python3 main.py sudoku --board-file my-board.json
```

A custom board is a JSON array of nine rows, each containing nine integers 0..9;
zero means empty. The solver preserves clues and the supplied input. Conflicting
clues are input errors. Exhausting the FIFO queue reports `infeasible`; reaching
a resource limit reports `resource_limit`, leaving feasibility unknown.

Options `--max-nodes`, `--max-frontier` and `--time-limit` control search budgets.
Defaults are 200,000 expanded boards, 50,000 queued boards and ten seconds per
puzzle. Memory remains exponential in the worst case; difficult custom puzzles
may exceed those budgets.

`data/sudoku.json` contains reproducible, locally generated fixtures with 25, 35
and 45 empty cells. Easy/Medium/Hard are demonstration labels based on clue
removal and observed BFS effort, not certified human difficulty. All three were
generated from the same valid completed grid; uniqueness is not claimed. The
solver receives only the incomplete input and uses no stored solution.

`results/sudoku.json` records actual inputs, solutions, landscape values and
search statistics. Easy, Medium and Hard required 46, 76 and 2,637 expanded
boards respectively; all passed `validate_sudoku.py`. The report explains FIFO
branch rejection and the brief's wording "BFS with Backtracking".

## Latin Square and search trees

`python3 main.py latin --size 5` runs genuine iterative deepening with a fresh
depth-limited backtracking search at each limit. By symmetry it fixes the first
row and column to 1..n, leaving (n-1)^2 free cells. Use
`--size 3 --literal-deepening` to explore all cells without symmetry reduction.
The optional `--goal-depth-pruning` skips provably too-shallow trees; it is off
in the saved runs. The default 5x5 run enters 4,914 nodes across 17 iterations.
`validate_latin.py` independently checks the output.

`python3 main.py trees` writes readable trees to `results/search-trees.md` and
full node data to `results/search-trees.json`. The examples are an 8-Puzzle
(two-move solution, tree truncated at depth 3), Missionaries and Cannibals
(11 crossings), and a three-worker rotating six-day schedule. Repeated states
are reference leaves; rejected actions carry reasons. The workforce rules and
all initial states are explicitly documented in `report.md`. Use `--help` for
depth/node limits or to choose one problem.

## Optimality evidence and full reproduction

The mathematical maximum for 32 golfers in groups of four is **ten weeks**.
The published schedule linked by [CSPLib](https://www.csplib.org/Problems/prob010/results/)
is transcribed with attribution in `data/golfers-10-reference.json`.
`golfers_reference.py` checks the transcription against its numeric mapping and
independently validates all ten weeks: 480 distinct pairs meet, with no repeats.
Each golfer meets three new partners per week and has only 31 possible partners,
so at most floor(31/3)=10 weeks are possible. The witness attains this bound.

See `results/golfers-optimality.md` for the readable schedule and proof, and
`results/golfers-optimality.json` for the recomputed certificate. This reference
is separate from local DFS outputs, which continue to record five weeks found
and a resource limit for six weeks. No external schedule is used by `solve_dfs`.

Regenerate all outputs, recheck saved solutions and run the tests with:

```sh
python3 reproduce.py
```

This uses only the Python standard library and requires no internet. It replaces
files in `results/` with current runs, so measured times may change. The bounded
DFS result may also depend on machine speed. The verification checks the 14 baseline solutions, plus successful saved
benchmark trials, including the published witness; the test suite has 34 passing tests.

## Git workflow

`docs/REQUIREMENTS.md` maps each requirement to its implementation, explanation
and saved evidence. Keep source code, documentation, fixtures, tests and the
verified results in Git. Python caches and local environments are ignored.

From this directory, when ready to create your repository:

```sh
git init
git add .
git commit -m "Implement uninformed search assignment"
```

Run `python3 reproduce.py` before committing updated results. Execution times
may change between runs; review generated changes with `git diff`.

## Watch Social Golfers run step by step

```sh
python3 main.py golfers --groups 2 --players-per-group 2 --weeks 3 --trace --delay 0.3 --time-limit 60
```

Trace messages show the fixed first week, assignments, rejected repeated pairs,
completed weeks and the goal. For a small example that also undoes choices:

```sh
python3 main.py golfers --groups 3 --players-per-group 2 --weeks 5 --trace --delay 0.1 --time-limit 60
```

`BACKTRACK` means a choice led to a dead end and was undone. `REJECT` means a
candidate was never assigned because it would repeat a pair. `--delay` is the
number of seconds between trace messages; use `--trace` alone for full speed.
Printing and deliberate pauses count toward the time limit, so traced timings
should not be compared with benchmark runs. Press Ctrl+C to stop a demonstration.

With two groups of two, there are four players. Each can meet only three other
players, one per week, so seven weeks is rejected by the upper bound before any
search starts. `best_weeks_found: 0` in that run means no schedule was returned
for the requested seven-week instance; it does not mean zero weeks are feasible.
Use `--maximize --weeks 7` to try increasing week counts up to the bound instead.

## Measure runtime and practical limits

In the UI choose an algorithm, then **Run mode → Measure limits**. Set the
range, step, samples, per-trial time and total budget. This compares Sudoku
empty-cell counts, Social Golfers week counts, Latin Square sizes or one search
tree's exploration depths. Existing relevant settings, including node/frontier
budgets and Latin symmetry, are retained. Trace and animation are disabled so
measured solver time excludes presentation delays.

Results show solved/tested counts, median and slowest successful times, the
resource that stopped unfinished trials, peak frontier, and the largest observed
success. Charts show observed duration, including budget-stopped cases. This
is an empirical study of the tested cases, not a universal maximum or an ETA.
For trees, completing a depth budget and finding a goal are reported separately.

For Sudoku, generated inputs come from a valid completed grid with positions
removed using a recorded seed. Each count uses multiple seeds; uniqueness is not
checked. Even an empty grid has completions, but row-major BFS may exceed its
queue budget before finding one. Unique standard Sudoku puzzles require at least
17 clues (at most 64 blanks): see
[McGuire, Tugemann and Civario](https://arxiv.org/abs/1201.0749). This theoretical
bound does not guarantee uniqueness for every 17-clue input.

The **Measured examples & mathematical limits** panel shows previous timings
for exact examples and explains the mathematical and practical distinctions for
each problem. Use fresh benchmarks for your computer rather than extrapolating
from a blank count alone. Saved benchmark results are in `results/benchmark-*.json`.

CLI example:

```sh
python3 benchmarks.py --algorithm sudoku --from 25 --to 65 --step 10 --samples 3 --seconds 0.5 --total-seconds 10 --output results/benchmark-sudoku.json
```

`python3 reproduce.py` also regenerates the four saved benchmark sweeps.
