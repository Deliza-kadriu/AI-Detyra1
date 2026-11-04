# Sources and review notes

Reviewed on 2026-11-04:

- Assignment: https://github.com/adrianymeri/Artificial-Intelligence-2026/blob/main/Detyra1.md
- Repository and course syllabus: https://github.com/adrianymeri/Artificial-Intelligence-2026

The repository currently lists `README.md`, `Detyra1.md` and `LICENSE`.
The syllabus covers problem representations, objective functions, search-space
calculations, DFS/BFS/iterative deepening and constraint satisfaction.

The accompanying `Detyra1.md` was copied from the existing workspace file
`../detyra1-ready-sample/docs/Detyra1.md` (path relative to the project root).
Its substantive requirements were compared with the online brief during setup.
It is a local transcription, not a byte-for-byte download of the current upstream
file. Direct shell download was unavailable because host resolution failed.
The official link above remains authoritative.

Existing sample solvers were not copied into this project. Initial models and
Python scaffolding were prepared with Codex assistance.

Two details need explicit treatment in the final report:

- "BFS with Backtracking" is the brief's wording. Ordinary BFS stores a FIFO
  frontier of independent partial boards; inconsistent children can be rejected
  without recursive DFS. This interpretation is implemented in `sudoku.py` and explained in `report.md`.
- Search-tree initial states, depth limits and workforce rules are not specified
  in the brief. The chosen instances and rules are now documented in `report.md` and `search_trees/problems.py`.

Sudoku fixtures were generated locally from a cyclic valid completed board,
with deterministic seed 2026 and 25/35/45 removed clues. They are demonstration
levels, not externally sourced or certified benchmark puzzles. See
`data/sudoku.json` and the Sudoku report section for the exact construction.

## Published ten-week reference witness

Accessed 2026-11-04 via https://www.csplib.org/Problems/prob010/results/.
The linked archived article is Ed Pegg Jr., "Social Golfer Problem", Math Games,
August 14, 2007:
https://web.archive.org/web/20130516045754/http://www.maa.org/editorial/mathgames/mathgames_08_14_07.html

The 32-golfer Day0..Day9 table was manually transcribed into
`data/golfers-10-reference.json`. Transformation: map A..P to IDs 0..15 and
a..p to 16..31, preserving case and group order. The article credits Alejandro
Aguado's design-based construction. We independently validated the numeric
schedule rather than treating the source claim alone as proof of feasibility.
This attributed reference is never used to guide or seed the local DFS.

CSPLib's specification page contains an old statement that the optimum is
unknown, while its results page links the ten-week witness. The executable
witness check and matching mathematical upper bound resolve that inconsistency
for this assignment.

## Sudoku uniqueness bound

Gary McGuire, Bastian Tugemann and Gilles Civario, "There is no 16-Clue Sudoku:
Solving the Sudoku Minimum Number of Clues Problem", arXiv:1201.0749 (v2, 2013),
https://arxiv.org/abs/1201.0749, accessed 2026-11-04. The study establishes the
17-clue minimum for unique standard Sudoku puzzles. We use 81-17=64 as a bound
on blanks for uniquely solvable puzzles, not as a runtime limit or a uniqueness
claim about the generated examples. Benchmark timing claims come from local
measurements, not this paper.
