from typing import Dict, List, Tuple

from Maze.cell import Cell


OPPOSITE: Dict[str, str] = {
    "N": "S",
    "E": "W",
    "S": "N",
    "W": "E",
}


class Grid:
    def __init__(self, width: int, height: int) -> None:

        self.width: int = width
        self.height: int = height
        self.cells: List[List[Cell]] = [
            [Cell(x, y) for x in range(width)] for y in range(height)
        ]

    def get_cell(self, x: int, y: int) -> Cell:
        return self.cells[y][x]

    def in_bounds(self, x: int, y: int) -> bool:

        return 0 <= x < self.width and 0 <= y < self.height

    def get_neighbors(self, cell: Cell) -> List[Tuple[str, Cell]]:

        candidates: Dict[str, Tuple[int, int]] = {
            "N": (cell.x, cell.y - 1),
            "E": (cell.x + 1, cell.y),
            "S": (cell.x, cell.y + 1),
            "W": (cell.x - 1, cell.y),
        }
        return [
            (direction, self.cells[y][x])
            for direction, (x, y) in candidates.items()
            if self.in_bounds(x, y)
        ]

    def open_wall(self, cell: Cell, neighbor: Cell, direction: str) -> None:

        cell.walls[direction] = True
        neighbor.walls[OPPOSITE[direction]] = True

    def close_wall(self, cell: Cell, neighbor: Cell, direction: str) -> None:

        cell.walls[direction] = False
        neighbor.walls[OPPOSITE[direction]] = False
