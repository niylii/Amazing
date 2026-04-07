*This project has been created as part of the 42 curriculum by nouhiyli, fadel-bo.*


# A-Maze-ing

## Description

**A-Maze-ing** is a terminal-based maze generator and solver built with Python.
The program generates a maze from a configuration file, writes it to an output file in a hex encoded format,
then launches an interactive curses UI where the maze is animated, navigable, and solvable.

**Goal:** Implement a complete maze generation from config parsing to visual display
with clean separation between generation logic, rendering, animation, and menu control.

**Overview of features:**
- Maze generation using iterative **Depth-First Search (recursive backtracker)**
- Optional **imperfect maze** mode that breaks extra walls to create loops
- A hidden **"42" pattern** stamped into every maze
- BFS-based **automatic solver** that finds and displays the shortest path
- Animated maze reveal with **6 different animation strategies**
- Interactive **curses UI** with menus, config editing, color themes, and help panel
- Maze output written to a `.txt` file in hex format

---

## Instructions

### Requirements

- Python 3.10+
- A terminal with curses support (Linux / macOS)

### Installation

```bash
git clone <your-repo-url>
cd a-maze-ing
make install
```

### Running

```bash
make run
# or directly:
python3 a_maze_ing.py config.txt
```

### Other Makefile targets

 `make run`: Run with default config 
 `make install`: Install dependencies via pip 
 `make debug` : Run under `pdb` debugger 
 `make lint` : Run `flake8` + `mypy` (standard) 
 `make lint-strict` : Run `mypy --strict` 
 `make clean`: Remove `__pycache__` and `.pyc` files 


## Config File
The config file is a plain `.txt` file passed as a command-line argument.
Each line follows the format `KEY=VALUE`. 
(Lines starting with `#` and blank lines are ignored.)

### Required keys
`x` is the column, `y` is the row
`WIDTH` : integer, 0–50 | Number of columns in the maze
`HEIGHT` : integer, 0–50 | Number of rows in the maze
`ENTRY` : `x,y` coordinate | Entry point (must be within bounds)
`EXIT` : `x,y` coordinate | Exit point (must differ from entry)
`OUTPUT_FILE` : string | Path for the hex-encoded output file

### Optional keys
`SEED` : integer or `random` | seed for reproducible mazes 
`PERFECT` : boolean (`true`/`false`) | if `false` extra walls are broken to create loops.

### Example `config.txt`
```
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=1,0
OUTPUT_FILE=test.txt
PERFECT=True
```

---
## Maze Generation Algorithm

### Algorithm: Iterative Depth-First Search (Recursive Backtracker)

The maze is generated using an **iterative DFS** with an explicit stack (no actual recursion to avoid stack overflow on large grids).

**How it works:**
1. Mark the entry cell as visited and push it onto the stack.
2. While the stack is not empty:
   - Look at the top cell. If it has unvisited neighbors, pick one at random, carve a passage between them, mark it visited, and push it.
   - If no unvisited neighbors remain, pop the cell (backtrack).
3. Repeat until all cells are visited.

**Imperfect mode** (`PERFECT=False`) runs DFS first, then randomly breaks ~10% of remaining walls — filtered to avoid creating any open 3×3 square region, which would look like a hole rather than a loop.

### Why DFS?

- **Simplicity:** The algorithm is easy to reason about, implement correctly, and test.
- **Quality:** DFS produces mazes with long, winding corridors and relatively few dead ends — aesthetically interesting and non-trivial to solve by hand.
- **Guaranteed perfect maze:** Every cell is reachable, and there is exactly one path between any two cells (before imperfect mode).
- **Controllable with a seed:** Deterministic output makes debugging and testing straightforward.

### Solver: BFS

The solver uses **Breadth-First Search** from entry to exit, guaranteeing the shortest path. The result is cached after the first call (`_solution_cache`) so repeated calls (e.g., during animation) are free.

---

