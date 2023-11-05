Position = tuple[int, int]


def flat_pos(pos: Position):
    """
    Returns the 1D flat position of row and column
    :param pos: position
    :return: flat position
    """
    return pos[0] * 15 + pos[1]


def out_of_bounds(pos: Position) -> bool:
    """
    Returns True if position is out of bounds
    :param pos: position
    :return: out of bounds
    """
    if pos[0] < 0 or pos[0] > 14 or pos[1] < 0 or pos[1] > 14:
        return True
    return False


def transpose(pos: Position) -> Position:
    """
    Returns the position transposed.
    :param pos: position
    :return: transposed position
    """
    return pos[::-1]
