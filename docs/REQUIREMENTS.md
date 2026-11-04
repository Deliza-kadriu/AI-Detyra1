# Assignment requirement map

The assignment brief is `Detyra1.md`; `../report.md` explains the implementation
and its assumptions. All commands below run from the project root with Python
3.10+ and no external packages or network access.

| Requirement | Implementation / explanation | Evidence |
| --- | --- | --- |
| Social Golfers: model and representation | `report.md`, section 1; `social_golfers.GolfersProblem` | Variables, domains, weekly partitions and pair constraints |
| Social Golfers: objective | `report.md`, section 1 | Repeated-pair excess; independently counted by `validate_golfers.py` |
| Social Golfers: landscape | `weekly_partitions()`, `landscape()`; report | `python3 main.py --landscape` |
| Social Golfers: DFS/backtracking | `social_golfers.solve_dfs` | `results/golfers-32.json`; `tests/test_golfers.py` |
| Social Golfers: maximum weeks | `golfers_reference.py`; report section 1 | Attributed published witness and matching upper bound in `results/golfers-optimality.md` |
| Sudoku: model and representation | `report.md`, section 2; `sudoku.py` | Cell variables, 1..9 domains, fixed clues, row/column/box constraints |
| Sudoku: objective | `report.md`, section 2 | Complete-board duplicate excess; `validate_sudoku.py` |
| Sudoku: landscape | `sudoku.landscape`; report | Per-puzzle values in `results/sudoku.json` |
| Sudoku: BFS with backtracking | `sudoku.solve_bfs`; report's interpretation subsection | FIFO expansion, independent states and branch rejection; `tests/test_sudoku.py` |
| Sudoku: Easy, Medium, Hard | `data/sudoku.json` | All three solved and independently validated in `results/sudoku.json` |
| Latin Square: model and representation | `report.md`, section 3; `latin_square.py` | Cell variables, 1..n domains and row/column constraints |
| Latin Square: objective | `report.md`, section 3 | Complete-square duplicate excess; `validate_latin.py` |
| Latin Square: landscape | `latin_square.landscape`; report | Raw and symmetry-reduced candidate counts |
| Latin Square: IDDFS/backtracking | `latin_square.solve_iddfs` | `results/latin-5.json`, `results/latin-3-classic.json`; `tests/test_latin.py` |
| 8-Puzzle search tree | `search_trees/problems.py`, `generate.py`; report section 4 | `results/search-trees.md`: depth-3 partial tree and two-move solution |
| Missionaries and Cannibals search tree | Same modules; report section 4 | Reachable graph represented as a spanning tree; 11-crossing solution |
| Rotating Workforce Scheduling search tree | Same modules; report section 4 | Legal-prefix tree, six-day roster, explicit chosen rules |

## What the results establish

- The local Social Golfers DFS found five weeks within its recorded budget. The
  mathematical optimum of ten is supported by a separately attributed published
  schedule, independently checked against every constraint. It is not claimed
  as a ten-week discovery by our DFS.
- Sudoku uses ordinary FIFO BFS with independent boards and rejection of failed
  branches. This is the documented interpretation of "BFS with Backtracking";
  it does not perform recursive DFS assignment/undo. Level names describe the
  generated demonstrations, not certified human difficulty or unique solutions.
- Latin Square uses actual repeated depth-limited exploration. The normal mode
  fixes the first row and column by symmetry; `--literal-deepening` disables that
  reduction. The optional known-depth shortcut is off in recorded runs.
- Search-tree initial states and workforce rules were chosen explicitly because
  the brief does not specify instances. The 8-Puzzle tree is partial. Repeated
  states in the two cyclic problems appear as reference leaves.

## Verification and Git

```sh
python3 reproduce.py
python3 verify_results.py
```

`reproduce.py` regenerates search outputs and runs all checks. Verification
validates saved solutions without rerunning searches. Commit the source,
documentation, fixtures, tests and verified results to Git; the project
`.gitignore` excludes Python caches and local environments. See `../README.md`
for the initial Git commands.

## Interactive demonstration

Run `python3 ui_server.py` to open the local UI. The algorithm selector reveals
relevant inputs; Run, Stop, live trace speed and JSON export support classroom
presentation. It executes the same solvers and independent validators as the CLI.
`ui/` contains the HTML/CSS/JavaScript; `demo_runner.py` isolates each experiment.
See the README for budgets, sample presentation order and startup options.

## Limit and runtime experiments

The UI's Measure limits mode sweeps Sudoku blank counts, Golfers weeks, Latin
Square sizes or tree depth. `benchmarks.py` records trace-free timings, seeded
inputs, per-trial validation, budget stops and the largest observed success.
Prior exact-example timings and mathematical limits appear in a separate panel.
The distinction between practical completion, existence and uniqueness is
explained in the report; no sampled largest success is called a universal limit.
