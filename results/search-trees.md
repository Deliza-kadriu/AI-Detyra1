# Generated search trees

BFS spanning trees: repeated states are shown as leaves referring to their first node.
Rejected actions appear below their parent. `*` marks the first solution path.

## 8-puzzle

3x3 board, 0=blank; start 123/456/078; goal 123/456/780. Order: Up, Down, Left, Right.

Truncated: **True**. Depth limit: 3. Expanded nodes: 6. Peak frontier: 8.

```text
* #0 Start: (1, 2, 3, 4, 5, 6, 0, 7, 8) [expanded]
  x Down: Blank would leave the board.
  x Left: Blank would leave the board.
  - #1 Up: (1, 2, 3, 0, 5, 6, 4, 7, 8) [expanded]
    x Left: Blank would leave the board.
    - #3 Up: (0, 2, 3, 1, 5, 6, 4, 7, 8) [expanded]
      x Up: Blank would leave the board.
      x Left: Blank would leave the board.
      - #9 Down: (1, 2, 3, 0, 5, 6, 4, 7, 8) [repeated -> #1]
      - #10 Right: (2, 0, 3, 1, 5, 6, 4, 7, 8) [depth_limit]
    - #4 Down: (1, 2, 3, 4, 5, 6, 0, 7, 8) [repeated -> #0]
    - #5 Right: (1, 2, 3, 5, 0, 6, 4, 7, 8) [expanded]
      - #11 Up: (1, 0, 3, 5, 2, 6, 4, 7, 8) [depth_limit]
      - #12 Down: (1, 2, 3, 5, 7, 6, 4, 0, 8) [depth_limit]
      - #13 Left: (1, 2, 3, 0, 5, 6, 4, 7, 8) [repeated -> #1]
      - #14 Right: (1, 2, 3, 5, 6, 0, 4, 7, 8) [depth_limit]
  * #2 Right: (1, 2, 3, 4, 5, 6, 7, 0, 8) [expanded]
    x Down: Blank would leave the board.
    - #6 Up: (1, 2, 3, 4, 0, 6, 7, 5, 8) [expanded]
      - #15 Up: (1, 0, 3, 4, 2, 6, 7, 5, 8) [depth_limit]
      - #16 Down: (1, 2, 3, 4, 5, 6, 7, 0, 8) [repeated -> #2]
      - #17 Left: (1, 2, 3, 0, 4, 6, 7, 5, 8) [depth_limit]
      - #18 Right: (1, 2, 3, 4, 6, 0, 7, 5, 8) [depth_limit]
    - #7 Left: (1, 2, 3, 4, 5, 6, 0, 7, 8) [repeated -> #0]
    * #8 Right: (1, 2, 3, 4, 5, 6, 7, 8, 0) [goal]
```

Solution path: #0 → #2 → #8

## missionaries

3 missionaries, 3 cannibals, capacity 2; boat carries 1 or 2 people. State (M left, C left, boat bank); 0=left, 1=right. Both banks must be safe.

Truncated: **False**. Depth limit: 12. Expanded nodes: 14. Peak frontier: 3.

