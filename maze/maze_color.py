import curses
import curses.panel
import random
from typing import Dict
import time
# from  fake_generator import Cell, generate_fake_maze


from typing import Dict, Any
from validate_config import validate
from Errors import InvalidEntryError, InvalidFileError, InvalidArgumentError
from mazegen import MazeGenerator, MazeWriter, cell

import sys
import os



type CWindow = curses.window
type Maze = MazeGenerator

def center_text(win : CWindow, texte : str, y : int):
    _, width = win.getmaxyx()
    x = (width - len(texte)) // 2
    win.addstr(y, x, texte)

def center_text_win(win, texte):
    height, width = win.getmaxyx()
    lignes = texte.split("\n")
    start_y = (height - len(lignes)) // 2
    for i, ligne in enumerate(lignes):
        x = (width - len(ligne)) // 2
        win.addstr(start_y + i, x, ligne)

def create_win_with_panel(h, w, y, x, title, color_pair = 0):
    win = curses.newwin(h, w, y, x)
    win.bkgd(' ', curses.color_pair(1))
    win.box()
    win.addstr(0, 1, title)
    panel = curses.panel.new_panel(win)
    panel.hide()
    return win, panel



class Display:
    stdscr: CWindow
    menu_win: CWindow
    menu_panel: curses.panel.panel
    maze: Maze
    error_mod : bool
    maze_state : bool


    def __init__(self, maze: Maze, stdscr: CWindow) -> None:
        self.error_mod : bool = False
        self.INITIAL_STATE : bool = True


        self.maze_animation_step : int = 0
        self.maze_is_animating : bool = False
        self.last_time_maze_animation : float = time.time()

        self.path_animation_step : int = 0
        self.path_is_animating : bool = False
        self.last_time_path_animation : float = time.time()

        self.stdscr = stdscr
        curses.curs_set(False)
        self.stdscr.nodelay(True)
        self.stdscr.box()

        self.maze = maze
        self.scr_height, self.scr_width = stdscr.getmaxyx()
        self.selected_index = 0

        self.path : str = self.maze.solve()
        self.path_shown : bool = False

        self.create_maze()
        self.create_menu()
        self.create_error_popup()

    def create_error_popup(self) -> None:
        self.error_popup_win, self.popup_panel = create_win_with_panel(
            self.scr_height,
            self.scr_width,
            0,
            0,
            "pop up!",
        )
        center_text_win(self.error_popup_win, f"resize windows!{self.scr_height}x{self.scr_width}")


    def show_error_popup(self) -> None:
        if self.popup_panel.hidden():
            self.popup_panel.show()
            self.menu_panel.hide()
            self.maze_panel.hide()
            self.popup_panel.top()

    def create_menu(self) -> None:
        self.menu_height = self.scr_height // 4 - 1
        self.menu_width  = self.scr_width // 2 - 1
        self.menu_y = self.scr_height - self.scr_height // 4
        self.menu_x = (self.scr_width - self.menu_width) // 2
        self.menu_win, self.menu_panel = create_win_with_panel(
            self.menu_height,
            self.menu_width,
            self.menu_y,
            self.menu_x,
            "menu:",
            1
        )
        self.menu_win.keypad(True)
        self.menu_win.nodelay(True)
        self.menu_items = ["generate", "show_path", "quit"]
