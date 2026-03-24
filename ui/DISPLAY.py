import curses
import curses.panel
import time
import random
from collections import deque
from curses.textpad import Textbox

from typing import TypeAlias
from maze.mazegen import MazeGenerator
from ui.ui_utils import create_win_with_panel, center_text_win
from ui.ANIMATION import prepare_maze_timeline, animate_maze, animate_path

CWindow: TypeAlias = curses.window
Maze: TypeAlias = MazeGenerator

BLACK = 0
RED = 1
GREEN = 2
YELLOW = 3
BLUE = 4
MAGENTA = 5
CYAN = 6
WHITE = 8


class Display:
    stdscr: CWindow
    menu_win: CWindow
    maze: Maze
    error_mod: bool
    maze_state: bool

    def __init__(self, maze: Maze, stdscr: CWindow) -> None:
        self.INITIAL_STATE: bool = True
        self.theme = "dark"

        self.maze = maze
        self.path: str = self.maze.solve()

        curses.start_color()
        curses.use_default_colors()

        self.maze_is_animating: bool = False
        self.path_is_animating: bool = False
        self.togle_animation: bool = True
        self.path_shown: bool = False

        self.maze_animation_step: int = 0
        self.maze_animation_step_number: int = 1
        self.last_time_maze_animation: float = time.time()
        self.path_animation_step: int = 0
        self.last_time_path_animation: float = time.time()

        self.stdscr = stdscr
        curses.curs_set(False)
        self.stdscr.nodelay(True)
        self.stdscr.box()
        self.scr_height, self.scr_width = stdscr.getmaxyx()

        # Menu & selectors setup
        self.menu_state = "main"
        self.selectors_data = {
            "animation": [],
            "walls color": [("white", 1), ("cyan", 2), ("blue", 3), ("green", 4), ("red", 5), ("yellow", 6), ("magenta", 7)],
            "path color": [("cyan", 2), ("blue", 3)],
            "theme": [("dark", "dark"), ("light", "light")],
            "perfect ": [("on", True), ("off", False)],
        }
        self.selectors_indexes = {k: 0 for k in self.selectors_data.keys()}

        # Config
        self.config = {
            "width": self.maze.width,
            "height": self.maze.height,
            "entry": self.maze.entry_point,
            "exit": self.maze.exit_point,
            "seed": self.maze.seed,
            "perfect": self.maze.perfect,
        }

        self.input_mod = False
        self.input_done = False
        self.input_come_from: str

        # Panels
        try:
            self.create_maze()
            self.create_menu()
            self.create_help()
            self.create_input_popup("")
            self.create_error_popup()
            self.error_mod = False
        except curses.error:
            self.create_error_popup()
            self.error_mod = True

    # ================== Window / popup creation ==================
    def create_input_popup(self, label: str) -> None:
        self.input_height = 3
        self.input_width = 20
        self.input_y = self.menu_y + self.menu_height - 2
        self.input_x = self.menu_x + (self.menu_width // 4)
        self.input_win, self.input_panel = create_win_with_panel(
            self.input_height, self.input_width, self.input_y, self.input_x, label, 1
        )
        self.sub_input_win = self.input_win.derwin(1, 18, 1, 1)
        self.input_box = Textbox(self.sub_input_win)

    def show_input_popup(self) -> None:
        if self.input_panel.hidden():
            self.input_panel.show()
            self.input_panel.top()

    def create_error_popup(self) -> None:
        try:
            self.error_popup_win, self.popup_panel = create_win_with_panel(
                self.scr_height, self.scr_width, 0, 0, "pop up!", 5
            )
            center_text_win(self.error_popup_win, f"resize windows! {self.scr_height}x{self.scr_width}")
        except curses.error:
            pass

    def show_error_popup(self) -> None:
        if self.popup_panel.hidden():
            self.popup_panel.show()
            self.popup_panel.top()

    def create_help(self) -> None:
        self.help_height = self.scr_height // 4 - 1
        self.help_width = self.scr_width // 2 - 1
        self.help_y = (self.scr_height - self.help_height) // 2
        self.help_x = (self.scr_width - self.help_width) // 2
        self.help_win, self.help_panel = create_win_with_panel(
            self.help_height, self.help_width, self.help_y, self.help_x, "help:", 1
        )

        help_option = """\
space: toggle maze animation
k/⭡-j/⭣: navigate up/down
"""
        center_text_win(self.help_win, help_option)

    def show_help(self) -> None:
        if self.help_panel.hidden():
            self.help_panel.show()
            self.help_panel.top()
        else:
            self.help_panel.hide()

    # ================== Maze & Menu creation ==================
    def create_menu(self) -> None:
        self.menu_height = self.scr_height // 4 - 1
        self.menu_width = 40
        self.menu_y = self.scr_height - self.scr_height // 4
        self.menu_x = (self.scr_width - self.menu_width) // 2
        self.menu_win, self.menu_panel = create_win_with_panel(self.menu_height, self.menu_width, self.menu_y, self.menu_x, "", 1)
        self.menu_win.keypad(True)
        self.menu_win.nodelay(True)

    def show_menu(self) -> None:
        if self.menu_panel.hidden():
            self.menu_panel.show()
            self.menu_panel.top()

    def create_maze(self) -> None:
        self.maze_height = (self.scr_height * 3) // 4 - 1
        self.maze_width = self.scr_width - 2
        self.maze_y = 1
        self.maze_x = 1
        self.maze_win, self.maze_panel = create_win_with_panel(self.maze_height, self.maze_width, self.maze_y, self.maze_x, "disp", 1)
        self.maze_win.nodelay(True)

    def show_maze(self) -> None:
        if self.maze_panel.hidden():
            self.maze_panel.show()
            self.maze_panel.top()

    # ================== Resizing ==================
    def check_isresized(self) -> bool:
        y, x = self.stdscr.getmaxyx()
        return y != self.scr_height or x != self.scr_width

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
            self.create_input_popup("")
            self.create_help()
            self.create_error_popup()
        except curses.error:
            self.create_error_popup()