"""Display project status or reproducible initial landscape calculations."""

import argparse
import sys

from latin_square import landscape as latin_landscape
from social_golfers import GolfersProblem
from sudoku import landscape as sudoku_landscape


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "golfers-reference":
        from golfers_reference import main as reference_main
        reference_main(sys.argv[2:])
        return
    if len(sys.argv) > 1 and sys.argv[1] == "latin":
        from latin_square import main as latin_main
        latin_main(sys.argv[2:])
        return
    if len(sys.argv) > 1 and sys.argv[1] == "trees":
        from search_trees.generate import main as trees_main
        trees_main(sys.argv[2:])
        return
    if len(sys.argv) > 1 and sys.argv[1] == "golfers":
        from social_golfers import main as golfers_main
        golfers_main(sys.argv[2:])
        return
    if len(sys.argv) > 1 and sys.argv[1] == "sudoku":
        from sudoku import main as sudoku_main
        sudoku_main(sys.argv[2:])
        return
    parser = argparse.ArgumentParser(description=__doc__)
    parser.epilog = "Commands: golfers, golfers-reference, sudoku, latin, trees; append --help for options."
    parser.add_argument("--landscape", action="store_true",
                        help="calculate initial unconstrained search-space sizes")
    args = parser.parse_args()
    if not args.landscape:
        print("Social Golfers implemented: python3 main.py golfers --help")
        print("Published ten-week witness: python3 main.py golfers-reference")
        print("Sudoku implemented: python3 main.py sudoku --help")
        print("Latin Square implemented: python3 main.py latin --help")
        print("Search trees implemented: python3 main.py trees --help")
        print("See README.md and report.md for requirements and models.")
        return

    golfers = GolfersProblem()
    print(f"Social Golfers ({golfers.players} players, {golfers.weeks} weeks):")
    print(f"  Unordered weekly partitions: {golfers.weekly_partitions()}")
    print(f"  Schedules before pair constraints: {golfers.landscape()}")
    print(f"  Pair-counting upper bound on weeks: {golfers.week_upper_bound()}")
    empty_board = tuple((0,) * 9 for _ in range(9))
    print(f"Sudoku (empty board, 81 blanks): {sudoku_landscape(empty_board)}")
    print(f"Latin Square (n=5): {latin_landscape(5)}")
    print("These are candidate-space sizes, not measured visited-node counts.")


if __name__ == "__main__":
    main()
