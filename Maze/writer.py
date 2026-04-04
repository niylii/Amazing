from __future__ import annotations

from Maze.generator import MazeGenerator


class MazeWriter:
    def __init__(self, maze: MazeGenerator, output_path: str) -> None:

        self.maze: MazeGenerator = maze
        self.output_path: str = output_path

    def write(self) -> None:

        directions: str = self.maze.solve()

        with open(self.output_path, "w", encoding="utf-8") as f:
            for row in self.maze.grid.cells:
                f.write("".join(cell.to_hex() for cell in row) + "\n")

            f.write("\n")

            entry_x, entry_y = self.maze.entry_point
            exit_x, exit_y = self.maze.exit_point
            f.write(f"{entry_x},{entry_y}\n")
            f.write(f"{exit_x},{exit_y}\n")

            f.write(directions + "\n")
