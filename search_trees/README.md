# Search trees

Run from the project directory:

```sh
python3 main.py trees
python3 main.py trees --problem missionaries
```

- `problems.py`: explicit instances, state transitions and rejection rules.
- `generate.py`: FIFO construction, repeated-state leaves, budgets and rendering.
- `../validate_trees.py`: independent solution-path and roster checks.
- `../results/search-trees.md`: indented trees with rejection reasons and marked paths.
- `../results/search-trees.json`: node IDs, parents, actions, states, depth and statistics.

Default trees: 8-Puzzle to depth 3 (partial), Missionaries and Cannibals to depth
12 (reachable graph exhausted), workforce to depth 6 (complete legal-prefix tree).
Default node limit: 5,000. Use `--max-depth` or `--max-nodes` to change budgets.

See `../report.md` for chosen rules, initial/goal states and measured results.
The workforce example uses three workers following cyclically shifted copies
of a six-day base pattern; these assumptions were chosen because the brief
does not prescribe a concrete staffing instance.
