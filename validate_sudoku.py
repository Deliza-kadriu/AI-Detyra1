"""Independent complete-Sudoku validator; does not import the BFS solver."""


def validate_solution(clues, solution) -> dict:
    def well_formed(board, minimum):
        return (isinstance(board, (list, tuple)) and len(board) == 9
                and all(isinstance(row, (list, tuple)) and len(row) == 9
                        and all(type(v) is int and minimum <= v <= 9 for v in row)
                        for row in board))

    if not well_formed(clues, 0) or not well_formed(solution, 1):
        return {"valid": False, "objective": None,
                "errors": ["Expected 9x9 clues (0..9) and complete solution (1..9)."]}
    errors = []
    if any(clues[r][c] and clues[r][c] != solution[r][c]
           for r in range(9) for c in range(9)):
        errors.append("A fixed clue was changed.")
    units = [(f"Row {r + 1}", list(solution[r])) for r in range(9)]
    units.extend((f"Column {c + 1}", [solution[r][c] for r in range(9)]) for c in range(9))
    units.extend((f"Box {br // 3 + 1},{bc // 3 + 1}",
                  [solution[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3)])
                 for br in (0, 3, 6) for bc in (0, 3, 6))
    objective = 0
    for name, unit in units:
        objective += sum(max(0, unit.count(digit) - 1) for digit in range(1, 10))
        if set(unit) != set(range(1, 10)):
            errors.append(f"{name} does not contain 1..9 exactly once.")
    return {"valid": not errors, "objective": objective, "errors": errors}
