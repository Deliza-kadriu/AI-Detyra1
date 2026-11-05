# Generated results

`golfers-32.json` records actual Social Golfers DFS runs for weeks 1..6:
complete inputs, schedules, search statistics, independent validation and the
best-weeks summary. Weeks 1..5 pass; week 6 hit the node limit. The exact
maximum is not established by that DFS run. A separate reference witness now
establishes the mathematical maximum as ten. See `report.md` for the reproduction command.

`sudoku.json` records actual FIFO BFS runs for the three generated demonstration
levels, including input clues, complete solutions, raw search spaces, resource
budgets, timings, frontier sizes and independent validation. All three pass.
Reproduce with `python3 main.py sudoku --output results/sudoku.json`.

`latin-5.json` records the symmetry-reduced 5x5 IDDFS run;
`latin-3-classic.json` records unrestricted 3x3 iterative deepening. Both pass
independent Latin Square validation.

`search-trees.md` and `search-trees.json` contain all three trees, classifications,
rejected actions, solution paths, statistics and independent path validation.
The 8-Puzzle tree is intentionally truncated.

Run `python3 verify_results.py` to recheck saved solutions without rerunning search.

`golfers-optimality.md` contains an attributed ten-week reference schedule and
matching upper-bound proof. `golfers-optimality.json` records its independently
recomputed validation. These are reference evidence, not local DFS outputs.

`python3 reproduce.py` regenerates all output files and runs verification/tests.

`benchmark-sudoku.json`, `benchmark-golfers.json`, `benchmark-latin.json` and
`benchmark-trees.json` record bounded, trace-free parameter sweeps. They include
seeds/settings, trial inputs/results, validation and empirical summaries. The
recorded largest success is not a universal maximum or runtime prediction.
`reproduce.py` regenerates them and `verify_results.py` checks successful
completions and empirical summary consistency.

`golfers-restarts-32.json` retains seven weeks from enhanced restarted DFS.
`golfers-explore-32.json` retains nine weeks from structure-guided DFS while
reporting that the ten-week target was not reached. `golfers-structured-9.json`
records successfully reaching a nine-week target. These are locally generated
search outputs with independent prefix validation, distinct from the numeric
baseline and the published ten-week reference.
