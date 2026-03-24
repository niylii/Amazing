import curses, random, time
from collections import deque
from typing import List, Tuple

BLACK = 0
RED = 1
GREEN = 2
YELLOW = 3
BLUE = 4
MAGENTA = 5
CYAN = 6
WHITE = 8

class Animator:
    def __init__(self, maze):
        self.maze = maze
        self.maze_animation_step = 0
        self.maze_animation_step_number = 1
        self.last_time_maze_animation = time.time()
        self.path_animation_step = 0
        self.last_time_path_animation = time.time()
        self.maze_timeline = []
        self.maze_animation_types = {
            "line by line" : self.line_by_line_maze_animation,
            "cell by cell" : self.cell_by_cell_maze_animation,
            "random" : self.random_maze_animation,
            "prim" : self.prim_maze_animation,
            "spread" : self.spread_maze_animation,
            "oil effect" : self.oil_effect_maze_animation,
        }
        
        self.selectors_indexes = {
            "animation" : 0,
            "walls color" : 0,
            "path color" : 0, 
            "theme" : 0,
            "perfect " : 0,
        }

    # Maze animations
    def random_maze_animation(self) -> List[Tuple[int,int]]:
        coords = [(x, y) for y in range(self.maze.height) for x in range(self.maze.width)]
        self.maze_animation_step_number = 5
        random.shuffle(coords)
        return coords

    def line_by_line_maze_animation(self) -> List[Tuple[int,int]]:
        coords = [(x, y) for y in range(self.maze.height) for x in range(self.maze.width)]
        self.maze_animation_step_number = self.maze.width
        return coords

    def cell_by_cell_maze_animation(self) -> List[Tuple[int,int]]:
        coords = [(x, y) for y in range(self.maze.height) for x in range(self.maze.width)]
        self.maze_animation_step_number = 1
        return coords

    def prim_maze_animation(self) -> List[Tuple[int,int]]:
        start_node = self.maze.entry_point
        order = []
        visited = {start_node}
        frontier = [start_node] 
        self.maze_animation_step_number = 1

        while frontier:
            current = random.choice(frontier)
            frontier.remove(current)
            order.append(current)
            cx, cy = current
            cell = self.maze.grid.get_cell(cx, cy)
            for direction, (dx, dy) in [("N", (0,-1)),("S",(0,1)),("W",(-1,0)),("E",(1,0))]:
                nx, ny = cx+dx, cy+dy
                if 0 <= nx < self.maze.width and 0 <= ny < self.maze.height:
                    if (nx, ny) not in visited and cell.walls[direction]:
                        visited.add((nx, ny))
                        frontier.append((nx, ny))
        return order

    def oil_effect_maze_animation(self) -> List[Tuple[int,int]]:
        cx, cy = self.maze.width // 2, self.maze.height // 2
        coords = [(x, y, max(abs(x-cx), abs(y-cy))) for y in range(self.maze.height) for x in range(self.maze.width)]
        coords.sort(key=lambda c:c[2])
        self.maze_animation_step_number = 5
        return [(c[0],c[1]) for c in coords]

    def spread_maze_animation(self) -> List[Tuple[int,int]]:
        start_node = (self.maze.width//2, self.maze.height//2)
        order = [start_node]
        queue = deque([start_node])
        visited = {start_node}
        self.maze_animation_step_number = 2

        while queue:
            cx, cy = queue.popleft()
            cell = self.maze.grid.get_cell(cx, cy)
            for direction, (dx, dy) in [("N",(0,-1)),("S",(0,1)),("W",(-1,0)),("E",(1,0))]:
                nx, ny = cx+dx, cy+dy
                if 0 <= nx < self.maze.width and 0 <= ny < self.maze.height:
                    if (nx, ny) not in visited and cell.walls[direction]:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
                        order.append((nx, ny))
        return order
    
    def prepare_maze_timeline(self):
        self.maze_timeline = []

        maze = self.maze
        maze = self.maze

        self.current_animation = self.selectors_data["animation"][self.selectors_indexes["animation"]][0]
        coords = self.maze_animation_types[self.current_animation]() 
        for x, y in coords:
            cell = maze.grid.get_cell(x, y)

            real_x = (x * 2) + 1
            real_y = (y * 2) + 1

            actions = [(real_y, real_x)]

            if cell.walls["N"]: actions.append((real_y - 1, real_x))
            if cell.walls["S"]: actions.append((real_y + 1, real_x))
            if cell.walls["W"]: actions.append((real_y, real_x - 1))
            if cell.walls["E"]: actions.append((real_y, real_x + 1))

            self.maze_timeline.append(actions)