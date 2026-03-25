
from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from generator import Maze


@dataclass
class SolverResult:

    path: list[tuple[int, int]]
    directions: str

class SolverError(RuntimeError):
    """Raised when the maze has no path from entry to exit."""


_DELTA_TO_DIRECTION: dict[tuple[int, int], str] = {
    (0, -1): "N",
    (1, 0): "E",
    (0, 1): "S",
    (-1, 0): "W",
}

_DIRECTIONS: list[tuple[int, int]] = list(_DELTA_TO_DIRECTION.keys())


def _is_passable(maze: Maze, cx: int, cy: int, nx: int, ny: int) -> bool:
 
    dx, dy = nx - cx, ny - cy
    cell = maze.get_cell(cx, cy)

    if dx == 1:
        return not cell.E
    if dx == -1:
        return not cell.W
    if dy == 1:
        return not cell.S
    if dy == -1:
        return not cell.N

    return False



def solve(
    maze: Maze,
    entry: tuple[int, int],
    exit_p: tuple[int, int],
) -> SolverResult:
    
    queue: deque[tuple[int, int]] = deque([entry])
    came_from: dict[tuple[int, int], tuple[int, int] | None] = {entry: None}

    while queue:
        cx, cy = queue.popleft()

        if (cx, cy) == exit_p:
            break

        for dx, dy in _DIRECTIONS:
            nx, ny = cx + dx, cy + dy

            if not (0 <= nx < maze.width and 0 <= ny < maze.height):
                continue

            if (nx, ny) in came_from:
                continue

            if not _is_passable(maze, cx, cy, nx, ny):
                continue

            came_from[(nx, ny)] = (cx, cy)
            queue.append((nx, ny))
    else:
        raise SolverError(
            f"No path found from {entry} to {exit_p}. "
            "The maze may be disconnected."
        )

    path: list[tuple[int, int]] = []
    current: tuple[int, int] | None = exit_p
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()

    direction_chars: list[str] = []
    for i in range(len(path) - 1):
        px, py = path[i]
        qx, qy = path[i + 1]
        delta = (qx - px, qy - py)
        direction_chars.append(_DELTA_TO_DIRECTION[delta])

    return SolverResult(path=path, directions="".join(direction_chars))