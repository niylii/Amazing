from __future__ import annotations
import random
from dataclasses import dataclass, field

#what gets exported when "import"
__all__ = ["Cell", "Maze", "MazeGenerator"]


@dataclass
class Cell:
    """a single cell (4 walls), if a wall is open -> false"""
    N: bool = True
    E: bool = True
    S: bool = True
    W: bool = True


@dataclass
class Maze:

    width: int
    height: int
    entry: tuple[int, int]
    exit_p: tuple[int,int]
    grid: list[list[Cell]] = field(default_factory=list)

    def get_cell(self, x: int, y: int) -> Cell:
        """return the cell at position x,y/ y (rows/) x (columns)"""
        return self.grid[y][x]
    


class MazeGenerator:

    def __init__(
        self,
        width: int,
        height: int,
        seed: int,
        entry: tuple[int, int] = (0,0),
        exit_p: tuple[int, int] | None = None,
        perfect: bool = True
    ) -> None:
        
        self.width = width
        self.height = height
        self.seed = seed
        self.perfect = perfect
        self.pattern_42: set[tuple[int, int]] = set()

        random.seed(seed)

        # default exit to the bottom-right corner of the maze.
        if exit_p is None:
            exit_p = (width - 1, height - 1)

        self.entry = self.validate_point(entry, "entry")
        self.exit_p = self.validate_point(exit_p, "exit")

        if self.entry == self.exit_p:
            raise ValueError("entry and exit must be different points")
        
        self.maze = Maze(
            width=width,
            height=height,
            entry=self.entry,
            exit_p=self.exit_p,
            grid=[[Cell() for _ in range(width)] for _ in range(height)]
            )
        # track which cells have been visited by the algorithm
        self.visited: list[list[bool]] = [
            [False for _ in range(width)] for _ in range(height)
        ]
    
    def validate_point(
            self, point: tuple[int, int], name: str
    ) -> tuple[int, int]:
        
        x, y = point
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError(
                f"{name} ({x}, {y}) is out of bounds "
                f"for grid {self.width}x{self.height}"
            )
        return point
    
    def remove_wall(self, curr_x: int, curr_y: int, neigh_x: int, neigh_y: int) -> None:
        dx, dy = neigh_x - curr_x, neigh_y - curr_y
        current = self.maze.get_cell(curr_x, curr_y)
        neighbor = self.maze.get_cell(neigh_x, neigh_y)

        if dx == 1: # moving east
            current.E = False
            neighbor.W = False
        elif dx == -1: # moving west
            current.W = False
            neighbor.E = False
        elif dy == 1: # .. south
            current.S = False
            neighbor.N = False
        elif dy == -1: #...North
            current.N = False
            neighbor.S = False
        else:
            raise ValueError(
            f"cells ({curr_x},{curr_y}) and ({neigh_x},{neigh_y}) "
            f"are not adjacent"
        )

    def restore_wall(
            self,
            curr_x: int,
            curr_y: int,
            neigh_x: int,
            neigh_y: int
    ) -> None:
        
        dx, dy = neigh_x - curr_x, neigh_y - curr_y
        current = self.maze.get_cell(curr_x, curr_y)
        neighbor = self.maze.get_cell(neigh_x, neigh_y)

        if dx == 1:
            current.E = True
            neighbor.W = True
        elif dx == -1:
            current.W = True
            neighbor.E = True
        elif dy == 1:
            current.S = True
            neighbor.N = True
        elif dy == -1:
            current.N = True
            neighbor.S = True
        else:
            raise ValueError(
            f"cells ({curr_x},{curr_y}) and ({neigh_x},{neigh_y}) "
            f"are not adjacent"
        )
    def _is_3x3_open(self, ax: int, ay: int) -> bool:
        for y in range(ay, ay + 3):
            for x in range(ax, ax + 2):
                if self.maze.get_cell(x, y).E:
                    return False
        for x in range (ax, ax + 3):
            for y in range(ay, ay + 2):
                if self.maze.get_cell(x, y).S:
                    return False
        return True
    
    def _can_create_3x3(
            self, cx: int, cy: int, nx: int, ny: int
    ) -> bool:
        self.remove_wall(cx, cy, nx, ny)
        result = False
        check_xs = set(range(max(0, cx - 2), min(self.width - 2, cx + 1)))
        check_xs.update(range(max(0, nx - 2), min(self.width - 2, nx + 1)))
        check_ys = set(range(max(0, cy - 2), min(self.height - 2, cy + 1)))
        check_ys.update(range(max(0, ny - 2), min(self.height - 2, ny + 1)))

        for ax in check_xs:
            for ay in check_ys:
                if self._is_3x3_open(ax, ay):
                    result = True
                    break
            if result:
                break

        self.restore_wall(cx, cy, nx, ny)
        return result
    
    
    def display_42(self) -> None:
        if self.width < 11 or self.height < 7:
            print("Grid too small, can't display '42' pattern.")
            return
        
        mid_x, mid_y = self.width // 2, self.height // 2

        coords_4 = [
            (mid_x - 3, mid_y - 2),
            (mid_x - 3, mid_y - 1),
            (mid_x - 3, mid_y),
            (mid_x - 2, mid_y),
            (mid_x - 1, mid_y),
            (mid_x - 1, mid_y + 1),
            (mid_x - 1, mid_y + 2),
        ]
        coords_2 = [
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
            if 0 <= x < self.width and 0 <= y < self.height:
                self.visited[y][x] = True
                self.pattern_42.add((x, y))

    def generate_perfect_maze(self) -> None:
        self.display_42()
        if self.entry in self.pattern_42:
            raise ValueError(
                f"Entry {self.entry} overlaps with the '42' pattern."
            )
        if self.exit_p in self.pattern_42:
            raise ValueError(
                f"Exit {self.exit_p} overlaps with the '42' pattern."
            )
        
        start_x, start_y = self.entry
        stack: list[tuple[int, int]] = [(start_x, start_y)]
        self.visited[start_y][start_x] = True

        directions = [
            (0, -1), #north
            (1, 0), #east
            (0, 1), #south
            (-1, 0), #west
        ]

        while stack:
            cx, cy = stack[-1]
            neighboors: list[tuple[int, int]] = []

            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                if (0 <= nx < self.width
                        and 0 <= ny < self.height
                        and not self.visited[ny][nx]):
                    neighboors.append((nx, ny))
            
            if neighboors:
                nx, ny = random.choice(neighboors)
                self.remove_wall(cx, cy, nx, ny)
                self.visited[ny][nx] = True
                stack.append((nx, ny))
            else:
                stack.pop()
    
    def generate_imperfect_maze(self) -> None:
        self.generate_perfect_maze()
        directions = [
            (1, 0), #east
            (0, 1) #south
        ]

        breakable_walls: list[tuple[int, int, int, int]] = []
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern_42:
                    continue
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if not (0 <= nx < self.width and 0 <= ny < self.height):
                        continue
                    if (nx, ny) in self.pattern_42:
                        continue
                    cell = self.maze.get_cell(x, y)
                    if (dx == 1 and cell.E) or (dy == 1 and cell.S):
                        breakable_walls.append((x, y, nx, ny))

        walls_to_open = max(1, len(breakable_walls) // 10)
        random.shuffle(breakable_walls)

        opened = 0
        for x, y, nx, ny in breakable_walls:
            if opened >= walls_to_open:
                break
            if not self._can_create_3x3(x, y, nx, ny):
                self.remove_wall(x, y, nx, ny)
                opened += 1

    def generate(self) -> None:
        if self.perfect:
            self.generate_perfect_maze()
        else:
            self.generate_imperfect_maze()

    def cell_to_bitmask(self, cell: Cell) -> int:
       
        val = 0
        if cell.N:
            val |= 1
        if cell.E:
            val |= 2
        if cell.S:
            val |= 4
        if cell.W:
            val |= 8
        return val

    def to_hex_grid(self) -> list[list[str]]:
        
        return [
            [
                format(self.cell_to_bitmask(self.maze.get_cell(x, y)), 'X')
                for x in range(self.width)
            ]
            for y in range(self.height)
        ]

    def afficher_ascii(self, show_path: list[tuple[int, int]] | None = None) -> None:

        path_set: set[tuple[int, int]] = set(show_path) if show_path else set()

        for y in range(self.height):
            # top wall of each row
            top = ""
            for x in range(self.width):
                cell = self.maze.get_cell(x, y)
                top += "+---" if cell.N else "+   "
            print(top + "+")

            # west wall + cell content
            middle = ""
            for x in range(self.width):
                cell = self.maze.get_cell(x, y)
                west = "|" if cell.W else " "

                if (x, y) == self.entry:
                    content = " E "   # Entry
                elif (x, y) == self.exit_p:
                    content = " X "   # Exit
                elif (x, y) in self.pattern_42:
                    content = "###"   # 42 pattern
                elif (x, y) in path_set:
                    content = " . "   # solution path
                else:
                    content = "   "
                middle += west + content
            print(middle + "|")

        # bottom border
        print("+---" * self.width + "+")


if __name__ == "__main__":
    from solver import solve

    mg = MazeGenerator(
        width=20,
        height=15,
        seed=42,
        entry=(0, 0),
        exit_p=(19, 14),
        perfect=True
    )
    mg.generate()
    result = solve(mg.maze, mg.entry, mg.exit_p)
    mg.afficher_ascii()
    mg.afficher_ascii(show_path=result.path)