```text
* #0 Start: (3, 3, 0) [expanded]
  x 1M,0C L->R: Cannibals outnumber missionaries on a bank.
  x 2M,0C L->R: Cannibals outnumber missionaries on a bank.
  - #1 0M,1C L->R: (3, 2, 1) [expanded]
    x 1M,0C R->L: Passengers unavailable on departure bank.
    x 2M,0C R->L: Passengers unavailable on departure bank.
    x 1M,1C R->L: Passengers unavailable on departure bank.
    x 0M,2C R->L: Passengers unavailable on departure bank.
    - #4 0M,1C R->L: (3, 3, 0) [repeated -> #0]
  * #2 1M,1C L->R: (2, 2, 1) [expanded]
    x 0M,1C R->L: Cannibals outnumber missionaries on a bank.
    x 2M,0C R->L: Passengers unavailable on departure bank.
    x 0M,2C R->L: Passengers unavailable on departure bank.
    * #5 1M,0C R->L: (3, 2, 0) [expanded]
      x 2M,0C L->R: Cannibals outnumber missionaries on a bank.
      x 1M,1C L->R: Cannibals outnumber missionaries on a bank.
      - #9 1M,0C L->R: (2, 2, 1) [repeated -> #2]
      - #10 0M,1C L->R: (3, 1, 1) [repeated -> #3]
      * #11 0M,2C L->R: (3, 0, 1) [expanded]
        x 1M,0C R->L: Passengers unavailable on departure bank.
        x 2M,0C R->L: Passengers unavailable on departure bank.
        x 1M,1C R->L: Passengers unavailable on departure bank.
        * #12 0M,1C R->L: (3, 1, 0) [expanded]
          x 1M,0C L->R: Cannibals outnumber missionaries on a bank.
          x 1M,1C L->R: Cannibals outnumber missionaries on a bank.
          x 0M,2C L->R: Passengers unavailable on departure bank.
          - #14 0M,1C L->R: (3, 0, 1) [repeated -> #11]
          * #15 2M,0C L->R: (1, 1, 1) [expanded]
            x 1M,0C R->L: Cannibals outnumber missionaries on a bank.
            x 0M,1C R->L: Cannibals outnumber missionaries on a bank.
            x 0M,2C R->L: Cannibals outnumber missionaries on a bank.
            - #16 2M,0C R->L: (3, 1, 0) [repeated -> #12]
            * #17 1M,1C R->L: (2, 2, 0) [expanded]
              x 1M,0C L->R: Cannibals outnumber missionaries on a bank.
              x 0M,1C L->R: Cannibals outnumber missionaries on a bank.
              x 0M,2C L->R: Cannibals outnumber missionaries on a bank.
              * #18 2M,0C L->R: (0, 2, 1) [expanded]
                x 1M,0C R->L: Cannibals outnumber missionaries on a bank.
                x 1M,1C R->L: Cannibals outnumber missionaries on a bank.
                x 0M,2C R->L: Passengers unavailable on departure bank.
                * #20 0M,1C R->L: (0, 3, 0) [expanded]
                  x 1M,0C L->R: Passengers unavailable on departure bank.
                  x 2M,0C L->R: Passengers unavailable on departure bank.
                  x 1M,1C L->R: Passengers unavailable on departure bank.
                  - #22 0M,1C L->R: (0, 2, 1) [repeated -> #18]
                  * #23 0M,2C L->R: (0, 1, 1) [expanded]
                    x 2M,0C R->L: Cannibals outnumber missionaries on a bank.
                    x 1M,1C R->L: Cannibals outnumber missionaries on a bank.
                    * #24 1M,0C R->L: (1, 1, 0) [expanded]
                      x 0M,1C L->R: Cannibals outnumber missionaries on a bank.
                      x 2M,0C L->R: Passengers unavailable on departure bank.
                      x 0M,2C L->R: Passengers unavailable on departure bank.
                      - #27 1M,0C L->R: (0, 1, 1) [repeated -> #23]
                      * #28 1M,1C L->R: (0, 0, 1) [goal]
                    - #25 0M,1C R->L: (0, 2, 0) [expanded]
                      x 1M,0C L->R: Passengers unavailable on departure bank.
                      x 2M,0C L->R: Passengers unavailable on departure bank.
                      x 1M,1C L->R: Passengers unavailable on departure bank.
                      - #29 0M,1C L->R: (0, 1, 1) [repeated -> #23]
                      - #30 0M,2C L->R: (0, 0, 1) [repeated -> #28]
                    - #26 0M,2C R->L: (0, 3, 0) [repeated -> #20]
                - #21 2M,0C R->L: (2, 2, 0) [repeated -> #17]
              - #19 1M,1C L->R: (1, 1, 1) [repeated -> #15]
        - #13 0M,2C R->L: (3, 2, 0) [repeated -> #5]
    - #6 1M,1C R->L: (3, 3, 0) [repeated -> #0]
  - #3 0M,2C L->R: (3, 1, 1) [expanded]
    x 1M,0C R->L: Passengers unavailable on departure bank.
    x 2M,0C R->L: Passengers unavailable on departure bank.
    x 1M,1C R->L: Passengers unavailable on departure bank.
    - #7 0M,1C R->L: (3, 2, 0) [repeated -> #5]
    - #8 0M,2C R->L: (3, 3, 0) [repeated -> #0]
```

Solution path: #0 → #2 → #5 → #11 → #12 → #15 → #17 → #18 → #20 → #23 → #24 → #28

## workforce

3 workers; 6-day repeating cycle; shifts D=Day, N=Night, O=Off. Worker w follows base[(day-2*w) mod 6]. Exactly one D/N/O per day, two of each shift per worker, at most two consecutive working days, no N->D, including cycle boundary. State is a base-pattern prefix; order D,N,O.

Truncated: **False**. Depth limit: 6. Expanded nodes: 58. Peak frontier: 19.

