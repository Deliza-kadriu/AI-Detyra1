# Detyra 1 — Initial report

Status: all four assignment sections implemented and measured. A separately attributed, independently validated ten-week reference witness establishes the Social Golfers optimum; local DFS results remain distinct.
Assignment source and interpretation notes: `docs/SOURCES.md`.

## 1. Social Golfers

For g groups of p players, n = g*p. Represent a schedule as
`schedule[week][group] = list of player IDs`, with IDs 0..n-1.
Every week partitions all players into g disjoint groups of size p.
Each unordered player pair may occur together at most once across all weeks.

For a complete schedule satisfying weekly partitions, let c(a,b) count weeks
when players a and b meet. Minimize F = sum(max(0, c(a,b)-1)) over a<b.
A feasible schedule has F=0. To maximize weeks, solve feasibility for increasing
w; finding one schedule does not establish the maximum.

With unordered groups and players, the number of weekly partitions is
P = n! / ((p!)^g * g!). The complete candidate space is P^w before pair
constraints; weeks are ordered. This counts complete candidates, not all tree
nodes. For p>1, w <= floor((n-1)/(p-1)): a player meets p-1 new players each week.
For 32 players in groups of four, w <= 10. The local DFS runs below do not attain
this bound; the separately validated published witness does.

### Representation and transitions

Equivalently, define a variable X[t,a] for each week t and player a with domain
0..g-1 (group labels). Each group contains exactly p players, and for each pair
a<b the equality X[t,a]=X[t,b] holds in at most one week. The implementation
uses nested lists for these assignments and a bit mask of previous partners per
player. Partial state consists of completed weeks, completed groups in the
current week, a group under construction, and unassigned players.

DFS adds one player at a time in ascending numeric order. A candidate is rejected
if it has met anyone already in the group. On assignment, partner bits are set
in both directions. On failure, the player and precisely those bits are removed.
A full group leads to the next group; a full week leads to the next week. The
goal is w complete weeks. Exhaustion returns infeasible; a resource limit raises
a separate exception and is reported as unresolved. The objective is a feasibility
test, not a heuristic used to rank candidates.

Week one is fixed to consecutive player IDs: every first-week partition can be
relabelled this way. Within later weeks, each group's first member is the smallest
unassigned player and the remaining members increase. Sorting groups and their
members removes equivalent permutations without excluding feasible schedules.
Consequently the search fixes one of P first-week choices and explores at most
P^(w-1) complete schedules before additional pair pruning. This is an upper
bound on leaves, not the measured node count.

### Complexity and instrumentation

Time is exponential in the number of player assignments. A loose bound for the
fixed-first-week tree is O(n^(n*(w-1))); legality checks scan at most p partners.
The active state and recursion use O(n*w + n^2) bits/entries up to representation
factors: a schedule/stack of O(n*w) and n partner bit masks of n bits each. Python
recursion and integer representation add overhead; very large inputs may hit
Python's recursion limit. This implementation targets small coursework cases.

`expanded_nodes` counts entered week, partition and group-fill calls, including
terminal calls; it is not the number of unique schedules. `backtracks` counts
undone player/group/week choices. `max_depth` counts assigned player slots,
including the fixed first week; it is not a measured byte count or Python call
stack depth. Elapsed time uses `perf_counter`.

### Measured results

Actual output: `results/golfers-32.json`, generated with Python 3.13.5 on
2026-11-04 using:

```sh
python3 social_golfers.py --maximize --weeks 10 --time-limit 3 --output results/golfers-32.json
```

| Weeks | Outcome | Entered nodes | Backtracks |
| --- | --- | ---: | ---: |
| 1 | Solved, independently validated | 1 | 0 |
| 2 | Solved, independently validated | 43 | 0 |
| 3 | Solved, independently validated | 85 | 0 |
| 4 | Solved, independently validated | 127 | 0 |
| 5 | Solved, independently validated | 169 | 0 |
| 6 | One-million-node limit | 1000000 | 838618 |