#add a button to change color,

    def show_menu(self) -> None:
        if self.menu_panel.hidden():
            self.menu_panel.show()
            self.menu_panel.top()

    def create_maze(self) -> None:
        self.maze_height = (self.scr_height  * 3) // 4 - 1 
        self.maze_width  = self.scr_width - 2
        self.maze_y = 1
        self.maze_x = 1
        self.maze_win, self.maze_panel = create_win_with_panel(
             self.maze_height,
            self.maze_width,
            self.maze_y,
            self.maze_x,
            "disp",
            1
        )
        self.maze_win.nodelay(True)

    def show_maze(self) -> None:
        if self.maze_panel.hidden():
            self.maze_panel.show()
            self.maze_panel.top()


    def draw_menu(self) -> None:
        _, width = self.menu_win.getmaxyx()
        center_text(self.menu_win, "OPTIONS", 0)
        for i, item in enumerate(self.menu_items):
            prefix = "> " if i == self.selected_index else "  "
            x = (width - 13) // 2
            self.menu_win.addstr(i + 2, x, prefix + item, curses.color_pair(1))


    def handle_menu_input(self) -> str | None:
        try:
            key = self.menu_win.getch()
        except curses.error:
            return None
        if key == curses.KEY_UP:
            self.selected_index = (self.selected_index - 1) % len(self.menu_items)
        elif key == curses.KEY_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.menu_items)
        elif key in [curses.KEY_ENTER, ord('\n')]:
            return self.menu_items[self.selected_index]
        elif key == ord(' '):
            return None


    def prepare_maze_timeline(self):
        self.maze_timeline = []
        maze = self.maze
        
        for y in range(maze.height):
            for x in range(maze.width):
                cell = maze.grid.get_cell(x, y)
                
                real_x = (x * 2) + 1
                real_y = (y * 2) + 1
                
                actions = [(real_y, real_x)]
                
                if cell.walls["N"]: actions.append((real_y - 1, real_x))
                if cell.walls["S"]: actions.append((real_y + 1, real_x))
                if cell.walls["W"]: actions.append((real_y, real_x - 1))
                if cell.walls["E"]: actions.append((real_y, real_x + 1))
                
                self.maze_timeline.append(actions)


    def animate_maze(self) -> None:
        delay : float = 0.03 
        if not self.maze_is_animating:
            return
        
        current_time = time.time()

        if current_time - self.last_time_maze_animation >= delay:
            
            if self.maze_animation_step < len(self.maze_timeline):
                self.maze_animation_step += 1
                self.last_time_maze_animation = current_time

            else:
                self.maze_is_animating = False
                self.INITIAL_STATE = False


    def animate_path(self) -> None:
        delay : float = 0.03
        if not self.path_is_animating or self.maze_is_animating:
            return

        current_time = time.time()

        if current_time - self.last_time_path_animation >= delay:
            
            if self.path_animation_step < len(self.path):
                self.path_animation_step += 1
                self.last_time_path_animation = current_time

            else:
                self.path_is_animating = False



    def draw_path(self) -> None:
        if self.path_shown == False or self.INITIAL_STATE == True:
            return
        maze_win = self.maze_win
        maze = self.maze

        path = self.path

        start_x = (self.maze_width - (maze.width * 2 + 1)) // 2
        start_y = 4
        cell_char = "█"

        entry_x, entry_y = maze.entry_point
        exit_x, exit_y = maze.exit_point

        entry_x = start_x + (entry_x) * 2 + 1
        entry_y = start_y + (entry_y) * 2 + 1

        exit_x = start_x + (exit_x) * 2 + 1
        exit_y = start_y + (exit_y) * 2 + 1

        for i, dir in enumerate(path):
            if i >= self.path_animation_step and self.path_is_animating:
                break
            if dir == "N":
                maze_win.addstr(entry_y, entry_x, cell_char, curses.color_pair(2))
                maze_win.addstr(entry_y - 1, entry_x, cell_char, curses.color_pair(2))
                entry_y -= 2
            if dir == "S":
                maze_win.addstr(entry_y, entry_x, cell_char, curses.color_pair(2))
                maze_win.addstr(entry_y + 1, entry_x, cell_char, curses.color_pair(2))
                entry_y += 2
            if dir == "W":
                maze_win.addstr(entry_y, entry_x, cell_char, curses.color_pair(2))
                maze_win.addstr(entry_y, entry_x - 1, cell_char, curses.color_pair(2))
                entry_x -= 2
            if dir == "E":
                maze_win.addstr(entry_y, entry_x, cell_char, curses.color_pair(2))
                maze_win.addstr(entry_y, entry_x + 1, cell_char, curses.color_pair(2))
                entry_x += 2

        # print(maze.solve(), file=sys.stderr)



    def draw_maze(self) -> None:
        maze_win = self.maze_win
        maze = self.maze
        maze_win.erase()
        maze_win.box()

        start_x = (self.maze_width - (maze.width * 2 + 1)) // 2
        start_y = 4
        cell_char = "█"

        entry_x, entry_y = maze.entry_point
        exit_x, exit_y = maze.exit_point

        entry_x = start_x + (entry_x) * 2 + 1
        entry_y = start_y + (entry_y) * 2 + 1

        exit_x = start_x + (exit_x) * 2 + 1
        exit_y = start_y + (exit_y) * 2 + 1

        for y in range(maze.height * 2 + 1):
            for x in range(maze.width * 2 + 1):
                if x % 2 == 0 or y % 2 == 0:
                    maze_win.addstr(start_y + y, start_x + x, cell_char, curses.color_pair(5))

        for i in range(min(self.maze_animation_step, len(self.maze_timeline))):
            cell_actions = self.maze_timeline[i]
            for (rel_y, rel_x) in cell_actions:
                maze_win.addstr(start_y + rel_y, start_x + rel_x, " ")

        maze_win.addstr(entry_y, entry_x, cell_char, curses.color_pair(4))
        maze_win.addstr(exit_y, exit_x, cell_char, curses.color_pair(3))



    def exit_programme(self) -> None:
        exit(0)


    def generate(self) -> None:
        if not self.INITIAL_STATE and not self.path_is_animating:
            maze = self.maze
            self.maze = MazeGenerator(
                maze.width,
                maze.height, 
                None,
                maze.perfect,
                maze.entry_point,
                maze.exit_point
            )
            self.path = self.maze.solve()

        self.prepare_maze_timeline()
        self.maze_is_animating = True

    def show_path(self) -> None:
        if self.maze_is_animating:
            return
        self.path_shown = not self.path_shown
        self.path_is_animating = not self.path_is_animating


    def menu(self) -> None:

        menu_options : Dict= {
            "quit": self.exit_programme,
            "generate": self.generate,
            "show_path": self.show_path
      #      "change_color": self.change_color
        }

        option : str|None = self.handle_menu_input()
        menu_option = menu_options.get(option)
        if menu_option is None:
            return
        menu_option()

    def check_isresized(self) -> bool:
        y, x = self.stdscr.getmaxyx()
        if y != self.scr_height or x != self.scr_width:
            return True
        return False


    def resize_windows(self) -> None:
        try:
            y, x = self.stdscr.getmaxyx()
            self.scr_height, self.scr_width = y, x
            curses.resizeterm(y, x)
            curses.update_lines_cols()

            self.stdscr.clear()
            self.stdscr.box()
            self.create_maze()
            self.create_menu()
            self.create_error_popup()
        except curses.error:
            self.stdscr.clear()
            self.stdscr.box()