```text
* #0 Start: () [expanded]
  * #1 Base day 1 = D: ('D',) [expanded]
    * #4 Base day 2 = D: ('D', 'D') [expanded]
      x Base day 3 = D: A worker would exceed two days of a shift.
      x Base day 3 = N: More than two consecutive working days.
      * #12 Base day 3 = O: ('D', 'D', 'O') [expanded]
        x Base day 4 = D: A worker would exceed two days of a shift.
        * #24 Base day 4 = N: ('D', 'D', 'O', 'N') [expanded]
          x Base day 5 = D: A worker would exceed two days of a shift.
          x Base day 5 = O: Daily coverage requires one Day, one Night and one Off.
          * #43 Base day 5 = N: ('D', 'D', 'O', 'N', 'N') [expanded]
            x Base day 6 = D: A worker would exceed two days of a shift.
            x Base day 6 = N: A worker would exceed two days of a shift.
            * #58 Base day 6 = O: ('D', 'D', 'O', 'N', 'N', 'O') [goal]
        - #25 Base day 4 = O: ('D', 'D', 'O', 'O') [expanded]
          x Base day 5 = D: A worker would exceed two days of a shift.
          x Base day 5 = O: A worker would exceed two days of a shift.
          - #44 Base day 5 = N: ('D', 'D', 'O', 'O', 'N') [expanded]
            x Base day 6 = D: A worker would exceed two days of a shift.
            x Base day 6 = N: Consecutive-work violation across cycle boundary.
            x Base day 6 = O: A worker would exceed two days of a shift.
    - #5 Base day 2 = N: ('D', 'N') [expanded]
      x Base day 3 = D: Night cannot be followed by Day.
      x Base day 3 = N: More than two consecutive working days.
      - #13 Base day 3 = O: ('D', 'N', 'O') [expanded]
        x Base day 4 = N: Daily coverage requires one Day, one Night and one Off.
        - #26 Base day 4 = D: ('D', 'N', 'O', 'D') [expanded]
          x Base day 5 = D: A worker would exceed two days of a shift.
          x Base day 5 = O: Daily coverage requires one Day, one Night and one Off.
          - #45 Base day 5 = N: ('D', 'N', 'O', 'D', 'N') [expanded]
            x Base day 6 = D: A worker would exceed two days of a shift.
            x Base day 6 = N: A worker would exceed two days of a shift.
            - #59 Base day 6 = O: ('D', 'N', 'O', 'D', 'N', 'O') [goal]
        - #27 Base day 4 = O: ('D', 'N', 'O', 'O') [expanded]
          x Base day 5 = D: Daily coverage requires one Day, one Night and one Off.
          x Base day 5 = O: A worker would exceed two days of a shift.
          - #46 Base day 5 = N: ('D', 'N', 'O', 'O', 'N') [expanded]
            x Base day 6 = D: Night cannot be followed by Day.
            x Base day 6 = N: A worker would exceed two days of a shift.
            x Base day 6 = O: A worker would exceed two days of a shift.
    - #6 Base day 2 = O: ('D', 'O') [expanded]
      x Base day 3 = D: Daily coverage requires one Day, one Night and one Off.
      - #14 Base day 3 = N: ('D', 'O', 'N') [expanded]
        x Base day 4 = D: Night cannot be followed by Day.
        x Base day 4 = O: Daily coverage requires one Day, one Night and one Off.
        - #28 Base day 4 = N: ('D', 'O', 'N', 'N') [expanded]
          x Base day 5 = D: Night cannot be followed by Day.
          x Base day 5 = N: A worker would exceed two days of a shift.
          - #47 Base day 5 = O: ('D', 'O', 'N', 'N', 'O') [expanded]
            x Base day 6 = N: A worker would exceed two days of a shift.
            x Base day 6 = O: A worker would exceed two days of a shift.
            - #60 Base day 6 = D: ('D', 'O', 'N', 'N', 'O', 'D') [goal]
      - #15 Base day 3 = O: ('D', 'O', 'O') [expanded]
        x Base day 4 = O: A worker would exceed two days of a shift.
        - #29 Base day 4 = D: ('D', 'O', 'O', 'D') [expanded]
          x Base day 5 = D: A worker would exceed two days of a shift.
          x Base day 5 = O: A worker would exceed two days of a shift.
          - #48 Base day 5 = N: ('D', 'O', 'O', 'D', 'N') [expanded]
            x Base day 6 = D: A worker would exceed two days of a shift.
            x Base day 6 = N: More than two consecutive working days.
            x Base day 6 = O: A worker would exceed two days of a shift.
        - #30 Base day 4 = N: ('D', 'O', 'O', 'N') [expanded]
          x Base day 5 = D: Night cannot be followed by Day.
          x Base day 5 = O: A worker would exceed two days of a shift.
          - #49 Base day 5 = N: ('D', 'O', 'O', 'N', 'N') [expanded]
            x Base day 6 = D: Night cannot be followed by Day.
            x Base day 6 = N: A worker would exceed two days of a shift.
            x Base day 6 = O: A worker would exceed two days of a shift.
  - #2 Base day 1 = N: ('N',) [expanded]
    x Base day 2 = D: Night cannot be followed by Day.
    - #7 Base day 2 = N: ('N', 'N') [expanded]
      x Base day 3 = D: Night cannot be followed by Day.
      x Base day 3 = N: A worker would exceed two days of a shift.
      - #16 Base day 3 = O: ('N', 'N', 'O') [expanded]
        x Base day 4 = N: A worker would exceed two days of a shift.
        - #31 Base day 4 = D: ('N', 'N', 'O', 'D') [expanded]
          x Base day 5 = N: A worker would exceed two days of a shift.
          x Base day 5 = O: Daily coverage requires one Day, one Night and one Off.
          - #50 Base day 5 = D: ('N', 'N', 'O', 'D', 'D') [expanded]
            x Base day 6 = D: A worker would exceed two days of a shift.
            x Base day 6 = N: A worker would exceed two days of a shift.
            - #61 Base day 6 = O: ('N', 'N', 'O', 'D', 'D', 'O') [goal]
        - #32 Base day 4 = O: ('N', 'N', 'O', 'O') [expanded]
          x Base day 5 = N: A worker would exceed two days of a shift.
          x Base day 5 = O: A worker would exceed two days of a shift.
          - #51 Base day 5 = D: ('N', 'N', 'O', 'O', 'D') [expanded]
            x Base day 6 = D: Consecutive-work violation across cycle boundary.
            x Base day 6 = N: A worker would exceed two days of a shift.
            x Base day 6 = O: A worker would exceed two days of a shift.
    - #8 Base day 2 = O: ('N', 'O') [expanded]
      x Base day 3 = N: Daily coverage requires one Day, one Night and one Off.
      - #17 Base day 3 = D: ('N', 'O', 'D') [expanded]
        x Base day 4 = O: Daily coverage requires one Day, one Night and one Off.
        - #33 Base day 4 = D: ('N', 'O', 'D', 'D') [expanded]
          x Base day 5 = D: A worker would exceed two days of a shift.
          x Base day 5 = N: More than two consecutive working days.
          - #52 Base day 5 = O: ('N', 'O', 'D', 'D', 'O') [expanded]
            x Base day 6 = D: A worker would exceed two days of a shift.
            x Base day 6 = O: A worker would exceed two days of a shift.
            - #62 Base day 6 = N: ('N', 'O', 'D', 'D', 'O', 'N') [goal]
        - #34 Base day 4 = N: ('N', 'O', 'D', 'N') [expanded]
          x Base day 5 = D: Night cannot be followed by Day.
          x Base day 5 = N: A worker would exceed two days of a shift.
          - #53 Base day 5 = O: ('N', 'O', 'D', 'N', 'O') [expanded]
            x Base day 6 = N: A worker would exceed two days of a shift.
            x Base day 6 = O: A worker would exceed two days of a shift.
            - #63 Base day 6 = D: ('N', 'O', 'D', 'N', 'O', 'D') [goal]
      - #18 Base day 3 = O: ('N', 'O', 'O') [expanded]
        x Base day 4 = O: A worker would exceed two days of a shift.
        - #35 Base day 4 = D: ('N', 'O', 'O', 'D') [expanded]
          x Base day 5 = N: Daily coverage requires one Day, one Night and one Off.
          x Base day 5 = O: A worker would exceed two days of a shift.
          - #54 Base day 5 = D: ('N', 'O', 'O', 'D', 'D') [expanded]
            x Base day 6 = D: A worker would exceed two days of a shift.
            x Base day 6 = N: More than two consecutive working days.
            x Base day 6 = O: A worker would exceed two days of a shift.
        - #36 Base day 4 = N: ('N', 'O', 'O', 'N') [expanded]
          x Base day 5 = D: Night cannot be followed by Day.
          x Base day 5 = N: A worker would exceed two days of a shift.
          x Base day 5 = O: A worker would exceed two days of a shift.
  - #3 Base day 1 = O: ('O',) [expanded]
    - #9 Base day 2 = D: ('O', 'D') [expanded]
      x Base day 3 = O: Daily coverage requires one Day, one Night and one Off.
      - #19 Base day 3 = D: ('O', 'D', 'D') [expanded]
        x Base day 4 = D: A worker would exceed two days of a shift.
        x Base day 4 = N: More than two consecutive working days.
        - #37 Base day 4 = O: ('O', 'D', 'D', 'O') [expanded]
          x Base day 5 = D: A worker would exceed two days of a shift.
          x Base day 5 = O: A worker would exceed two days of a shift.
          - #55 Base day 5 = N: ('O', 'D', 'D', 'O', 'N') [expanded]
            x Base day 6 = D: A worker would exceed two days of a shift.
            x Base day 6 = O: A worker would exceed two days of a shift.
            - #64 Base day 6 = N: ('O', 'D', 'D', 'O', 'N', 'N') [goal]
      - #20 Base day 3 = N: ('O', 'D', 'N') [expanded]
        x Base day 4 = D: Night cannot be followed by Day.
        x Base day 4 = N: More than two consecutive working days.
        - #38 Base day 4 = O: ('O', 'D', 'N', 'O') [expanded]
          x Base day 5 = N: Daily coverage requires one Day, one Night and one Off.
          x Base day 5 = O: A worker would exceed two days of a shift.
          - #56 Base day 5 = D: ('O', 'D', 'N', 'O', 'D') [expanded]
            x Base day 6 = D: A worker would exceed two days of a shift.
            x Base day 6 = O: A worker would exceed two days of a shift.
            - #65 Base day 6 = N: ('O', 'D', 'N', 'O', 'D', 'N') [goal]
    - #10 Base day 2 = N: ('O', 'N') [expanded]
      x Base day 3 = D: Night cannot be followed by Day.
      x Base day 3 = O: Daily coverage requires one Day, one Night and one Off.
      - #21 Base day 3 = N: ('O', 'N', 'N') [expanded]
        x Base day 4 = D: Night cannot be followed by Day.
        x Base day 4 = N: A worker would exceed two days of a shift.
        - #39 Base day 4 = O: ('O', 'N', 'N', 'O') [expanded]
          x Base day 5 = N: A worker would exceed two days of a shift.
          x Base day 5 = O: A worker would exceed two days of a shift.
          - #57 Base day 5 = D: ('O', 'N', 'N', 'O', 'D') [expanded]
            x Base day 6 = N: A worker would exceed two days of a shift.
            x Base day 6 = O: A worker would exceed two days of a shift.
            - #66 Base day 6 = D: ('O', 'N', 'N', 'O', 'D', 'D') [goal]
    - #11 Base day 2 = O: ('O', 'O') [expanded]
      x Base day 3 = O: A worker would exceed two days of a shift.
      - #22 Base day 3 = D: ('O', 'O', 'D') [expanded]
        x Base day 4 = O: A worker would exceed two days of a shift.
        - #40 Base day 4 = D: ('O', 'O', 'D', 'D') [expanded]
          x Base day 5 = D: A worker would exceed two days of a shift.
          x Base day 5 = N: More than two consecutive working days.
          x Base day 5 = O: A worker would exceed two days of a shift.
        - #41 Base day 4 = N: ('O', 'O', 'D', 'N') [expanded]
          x Base day 5 = D: Night cannot be followed by Day.
          x Base day 5 = N: More than two consecutive working days.
          x Base day 5 = O: A worker would exceed two days of a shift.
      - #23 Base day 3 = N: ('O', 'O', 'N') [expanded]
        x Base day 4 = D: Night cannot be followed by Day.
        x Base day 4 = O: A worker would exceed two days of a shift.
        - #42 Base day 4 = N: ('O', 'O', 'N', 'N') [expanded]
          x Base day 5 = D: Night cannot be followed by Day.
          x Base day 5 = N: A worker would exceed two days of a shift.
          x Base day 5 = O: A worker would exceed two days of a shift.
```

Solution path: #0 → #1 → #4 → #12 → #24 → #43 → #58

| Worker | Day 1 | Day 2 | Day 3 | Day 4 | Day 5 | Day 6 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | D | D | O | N | N | O |
| 2 | N | O | D | D | O | N |
| 3 | O | N | N | O | D | D |

