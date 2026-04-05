"""
display/animator.py
Pure animation logic — no curses dependency, fully testable.

Responsibilities
----------------
"""

from __future__ import annotations

import random
import time
from collections import deque
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from maze.generator import MazeGenerator


class Animator:
    """Owns all animation state and algorithms."""

    def __init__(self, maze: "MazeGenerator") -> None:
        self.maze = maze

        # maze animation state 
        self.maze_is_animating: bool = False
        self.path_is_animating: bool = False
        self.toggle_animation: bool = True
        self.path_shown: bool = False

        self.maze_animation_step: int = 0
        self.maze_animation_step_number: int = 1
        self._last_time_maze: float = time.time()

        self.maze_timeline: list[list[tuple[int, int]]] = []

        # path animation state 
        self.path_animation_step: int = 0
        self._last_time_path: float = time.time()

        # strategy registry (name → method) 
        self.strategies: dict[str, Callable[[], list[tuple[int, int]]]] = {
            "line by line": self._strategy_line_by_line,
            "cell by cell": self._strategy_cell_by_cell,
            "random":       self._strategy_random,
            "prim":         self._strategy_prim,
            "spread":       self._strategy_spread,
            "oil effect":   self._strategy_oil_effect,
        }

        self.current_strategy: str = "line by line"


    def reset(self, maze: "MazeGenerator", strategy: str, toggle: bool) -> None:
        """Prepare for a brand-new maze (called after generation)."""
        self.maze = maze
        self.current_strategy = strategy
        self.toggle_animation = toggle

        self.maze_animation_step = 0
        self.path_animation_step = 0
        self.maze_is_animating = True
        self.path_shown = False if toggle else self.path_shown

        self.build_maze_timeline()

    def build_maze_timeline(self) -> None:
        """Compute the full ordered list of per-cell draw-actions."""
        maze = self.maze
        strategy_fn = self.strategies.get(self.current_strategy, self._strategy_line_by_line)
        coords = strategy_fn()

        timeline: list[list[tuple[int, int]]] = []
        for x, y in coords:
            cell = maze.grid.get_cell(x, y)
            real_x = (x * 2) + 1
            real_y = (y * 2) + 1

            actions: list[tuple[int, int]] = [(real_y, real_x)]
            if cell.walls["N"]:
                actions.append((real_y - 1, real_x))
            if cell.walls["S"]:
                actions.append((real_y + 1, real_x))
            if cell.walls["W"]:
                actions.append((real_y, real_x - 1))
            if cell.walls["E"]:
                actions.append((real_y, real_x + 1))

            timeline.append(actions)

        self.maze_timeline = timeline

    def step_maze(self) -> None:
        """Advance the maze-reveal animation by one frame."""
        delay: float = 0.06

        if not self.maze_is_animating:
            return

        if not self.toggle_animation:
            # skip straight to the end
            self.maze_animation_step = len(self.maze_timeline)
            self.maze_is_animating = False
            return

        now = time.time()
        if now - self._last_time_maze >= delay:
            if self.maze_animation_step < len(self.maze_timeline):
                self.maze_animation_step += self.maze_animation_step_number
                self._last_time_maze = now
            else:
                self.maze_is_animating = False

    def step_path(self) -> None:
        """Advance the path-reveal animation by one frame."""
        delay: float = 0.03

        if not self.path_is_animating or self.maze_is_animating:
            return

        now = time.time()
        if now - self._last_time_path >= delay:
            if self.path_animation_step < len(self.maze.solve()):
                self.path_animation_step += 1
                self._last_time_path = now
            else:
                self.path_is_animating = False


    ### animation strategies ###
    def _strategy_random(self) -> list[tuple[int, int]]:
        maze = self.maze
        coords = [(x, y) for y in range(maze.height) for x in range(maze.width)]
        self.maze_animation_step_number = 5
        random.shuffle(coords)
        return coords

    def _strategy_line_by_line(self) -> list[tuple[int, int]]:
        maze = self.maze
        coords = [(x, y) for y in range(maze.height) for x in range(maze.width)]
        self.maze_animation_step_number = maze.width
        return coords

    def _strategy_cell_by_cell(self) -> list[tuple[int, int]]:
        maze = self.maze
        coords = [(x, y) for y in range(maze.height) for x in range(maze.width)]
        self.maze_animation_step_number = 1
        return coords

    def _strategy_prim(self) -> list[tuple[int, int]]:
        maze = self.maze
        self.maze_animation_step_number = 1

        start = maze.entry_point
        order: list[tuple[int, int]] = []
        visited: set[tuple[int, int]] = {start}
        frontier: list[tuple[int, int]] = [start]

        while frontier:
            current = random.choice(frontier)
            frontier.remove(current)
            order.append(current)
            cx, cy = current
            cell = maze.grid.get_cell(cx, cy)

            for direction, (dx, dy) in [("N", (0, -1)), ("S", (0, 1)), ("W", (-1, 0)), ("E", (1, 0))]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < maze.width and 0 <= ny < maze.height:
                    if (nx, ny) not in visited and cell.walls[direction]:
                        visited.add((nx, ny))
                        frontier.append((nx, ny))

        return order

    def _strategy_oil_effect(self) -> list[tuple[int, int]]:
        maze = self.maze
        self.maze_animation_step_number = 5
        cx, cy = maze.width // 2, maze.height // 2

        coords_with_dist = [
            (x, y, max(abs(x - cx), abs(y - cy)))
            for y in range(maze.height)
            for x in range(maze.width)
        ]
        coords_with_dist.sort(key=lambda c: c[2])
        return [(c[0], c[1]) for c in coords_with_dist]

    def _strategy_spread(self) -> list[tuple[int, int]]:
        maze = self.maze
        self.maze_animation_step_number = 2
        start = (maze.width // 2, maze.height // 2)

        order: list[tuple[int, int]] = [start]
        queue: deque[tuple[int, int]] = deque([start])
        visited: set[tuple[int, int]] = {start}

        while queue:
            cx, cy = queue.popleft()
            cell = maze.grid.get_cell(cx, cy)

            for direction, (dx, dy) in [("N", (0, -1)), ("S", (0, 1)), ("W", (-1, 0)), ("E", (1, 0))]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < maze.width and 0 <= ny < maze.height:
                    if (nx, ny) not in visited and cell.walls[direction]:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
                        order.append((nx, ny))

        return order