The six-week attempt took approximately 1.22 seconds and the successful runs
each took less than 0.001 seconds on this machine. Each successful result has
objective zero. Numeric order finds the first five weeks without undoing choices;
the six-week attempt demonstrates the rapid growth of search. Independent tests
also solve a 3-group, 2-player, 5-week instance after backtracking. Two groups
of three players cannot play two weeks: DFS exhaustively rejects this instance
even though the simple pair bound permits two weeks.

The local DFS experiment alone establishes five feasible weeks and an upper
bound of ten. It does not resolve the exact maximum. The published witness
in the next subsection separately resolves that mathematical question. Increasing
DFS limits may help search but does not guarantee quick discovery of the optimum.
`validate_golfers.py` independently reconstructs pair counts and checks every
player appears exactly once each week; it does not import the solver.

### What happened during the six-week attempt?

The program solved separate instances for one, two, three, four and five weeks.
It then started a new search for a complete six-week schedule. It did not lock
the previously printed five-week schedule and only try to append another week:
the first week remained fixed by symmetry, but weeks two onward could change.

As the search progressed, more player pairs had already met. A candidate player
could join a group only if they had never met any current member. When a group
or a later week could not be completed, DFS undid assignments and tried other
choices. Backtracking could reach earlier weeks to change their groups as well.

The six-week attempt entered 1,000,000 search nodes and made 838,618 backtracking
steps. It stopped after approximately 1.22 seconds because it reached the node
limit, before reaching the separate three-second time limit. No complete
six-week schedule was found within that budget. These counts cover the entire
six-week search, not just assignments in the sixth week.

This outcome is recorded as `resource_limit`, not `infeasible`. Proving
infeasibility would require exhausting the remaining search or a separate
mathematical argument. Therefore, this run does not establish that six weeks
are impossible or that five weeks is the maximum.

The increasing-weeks experiment stops at its first unsuccessful attempt, so
weeks seven through ten were not attempted. A schedule for any of those lengths
would also yield a six-week schedule by deleting later weeks. The saved result
for this DFS experiment is consequently five verified weeks, an upper bound of
ten, and no exact maximum established by the search. The complete attempt and
its statistics are preserved in
`results/golfers-32.json`.

### Published witness: the maximum is ten weeks