C1 = 250
C2 = 251
C3 = 252
C4 = 253
C5 = 254
C6 = 255

lavander = []
storm = []
tokyo_night = []
cutie = []

def display(stdscr : CWindow, maze : Maze) -> None:
    curses.start_color()
    curses.init_color(C1, 980, 1000, 910)   # FAFFE8
    curses.init_color(C2, 741, 949, 949)    # BDF2F2
    curses.init_color(C3, 651, 780, 1000)   # A6C7FF
    curses.init_color(C4, 478, 431, 769)    # 7A6EC4
    curses.init_color(C5, 859, 561, 769)    # DB8FC4
    curses.init_color(C6, 1000, 710, 820)   # FFB5D1

    curses.init_pair(1, C4, C1)  # UI (menu / borders)
    curses.init_pair(2, C6, curses.COLOR_BLACK)  # path
    curses.init_pair(3, C5, curses.COLOR_BLACK)  # exit
    curses.init_pair(4, C3, curses.COLOR_BLACK)  # entry
    curses.init_pair(5, C2, curses.COLOR_BLACK)  # maze walls
    displayer : Display = Display(maze, stdscr)
    displayer.prepare_maze_timeline()

    while True:
        if not displayer.error_mod:
            displayer.popup_panel.hide()
            displayer.show_maze()
            displayer.show_menu()
            displayer.menu()
        else:
            displayer.show_error_popup()

        try:
            displayer.animate_maze()
            displayer.draw_maze()

            displayer.animate_path()
            displayer.draw_path()

            displayer.draw_menu()
            displayer.error_mod = False
        except curses.error:
            displayer.error_mod = True

        if displayer.check_isresized() == True:
            displayer.resize_windows()
             
        curses.panel.update_panels()
        curses.doupdate()


def main() -> None:
    """Entry point for the maze generator program.

    Reads the configuration file path from command-line arguments,
    validates it, generates a maze, and prints the solution path.

    Raises:
        InvalidArgumentError: If the wrong number of arguments is provided.
        InvalidFileError: If the config file has an invalid extension.
        InvalidEntryError: If the config file contains invalid entries.
    """
    try:
        if len(sys.argv) != 2:
            raise InvalidArgumentError(
                "Usage: python3 a_maze_ing.py config.txt"
            )

        filename: str = sys.argv[1]
        _, extension = os.path.splitext(filename)

        if extension != ".txt":
            raise InvalidFileError(
                "Configuration file must be plain text (e.g. config.txt)."
            )

        config: Dict[str, Any] = validate(filename)

        maze = MazeGenerator(
            width=config['WIDTH'],
            height=config['HEIGHT'],
            seed=config['SEED'],
            perfect=config['PERFECT'],
            entry_point=config['ENTRY'],
            exit_point=config['EXIT']
        )

        maze_writer = MazeWriter(maze, config["OUTPUT_FILE"])
        maze_writer.write()
        curses.wrapper(display, maze)

    except (InvalidEntryError, InvalidFileError, InvalidArgumentError) as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
