from typing import Tuple




def vec(a: Tuple[int, int], b: Tuple[int, int]) -> Tuple[int, int]:
    """
    Get direction vector from point a to point b.

    @param a: point a (x1, y1)
    @param b: point b (x2, y2)
    @return: direction vector (dx, dy)
    """
    return b[0] - a[0], b[1] - a[1]


def is_straight(d1, d2) -> bool:
    """
    Check if two direction vectors represent a straight line (no turn).
    This is true if both directions are vertical or both are horizontal.

    @param d1: first direction vector (dx1, dy1)
    @param d2: second direction vector (dx2, dy2)
    @return: True if straight line, False if turn
    """
    return (d1[0] == 0 and d2[0] == 0) or (d1[1] == 0 and d2[1] == 0)
