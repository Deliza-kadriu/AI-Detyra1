# Ten-week reference schedule and optimality check

**This is a published reference witness, not a result found by our DFS.**

Source: [Social Golfer Problem, Ed Pegg Jr., Math Games, August 14, 2007](https://web.archive.org/web/20130516045754/http://www.maa.org/editorial/mathgames/mathgames_08_14_07.html).
Located via [CSPLib results](https://www.csplib.org/Problems/prob010/results/).

Transcribed the 32-golfer Day0..Day9 table; map A..P to 0..15, a..p to 16..31. Case is significant; order is preserved.

| Week | Group 1 | Group 2 | Group 3 | Group 4 | Group 5 | Group 6 | Group 7 | Group 8 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0,1,2,3 | 4,5,6,7 | 8,9,10,11 | 12,13,15,14 | 16,17,18,19 | 20,21,22,23 | 24,25,26,27 | 28,29,30,31 |
| 2 | 0,4,8,28 | 1,22,18,7 | 3,5,10,31 | 26,15,19,21 | 12,16,20,24 | 2,23,17,6 | 25,13,30,11 | 27,9,29,14 |
| 3 | 0,27,30,21 | 1,23,26,28 | 3,13,6,24 | 5,16,11,14 | 12,17,7,10 | 2,15,20,9 | 4,25,18,31 | 22,8,19,29 |
| 4 | 0,18,24,11 | 1,25,19,10 | 3,26,17,9 | 5,22,30,15 | 21,6,14,31 | 2,8,27,16 | 4,23,12,29 | 13,20,7,28 |
| 5 | 0,22,13,10 | 1,4,27,15 | 3,8,30,7 | 23,19,24,14 | 17,20,11,31 | 2,25,21,28 | 5,12,18,9 | 26,16,6,29 |
| 6 | 0,23,9,31 | 1,5,24,29 | 3,18,28,14 | 8,13,17,21 | 27,20,6,10 | 2,12,30,19 | 4,22,26,11 | 25,15,16,7 |
| 7 | 0,5,19,20 | 1,30,6,9 | 3,4,16,21 | 23,27,13,18 | 15,24,10,28 | 2,7,11,29 | 22,25,17,14 | 8,26,12,31 |
| 8 | 0,15,17,29 | 1,13,16,31 | 3,22,27,12 | 26,30,18,20 | 21,7,24,9 | 2,4,10,14 | 5,23,8,25 | 19,6,11,28 |
| 9 | 0,25,12,6 | 1,8,20,14 | 3,23,15,11 | 22,16,9,28 | 18,21,10,29 | 2,5,26,13 | 4,30,17,24 | 27,19,7,31 |
| 10 | 0,26,7,14 | 1,12,21,11 | 3,25,20,29 | 5,27,17,28 | 8,15,18,6 | 2,22,24,31 | 4,13,19,9 | 23,30,16,10 |

## Independent checks

- Exactly 32 players, partitioned into eight groups of four every week.
- No repeated pair; duplicate-excess objective is zero.
- 480 distinct pairs meet; each player meets 30 different partners.
- The 16 unmet pairs are disjoint: each player misses one partner.

## Why ten is the maximum

Each player meets three new partners per week and has only 31 possible partners.
Thus 3*w <= 31, so w <= floor(31/3) = 10. The independently validated
ten-week witness attains this bound, proving that the maximum is ten.

The saved local DFS experiment still found five weeks and hit its node
budget while searching for six. This reference resolves the mathematical
question without claiming that the local DFS discovered the optimum.