## Output File Format

Each row of the maze is written as a string of hex characters (one per cell),
followed by a blank line, then entry coordinates,
exit coordinates, and the solution direction string.

```
F9F3...   :one hex char per cell, one line per row
          :blank line
0,0       :entry x,y
19,14     :exit x,y
NNEESS... :solution as cardinal directions (N/S/E/W)
```

Each hex character encodes the **open walls** of a cell as a 4-bit value:

| Bit | Direction |
|---|---|
| 0 (LSB) | North |
| 1 | East |
| 2 | South |
| 3 | West |

A `0` bit means the wall is **open** (passage exists). A `1` bit means the wall is **closed**.

---
# For Bonus:
## UI & Advanced Features
### Animation strategies

The maze reveal can be animated in 6 modes, selectable from the "custom option" menu:

Strategy | Description |
--|---|
`line by line` | Reveals one full row at a time |
`cell by cell` | Reveals one cell at a time, left-to-right top-to-bottom |
`random` | Cells appear in random order |
`prim` | Spreads outward from entry using Prim-like frontier expansion |
`spread` | BFS flood-fill from the maze center |
`oil effect` | Chebyshev-distance rings expanding from the center |

### Keyboard controls

| Key | Action |
|---|---|
| `up/down ` | Navigate menu |
| `<-/->` | Cycle selector values |
| `Enter` | Confirm / activate button |
| `Space` | Toggle animation on/off |
| `?` | Toggle help panel |
| `Ctrl+C` | Quit |

### Menu sections

- **Main menu:** Generate, show path, maze config, custom options, exit
- **Maze config:** Edit width, height, entry, exit, seed live in the terminal
- **Custom options:** Animation strategy, wall color, perfect/imperfect mode, seed

### Color themes

7 wall color themes available: white, cyan, blue, green, red, yellow, magenta.

### The 42 pattern

Every maze with `WIDTH ≥ 11` and `HEIGHT ≥ 7` has the digits "42" stamped into the center as permanently-filled cells. These cells are excluded from generation and cannot be chosen as entry/exit points.

---

## Reusable Components

The codebase is deliberately decoupled. The following parts can be reused independently:

| Module | What it does |
|---|---|---|
| `maze/cell.py` — `Cell` | Represents a single grid cell with directional walls and a `to_hex()` encoder |
| `maze/grid.py` — `Grid` | 2D grid of `Cell` objects with `open_wall`, `close_wall`, `get_neighbors` | 
| `maze/generator.py` — `MazeGenerator` | Full generation + BFS solver, no UI dependency |
| `maze/writer.py` — `MazeWriter` | Serializes any `MazeGenerator` to the hex file format |
| `config/loader.py` | Parses and validates the `.txt` config file |
| `display/animator.py` — `Animator` | All animation state and strategy logic, zero curses dependency |
| `display/ui_utils.py` | Stateless curses helpers (`create_win_with_panel`, `center_text_win`) |

The `maze/` package has **no dependency on `display/`**

---

## Team & Project Management

### Roles

| Member | Responsibilities |
|---|---|
| [fadel-bo] | Maze generation algorithm, grid/cell data structures, BFS solver, file writer, makefile |
| [nouhiyli] | Curses UI, animation system, menu logic, config loader, integration , readme|

### Tools used

- **Python 3 + curses** — standard library only for the UI layer
- **mypy** — static type checking (all modules are fully annotated)
- **flake8** — style linting
- **pdb** — debugging via `make debug`
- **Git** — version control and collaboration
- **AI assistance:** 
---

## Resources

- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Depth-first search — Wikipedia](https://en.wikipedia.org/wiki/Depth-first_search)
- [Breadth-first search — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Jamis Buck — Maze generation in depth (blog series)](https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap)
- [Python curses documentation](https://docs.python.org/3/library/curses.html)
- [Python curses HOWTO](https://docs.python.org/3/howto/curses.html)