The unresolved local search does not mean the underlying mathematical question
is open. [CSPLib's results page](https://www.csplib.org/Problems/prob010/results/)
links a published ten-week schedule in
[Ed Pegg Jr.'s Math Games article](https://web.archive.org/web/20130516045754/http://www.maa.org/editorial/mathgames/mathgames_08_14_07.html)
(August 14, 2007). The article attributes the construction to Alejandro Aguado's
use of resolvable group divisible designs. We preserve the table's case-sensitive
labels and map A..P to 0..15 and a..p to 16..31, without changing the groups.

`data/golfers-10-reference.json` records the source, labelled table and numeric
transcription. `golfers_reference.py` first checks that the mapping matches, then
uses the independent schedule validator. It confirms ten valid weekly partitions,
480 distinct player pairs, no repeated pair, and 30 different partners per player.
The 16 unmet pairs are disjoint, leaving each player with one partner not met.

Since each week adds three new partners and only 31 other players exist,
3*w <= 31 implies w <= 10. The checked ten-week witness attains the bound,
so the maximum is exactly ten. No exhaustive infeasibility search is needed.
The numeric schedule and proof are in `results/golfers-optimality.md`; the
machine-readable checks are in `results/golfers-optimality.json`.

This is explicitly a published reference witness, not a solution found by our
DFS. The assignment's DFS implementation and its measured five-week result
remain unchanged. Reproduce the reference check with:

```sh
python3 main.py golfers-reference
```

## 2. Sudoku

State: immutable 9x9 tuple of tuples; zero denotes an empty cell. Variables are
initially empty cells, with domain 1..9. Clues remain fixed. Every row, column
and 3x3 box must contain 1..9 exactly once in a complete solution.

For complete candidate boards preserving clues, minimize duplicate excess summed
over all rows, columns and boxes: for each unit U, sum over d=1..9 of
max(0, count_U(d)-1). A complete board with F=0 is a solution. A partial board
with no duplicates is not yet a goal.

With e empty cells, the raw complete candidate space is 9^e. The unpruned tree
for fixed cell order has sum(9^k, k=0..e) nodes. Constraints reduce this space.

### BFS implementation and the brief's backtracking wording

`solve_bfs` uses `collections.deque`: remove the oldest board using `popleft`,
then append its legal children to the other end. The initially empty cells are
fixed in row-major order; at depth k, assign the kth cell. Candidate digits are
tried in ascending order 1..9. A successor copies the affected row into a new
immutable board and assigns exactly one digit. It is enqueued only if that digit
is absent from the row, column and box. No heuristic, recursive DFS or stored
solution is used.

All boards at depth k are processed before depth k+1. A board with no legal
children is a dead end and is discarded; alternatives already in the queue remain
available. The solver stops when a dequeued board has all initial blanks filled.
Because each step preserves consistency, this is a complete valid solution.
A fixed cell order gives each partial assignment a unique path, so duplicate
state detection is unnecessary. Input clues are checked before search.

The brief calls for "BFS with Backtracking". Ordinary recursive assignment/undo
backtracking explores depth first. This implementation interprets the wording as
BFS with constraint checking and rejection of unsuccessful branches: separate
immutable states retain the alternatives instead of undoing a shared board on a
recursive stack. It does not claim to perform recursive backtracking. This
interpretation should be confirmed with the instructor if recursive undo is
specifically required; replacing the FIFO search with DFS would change the
requested algorithm.

### Search space and complexity

With e initial blanks, the raw complete-assignment space is 9^e, and the complete
unpruned search tree contains (9^(e+1)-1)/8 nodes. This includes invalid digit
assignments; the actual BFS enqueues only consistent boards. All solutions are
at depth e, so BFS offers no shallower-goal advantage here. In the worst case,
time and frontier memory are exponential, O(9^e) for fixed-size boards. Each
successor retains a nine-row board representation, sharing unchanged immutable
rows. The measured peak frontier counts queued boards, not bytes of process RAM.

`expanded_nodes` counts dequeued boards, including the goal. `generated_nodes`
counts enqueued boards, including the input. `rejected_candidates` counts digits
rejected by row/column/box checks; `dead_ends` counts expanded incomplete boards
with no legal successor. `max_depth` counts filled initial blanks. These metrics
are separate from the raw landscape.

### Fixtures and measured results

The examples in `data/sudoku.json` are generated locally from the valid grid
`value(r,c) = (3*r + floor(r/3) + c) mod 9 + 1`, using zero-based coordinates.
For each level, remove the positions returned by
`random.Random(2026).sample(range(81), blanks)` with 25, 35 or 45 blanks.
These are nested examples from one grid, not independent benchmark puzzles.
They exercise branching and dead ends under the same deterministic BFS order.
The names Easy/Medium/Hard describe these demonstrations by clue count and
observed search effort. They are not certified human difficulty ratings and
solution uniqueness has not been established. The grid construction is only a
fixture-generation step; the solver is given the incomplete board alone.

Actual runs on 2026-11-04 with Python 3.13.5:

```sh
python3 sudoku.py --output results/sudoku.json
```

Limits per puzzle: 200,000 expanded nodes, 50,000 frontier states, ten seconds.
All three returned a complete solution and passed the independent validator.

| Level | Blanks | Raw landscape | Expanded boards | Peak frontier | Time (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Easy | 25 | 9^25 = 717897987691852588770249 | 46 | 4 | 0.000116 |
| Medium | 35 | 9^35 = 2503155504993241601315571986085849 | 76 | 6 | 0.000167 |
| Hard | 45 | 9^45 = 8727963568087712425891397479476727340041449 | 2637 | 468 | 0.005645 |

These timings describe one local run and can vary across machines. All solutions
have duplicate-excess objective zero and preserve every original clue.
`validate_sudoku.py` imports no solver code and independently checks complete
rows, columns, boxes and clue preservation. `tests/test_sudoku.py` additionally
checks solved boards, one-cell completion, invalid inputs, conflicting clues,
a consistent but impossible board, input immutability, and separate node,
frontier and time limits. Corrupted solutions are rejected independently.

### What happens when Sudoku search cannot finish?

If every queued branch is exhausted, the result is `infeasible`: no completion
exists for the given clues under the Sudoku rules. If a node, frontier or time
budget is reached first, the result is `resource_limit`. This says nothing about
whether a solution exists. BFS can accumulate many alternatives at the same
depth, so the explicit frontier limit protects memory usage for harder inputs.
The CLI records status and statistics for each case and continues to the next
example. It never labels a resource limit as proof of infeasibility.


## 3. Latin Square

State: n x n grid, with zero for unassigned cells. Variables are cells; each
domain is 1..n. Every number occurs once in each row and each column.
For complete candidates, minimize duplicate excess across rows and columns
using the same unit formula as Sudoku, without box constraints. Goal: complete
grid with zero conflicts.

The raw complete candidate space is n^(n*n), before row/column constraints.
For n=5 this is 5^25 = 298023223876953125. With one cell assigned per edge,
goal depth is n*n and the unpruned tree has sum(n^k, k=0..n*n) nodes.

### IDDFS and backtracking

The default solver fixes the first row and column to 1..n. This is a symmetry
reduction for an unconstrained Latin Square: relabel symbols to sort the first
row, then permute the remaining rows to sort the first column. It preserves
existence, although it does not enumerate every labelled square. This leaves
m=(n-1)^2 cells to assign in row-major order. The first row and column are fixed
before search, and depth counts only the remaining assignments.

IDDFS repeats depth-limited DFS for limits 0..m. Each iteration starts with a
fresh grid, row sets and column sets. Candidate values ascend 1..n; a value is
accepted only if absent from the current row and column. When a branch fails or
reaches the depth limit, the assignment is cleared and both sets are restored.
A goal requires all m remaining cells to be filled. Each iteration and its node
count are recorded in the JSON output. The solver returns the first valid square;
it does not optimize aesthetic properties or count all possible squares.

`--literal-deepening` disables symmetry reduction and uses all n*n cells, with
limits 0..n*n, for a direct small-scale demonstration. The separate optional flag
`--goal-depth-pruning` can reject every limit below the known goal depth at the
root. It is disabled in both recorded runs, which therefore demonstrate actual
repeated exploration. No heuristic ordering or direct cyclic construction is
used to solve the square.

### Landscape, complexity and measurements

The earlier n^(n*n) formula describes all labelled complete candidates. With the
canonical border fixed, the raw candidate space falls to n^((n-1)^2), before
row/column checks. For n=5 this is 5^16=152587890625. The corresponding unpruned
assignment tree has sum(n^k, k=0..m) nodes. IDDFS re-expands shallow prefixes,
while retaining only one active branch. A loose time bound is O(n^m) for n>1
and the fixed-depth tree, with implementation overhead for assignments/checks;
space is O(n^2) for the grid, row/column sets and recursion stack. General large
inputs can still exceed the node, time or Python recursion limit.

`expanded_nodes` counts entered depth-limited DFS calls, including cutoffs and
goals, across all iterations. `backtracks` counts undone assignments.
`max_depth` counts free cells assigned in the active branch, not bytes of memory.
`validate_latin.py` independently checks dimensions, value ranges, row uniqueness,
column uniqueness and the zero-conflict objective.

Reproduction commands:

```sh
python3 main.py latin --size 5 --output results/latin-5.json
python3 main.py latin --size 3 --literal-deepening --output results/latin-3-classic.json
```

| Run | Free cells / goal depth | Iterations | Entered nodes | Backtracks | Validation |
| --- | ---: | ---: | ---: | ---: | --- |
| n=5, canonical border | 16 | 17 | 4914 | 4881 | PASS |
| n=3, no symmetry reduction | 9 | 10 | 326 | 307 | PASS |

The 5x5 output is:

```text
1 2 3 4 5
2 1 4 5 3
3 4 5 1 2
4 5 2 3 1
5 3 1 2 4
```

All integers 1..5 occur exactly once in every row and column. Tests cover n=1..5,
both search modes, state undo, limits and invalid outputs. Resource exhaustion
is reported separately from infeasibility. Every positive n has a Latin Square;
a resource limit indicates unfinished search, not nonexistence.

## 4. Search trees

### Construction and output format

Run `python3 main.py trees` to generate `results/search-trees.json` and
`results/search-trees.md`. Each node records its ID, parent ID, state, action,
depth and classification. Illegal actions are listed with rejection reasons at
the parent. BFS expands unique states in FIFO order. An edge to an already seen
state is retained as a repeated-state leaf with a reference to its original node;
its descendants are not expanded again. This is a BFS spanning tree of the
reachable state graph, not an infinite unfolding of cycles. The Markdown output
indents edges, labels cutoffs and marks the first solution path with `*`.

Search continues after finding the first goal to show other reachable branches
within the selected limits. Goals are terminal. A depth or node limit marks the
tree as truncated; a solution can still be valid in a truncated tree. Defaults
are problem-specific depth limits and 5,000 recorded nodes. No goal within a
truncated tree is an unresolved search, not proof of infeasibility.

### 8-Puzzle

Initial board: `123/456/078`; goal: `123/456/780`; 0 is the blank. A state is an
immutable sequence of nine tiles. Actions move the blank Up, Down, Left or Right
in that order; moves outside the board are rejected. Fixed initial and goal
boards use the same tile inventory. BFS with depth limit 3 constructs a partial
tree. The first shortest solution is Right, Right (two moves). This is a small
illustration, not a claim to enumerate the entire puzzle state graph.

### Missionaries and Cannibals

There are three missionaries, three cannibals and a boat carrying one or two
people. Initially all are on the left bank; the goal places everyone and the
boat on the right. State `(M_left, C_left, boat_bank)` uses 0=left, 1=right.
Actions carry (1M), (1C), (2M), (1M,1C), or (2C), in that order. Passengers must
be available on the departure bank. On either bank, cannibals may not outnumber
missionaries when missionaries are present. The boat cannot travel empty.

The first goal is at depth 11. The depth-12 construction exhausts reachable
unique non-goal states under these rules; repeated-state leaves prevent cycles.
The generated Markdown shows each crossing and both illegal and repeated branches.

### Rotating Workforce Scheduling

Because the brief supplies no staffing instance, this example explicitly chooses
three workers and a six-day repeating cycle. Each day requires one Day shift
(D), one Night shift (N) and one Off assignment (O). Each worker must have exactly
two of each shift per cycle, at most two consecutive working days and no
Night-to-Day transition, including the last-to-first-day boundary.

A single base pattern determines all workers: worker w on day d receives
`base[(d-2*w) mod 6]`, with zero-based indices. Thus workers follow cyclically
shifted copies of one pattern. State is a base-pattern prefix; actions append D,
N or O in that order. Prefixes are rejected when shift counts exceed two, an
assigned rest rule fails, or known daily assignments duplicate a shift. Complete
patterns additionally check all wraparound rest constraints. These are chosen
educational rules, not requirements stated by the assignment or a labor policy.

The first solution has base D,N,O,D,N,O:

| Worker | Day 1 | Day 2 | Day 3 | Day 4 | Day 5 | Day 6 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | D | N | O | D | N | O |
| 2 | N | O | D | N | O | D |
| 3 | O | D | N | O | D | N |

It satisfies coverage, equal shift counts, cyclic rotation and rest rules. At
depth 6 the tree exhausts all legal prefixes. Tests compare all 3^6=729 possible
base patterns with an independent complete-roster validator and verify that
no prefix of a feasible pattern is incorrectly pruned.

### Measured tree results and validation

| Problem | Tree nodes (including repeat leaves) | Expanded unique states | Peak frontier | Solution edges | Truncated |
| --- | ---: | ---: | ---: | ---: | --- |
| 8-puzzle | 19 | 6 | 8 | 2 | True |
| missionaries | 31 | 14 | 3 | 11 | False |
| workforce | 67 | 58 | 19 | 6 | False |

`validate_trees.py` imports no problem-generation code. It independently checks
parent/depth links, initial and goal states, every move or crossing in the path,
and the complete workforce roster including cycle boundaries. All three saved
paths pass. Tree tests cover repeated states, limits, parent corruption and
workforce pruning. Frontier counts measure queued unique-state nodes; recorded
node storage is additional memory. For depth d and branching factor b, the
unpruned BFS time and memory can grow as O(b^d); repeat-state suppression reduces
this for the two cyclic state graphs.

## Verification and remaining limitations

All four sections now have executable code, saved outputs, independent result
checks and tests. Run `python3 -m unittest discover -s tests -v` and
`python3 verify_results.py` from this directory. JSON files record timings and
search statistics; DFS/IDDFS record active assignment depth and BFS records peak
frontier. Counts are not byte-level memory measurements.

The mathematical Social Golfers maximum is established as ten using an attributed
published witness. Local DFS still finds only five within the saved budget and
does not discover that optimum. Sudoku level labels are generated demonstrations,
not certified difficulty ratings, and uniqueness is not established. The
8-Puzzle tree is intentionally partial; the workforce rules are an explicitly
chosen instance. The Sudoku section explains the interpretation of the brief's
"BFS with Backtracking" wording. Resource limits never prove infeasibility.

## Full reproduction

`python3 reproduce.py` regenerates all local solver outputs, search trees and the
published-witness certificate and bounded benchmark sweeps, then independently
revalidates baseline solutions and successful benchmark trials and runs 34 tests. It requires only the Python standard library and no internet.
Timings are measurements of one run and vary across machines. This command
overwrites generated files in `results/`; it never substitutes a reference
schedule for the DFS search result.

## Live DFS demonstration

Social Golfers supports `--trace` and optional `--delay SECONDS`. Trace lines
show assignments, rejected pairs, completed weeks, undo operations and the
termination reason. A useful backtracking example is
`python3 main.py golfers --groups 3 --players-per-group 2 --weeks 5 --trace`.
Adding `--delay 0.1 --time-limit 60` slows the display for study. Delays and
printing contribute to elapsed time; keep tracing off for benchmark runs.

## Demonstration interface

`python3 ui_server.py` opens a local browser interface backed by the same Python
solvers. `ui_server.py` serves static files and streams newline-delimited JSON
from one isolated `demo_runner.py` process per experiment. Selecting a problem
reveals its parameters. Trace callbacks expose actual search events; Sudoku and
Latin Square show cell states, and tree events show the current graph state.
The UI does not simulate search or substitute stored results for solver execution.

Runs support explicit cancellation, node/time/frontier budgets and independent
result validation. The overall demonstration cap is 125 seconds. Trace pauses
count toward search time; at 5,000 emitted steps tracing stops while computation
continues. Downloaded JSON is a separate UI run and does not overwrite the saved
coursework measurements. The published golf reference remains clearly labelled.

`tests/test_demo.py` covers all five experiment choices, custom Sudoku inputs,
limits, tracing without changed solutions, and live board snapshots. Browser
checks cover dynamic inputs, live events, stopping, invalid clues and tree output.

## Measured performance versus mathematical limits

The UI's **Measure limits** mode compares a range of inputs while disabling trace
callbacks and animation. It records Python/system metadata, generator seed,
node/frontier/time budgets, every trial's outcome, solver time and independent
validation. Sudoku varies blanks; Golfers varies weeks for fixed groups and
group size; Latin Square varies n using the selected symmetry settings; search
trees vary depth for a fixed instance. Neither the largest tested value nor the
largest successful value is automatically a mathematical limit.

The four sweeps in `results/benchmark-*.json` are generated by the commands in
`reproduce.py`. Timings below summarize one recorded run; reruns vary.

### Sudoku benchmark

| empty cells | Successful / tested | Median successful time (ms) | Resource stops | Cause |
| --- | --- | ---: | ---: | --- |
| 25 | 3/3 | 0.103 | 0 | — |
| 35 | 3/3 | 0.201 | 0 | — |
| 45 | 3/3 | 3.164 | 0 | — |
| 55 | 0/3 | — | 3 | Frontier |
| 65 | 0/3 | — | 3 | Frontier |


### Golfers benchmark

| weeks | Successful / tested | Median successful time (ms) | Resource stops | Cause |
| --- | --- | ---: | ---: | --- |
| 1 | 1/1 | 0.013 | 0 | — |
| 2 | 1/1 | 0.062 | 0 | — |
| 3 | 1/1 | 0.222 | 0 | — |
| 4 | 1/1 | 0.148 | 0 | — |
| 5 | 1/1 | 0.200 | 0 | — |
| 6 | 0/1 | — | 1 | Node |
| 7 | 0/1 | — | 1 | Node |


### Latin benchmark

| square size | Successful / tested | Median successful time (ms) | Resource stops | Cause |
| --- | --- | ---: | ---: | --- |
| 1 | 1/1 | 0.005 | 0 | — |
| 2 | 1/1 | 0.009 | 0 | — |
| 3 | 1/1 | 0.023 | 0 | — |
| 4 | 1/1 | 0.109 | 0 | — |
| 5 | 1/1 | 2.475 | 0 | — |
| 6 | 0/1 | — | 1 | Node |


### Trees benchmark

| depth limit | Successful / tested | Median successful time (ms) | Resource stops | Cause |
| --- | --- | ---: | ---: | --- |
| 0 | 1/1 | 0.003 | 0 | — |
| 2 | 1/1 | 0.020 | 0 | — |
| 4 | 1/1 | 0.034 | 0 | — |
| 6 | 1/1 | 0.203 | 0 | — |
| 8 | 1/1 | 0.778 | 0 | — |

The Sudoku sweep uses seeds 2026..2028 and a 0.5-second per-trial budget,
200,000 node limit and 50,000 frontier limit. The three 45-blank cases solved,
whereas all sampled 55- and 65-blank cases hit the frontier limit. These generated
boards are known to admit a completion because clues were removed from a valid
grid; the stops demonstrate algorithmic resource limits, not infeasibility.
The sweep samples counts 25,35,45,55,65, not every possible blank count.

Sudoku has three different questions: existence of any completion, uniqueness,
and practical BFS runtime. Even 81 blanks admit completions. For a unique
standard Sudoku solution, at least 17 clues are necessary, so at most 64 blanks
are possible; this follows from the
[minimum-clue study](https://arxiv.org/abs/1201.0749) by McGuire, Tugemann and
Civario. A specific 17-clue puzzle need not be uniquely solvable. Our solver
finds one completion and does not establish uniqueness. Thus neither 64 nor
our observed 45 is a general performance threshold for BFS.

Golfers' pair-counting bound and the published ten-week witness establish the
mathematical optimum for 32 players, independently of local DFS runtime. Latin
Squares exist for every positive size (a cyclic construction suffices), while
IDDFS is limited by available computation. For trees, success in the table means
completing the requested depth budget without a node/time stop; goal discovery
is separate and recorded per trial. The depth-0 tree is explored completely
within its requested limit even though it has no goal.

Median successful time excludes unfinished trials. Observed-duration chart bars
include them and label resource stops, so a quick stop is never presented as a
quick solve. Node/frontier counts describe search effort, not measured bytes.
Total-budget exhaustion marks unattempted trials as untested. The exported
measurements can be used in a presentation without claiming a universal runtime
or a maximum derived from a limited sample.
