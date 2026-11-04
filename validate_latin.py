"""Independent validation of a complete Latin Square."""


def validate_square(square, size):
    if (not isinstance(square, (list, tuple)) or len(square) != size
            or any(not isinstance(row, (list, tuple)) or len(row) != size
                   or any(type(v) is not int or not 1 <= v <= size for v in row)
                   for row in square)):
        return {'valid': False, 'objective': None, 'errors': ['Invalid square shape or entries.']}
    units = list(square) + [[square[r][c] for r in range(size)] for c in range(size)]
    objective = sum(size - len(set(unit)) for unit in units)
    return {'valid': objective == 0, 'objective': objective,
            'errors': [] if objective == 0 else ['Repeated values in rows or columns.']}
