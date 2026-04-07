from __future__ import annotations

import random
from collections import deque
from typing import List, Optional, Set, Tuple

from maze.cell import Cell
from maze.grid import Grid


class MazeGenerator:
    def __init__(
        self,
        width: int,
        height: int,
        seed: Optional[int],
        perfect: bool,
        entry_point: Tuple[int, int],
        exit_point: Tuple[int, int],
    ) -> None:

        self.width: int = width
        self.height: int = height
        self.seed: Optional[int] = seed
        self.perfect: bool = perfect
        self.entry_point: Tuple[int, int] = self._validate_point(
            entry_point, "entry")
        self.exit_point: Tuple[int, int] = self._validate_point(
            exit_point, "exit")

        if self.entry_point == self.exit_point:
            raise ValueError("entry and exit must be different cells.")

        if seed is not None:
            random.seed(seed)

        self.grid: Grid = Grid(width, height)
        self._pattern_42: Set[Tuple[int, int]] = set()
        self.solution_path: List[Tuple[int, int]] = []
        self._solution_cache: Optional[str] = None
        self.pattern_42_warning = ""

    # Validate that point lies within the grid.
    def _validate_point(self, point: Tuple[int, int],
                        name: str) -> Tuple[int, int]:

        x, y = point
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError(
                f"{name} ({x}, {y}) is out of bounds "
                f"for a {self.width}x{self.height} grid."
            )
        return point

    # the 42 display , mark as visited
    def display_42(self) -> None:

        if self.width < 11 or self.height < 7:
            need = "(needs 12x8, "
            got = f"got {self.width}x{self.height})"
            self.pattern_42_warning = (
                f"⚠  Maze too small for '42' pattern "
                f"(need: {need}, got: {got})")
            return  # grid too small to display the pattern
        self.pattern_42_warning = ""

        mid_x, mid_y = self.width // 2, self.height // 2

        coords_4: List[Tuple[int, int]] = [
            (mid_x - 3, mid_y - 2),
            (mid_x - 1, mid_y - 2),
            (mid_x - 3, mid_y - 1),
            (mid_x - 1, mid_y - 1),
            (mid_x - 3, mid_y),
            (mid_x - 2, mid_y),
            (mid_x - 1, mid_y),
            (mid_x - 1, mid_y + 1),
            (mid_x - 1, mid_y + 2),
        ]
        coords_2: List[Tuple[int, int]] = [
            (mid_x + 1, mid_y - 2),
            (mid_x + 2, mid_y - 2),
            (mid_x + 3, mid_y - 2),
            (mid_x + 3, mid_y - 1),
            (mid_x + 1, mid_y),
            (mid_x + 2, mid_y),
            (mid_x + 3, mid_y),
            (mid_x + 1, mid_y + 1),
            (mid_x + 1, mid_y + 2),
            (mid_x + 2, mid_y + 2),
            (mid_x + 3, mid_y + 2),
        ]

        for x, y in coords_4 + coords_2:
            if not self.grid.in_bounds(x, y):
                continue
            self.grid.get_cell(x, y).visited = True
            self._pattern_42.add((x, y))
        if self.entry_point in self._pattern_42:
            raise ValueError(
                f"Entry {self.entry_point} overlaps with the '42' pattern."
            )
        if self.exit_point in self._pattern_42:
            raise ValueError(f"Exit {self.exit_point} "
                             f"overlaps with the '42' pattern.")

    # DFS helpers
    def get_unvisited_neighbors(self, cell: Cell) -> List[Tuple[str, Cell]]:

        return [
            (direction, neighbor)
            for direction, neighbor in self.grid.get_neighbors(cell)
            if not neighbor.visited
        ]

    def _is_3x3_open(self, ax: int, ay: int) -> bool:

        for y in range(ay, ay + 3):
            for x in range(ax, ax + 2):
                if not self.grid.get_cell(x, y).walls["E"]:
                    return False
        for x in range(ax, ax + 3):
            for y in range(ay, ay + 2):
                if not self.grid.get_cell(x, y).walls["S"]:
                    return False
        return True

    def can_create_3x3(self, cell: Cell, neighbor: Cell,
                       direction: str) -> bool:

        self.grid.open_wall(cell, neighbor, direction)

        cx, cy = cell.x, cell.y
        nx, ny = neighbor.x, neighbor.y

        check_xs = set(range(max(0, cx - 2), min(self.width - 2, cx + 1)))
        check_xs.update(range(max(0, nx - 2), min(self.width - 2, nx + 1)))
        check_ys = set(range(max(0, cy - 2), min(self.height - 2, cy + 1)))
        check_ys.update(range(max(0, ny - 2), min(self.height - 2, ny + 1)))

        result = any(
            self._is_3x3_open(ax, ay) for ax in check_xs for ay in check_ys)

        self.grid.close_wall(cell, neighbor, direction)
        return result

    def generate_perfect(self) -> None:

        self.display_42()

        start_cell = self.grid.get_cell(*self.entry_point)
        start_cell.visited = True
        stack: List[Cell] = [start_cell]

        while stack:
            unvisited = self.get_unvisited_neighbors(stack[-1])
            if unvisited:
                direction, neighbor = random.choice(unvisited)
                self.grid.open_wall(stack[-1], neighbor, direction)
                neighbor.visited = True
                stack.append(neighbor)
            else:
                stack.pop()

    def generate_imperfect(self) -> None:

        self.generate_perfect()

        breakable: List[Tuple[Cell, Cell, str]] = []

        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self._pattern_42:
                    continue
                for direction, (dx, dy) in [("E", (1, 0)), ("S", (0, 1))]:
                    nx, ny = x + dx, y + dy
                    if not self.grid.in_bounds(nx, ny):
                        continue
                    if (nx, ny) in self._pattern_42:
                        continue
                    cell = self.grid.get_cell(x, y)
                    if not cell.walls[direction]:
                        breakable.append(
                            (cell, self.grid.get_cell(nx, ny), direction))

        walls_to_open = max(1, len(breakable) // 10)
        random.shuffle(breakable)

        opened = 0
        for cell, neighbor, direction in breakable:
            if opened >= walls_to_open:
                break
            if not self.can_create_3x3(cell, neighbor, direction):
                self.grid.open_wall(cell, neighbor, direction)
                opened += 1

    def generate(self) -> None:
        if self.perfect:
            self.generate_perfect()
        else:
            self.generate_imperfect()

    # BFS solver
    def solve(self) -> str:

        if self._solution_cache is not None:
            return self._solution_cache

        entry_cell = self.grid.get_cell(*self.entry_point)
        exit_cell = self.grid.get_cell(*self.exit_point)

        queue: deque[Tuple[Cell, List[str], List[Cell]]] = deque()
        queue.append((entry_cell, [], [entry_cell]))
        visited: Set[Cell] = {entry_cell}

        while queue:
            current, dirs, cell_path = queue.popleft()

            if current is exit_cell:
                self.solution_path = [(c.x, c.y) for c in cell_path]
                self._solution_cache = "".join(dirs)
                return self._solution_cache

            for direction, neighbor in self.grid.get_neighbors(current):
                if current.walls[direction] and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(
                        (
                            neighbor,
                            dirs + [direction],
                            cell_path + [neighbor],
                        )
                    )

        self.solution_path = []
        self._solution_cache = ""
        return self._solution_cache


# #just for testing and understanding
#     def afficher_ascii(
#             self,
#             show_path: Optional[List[Tuple[int, int]]] = None,
#         ) -> None:
# path_set: Set[Tuple[int, int]] = set(show_path) if
# show_path else set()

#             for y in range(self.height):
#                 top = ""
#                 for x in range(self.width):
#                     cell = self.grid.get_cell(x, y)
#                     top += "+---" if not cell.walls["N"] else "+   "
#                 print(top + "+")

#                 middle = ""
#                 for x in range(self.width):
#                     cell = self.grid.get_cell(x, y)
#                     west = "|" if not cell.walls["W"] else " "

#                     if   (x, y) == self.entry_point:  content = " E "
#                     elif (x, y) == self.exit_point:   content = " X "
#                     elif (x, y) in self._pattern_42:  content = "###"
#                     elif (x, y) in path_set:          content = " . "
#                     else:                             content = "   "

#                     middle += west + content
#                 print(middle + "|")

#             print("+---" * self.width + "+")


# if __name__ == "__main__":

#     width, height = 25, 15
#     seed = 42
#     perfect = True,
#     entry = (0, 0)
#     exit_ = (width - 1, height - 1)

#     mg = MazeGenerator(
#         width=width,
#         height=height,
#         seed=seed,
#         perfect=perfect,
#         entry_point=entry,
#         exit_point=exit_,
#     )
#     mg.generate()

#     mg.solve()
#     mg.afficher_ascii(show_path=mg.solution_path)
