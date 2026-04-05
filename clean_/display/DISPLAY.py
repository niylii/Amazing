"""
display/display.py
Owns only drawing and window management.

Responsibilities
----------------

fro: win.addstr() callers.
"""

from __future__ import annotations

import curses
import curses.panel
from typing import TYPE_CHECKING

from display.ui_utils import create_win_with_panel, center_text_win

if TYPE_CHECKING:
    from maze.generator import MazeGenerator
    from display.ANIMATOR import Animator
    from display.MENU import Menu


# colour slot
BLACK   = 0
RED     = 1
GREEN   = 2
YELLOW  = 3
BLUE    = 4
MAGENTA = 5
CYAN    = 6
WHITE   = 8


class Display:
    """Pure rendering layer — never owns game state, never calls animate."""

    def __init__(self, stdscr: "curses._CursesWindow") -> None:
        self.stdscr = stdscr
        self.scr_height, self.scr_width = stdscr.getmaxyx()

        curses.curs_set(False)
        stdscr.nodelay(True)
        stdscr.box()

        self._init_colors()

        self.error_mod: bool = False

        try:
            self.create_maze_win()
            self.create_menu_win()
            self.create_help_win()
            self.create_input_popup("")
            self.create_error_popup()
        except curses.error:
            self.create_error_popup()
            self.error_mod = True

    # Colour initialisation
    def _init_colors(self) -> None:
        curses.start_color()
        curses.use_default_colors()

        curses.init_color(BLACK,   50,  55,  75)
        curses.init_color(RED,    600, 300, 350)
        curses.init_color(GREEN,  400, 550, 480)
        curses.init_color(YELLOW, 650, 550, 350)
        curses.init_color(BLUE,   400, 500, 700)
        curses.init_color(MAGENTA,600, 450, 650)
        curses.init_color(CYAN,   400, 600, 650)
        curses.init_color(WHITE,  600, 650, 750)

    def color_correction(self) -> None:
        """for good colors show up"""
        fg_map = [WHITE, CYAN, BLUE, GREEN, RED, YELLOW, MAGENTA]
        for i, fg in enumerate(fg_map, start=1):
            curses.init_pair(i, fg, BLACK)
            curses.init_pair(8, BLUE, BLACK)

    # Window creation
    def create_maze_win(self) -> None:
        self.maze_height = (self.scr_height * 3) // 4 - 1
        self.maze_width  = self.scr_width - 2
        self.maze_y      = 1
        self.maze_x      = 1
        self.maze_win, self.maze_panel = create_win_with_panel(
            self.maze_height, self.maze_width,
            self.maze_y, self.maze_x,
            "disp", 1,
        )
        self.maze_win.nodelay(True)

    def large_maze(self, maze) -> bool:
        needed_cols = maze.width  * 2 + 1
        needed_rows = maze.height * 2 + 1 + 3 # +3 for status bar + padding
        return needed_cols > self.maze_width or needed_rows > self.maze_height

    def create_menu_win(self) -> None:
        self.menu_height = self.scr_height // 4 - 1
        self.menu_width  = 40
        self.menu_y      = self.scr_height - self.scr_height // 4
        self.menu_x      = (self.scr_width - self.menu_width) // 2
        self.menu_win, self.menu_panel = create_win_with_panel(
            self.menu_height, self.menu_width,
            self.menu_y, self.menu_x,
            "", 1,
        )
        self.menu_win.keypad(True)
        self.menu_win.nodelay(True)

    def create_help_win(self) -> None:
        h = self.scr_height // 4 - 1
        w = self.scr_width  // 2 - 1
        y = (self.scr_height - h) // 2
        x = (self.scr_width  - w) // 2
        self.help_win, self.help_panel = create_win_with_panel(h, w, y, x, "help:", 1)
        center_text_win(
            self.help_win,
            "KEYS:\n"
            "space : toggles maze animation\n"
            "arrows: navigate up/down - left/right - swipe choises\n"
            "enter: is for entering values (for bottons only)\n"
            "cntl + C: Amazing says goodbye! lol\n"
            "CONFIG INSTRUCTIONS:\n"
            "width/height: integer > 0  (e.g. 20)\n"
            "entry/exit:* x,y  where x < width, y < height\n"
            "     * top-left is 0,0  (e.g. 0,0)\n"
            "           * entry and exit must be different\n"
            "seed: integer 1-500, or type: random\n"
            "⚠  press generate after any config change\n"
        )

    def create_input_popup(self, label: str) -> None:
        self.input_height = 3
        self.input_width  = 20
        self.input_y = self.menu_y + self.menu_height - 2
        self.input_x = self.menu_x + (self.menu_width // 4)
        self.input_win, self.input_panel = create_win_with_panel(
            self.input_height, self.input_width,
            self.input_y, self.input_x,
            label, 1,
        )
        from curses.textpad import Textbox
        self.sub_input_win = self.input_win.derwin(1, 18, 1, 1)
        self.input_box = Textbox(self.sub_input_win)

    def create_error_popup(self) -> None:
        error = f"Terminal too small!\nMaze needs {self.maze_width}x{self.maze_height} cells."
        error_1 = f"\nCurrent terminal: {self.scr_height}x{self.scr_width}\n"
        error_2 = "Please Ctr+C, resize your terminal then regenrate."
        resize = error + error_1 + error_2
        try:
            self.error_popup_win, self.popup_panel = create_win_with_panel(
                self.scr_height, self.scr_width, 0, 0, "pop up!", 5,
            )
            center_text_win(
                self.error_popup_win,
                resize
            )
        except curses.error:
            pass

    # Show / hide panels
    def show_maze(self) -> None:
        if self.maze_panel.hidden():
            self.maze_panel.show()
            self.maze_panel.top()

    def show_menu(self) -> None:
        if self.menu_panel.hidden():
            self.menu_panel.show()
            self.menu_panel.top()

    def show_input_popup(self, label: str = "") -> None:
        self.create_input_popup(label)
        if self.input_panel.hidden():
            self.input_panel.show()
            self.input_panel.top()

    def hide_input_popup(self) -> None:
        self.input_panel.hide()
        try:
            self.sub_input_win.clear()
            self.sub_input_win.refresh()
        except curses.error:
            pass

    def toggle_help(self) -> None:
        if self.help_panel.hidden():
            self.help_panel.show()
            self.help_panel.top()
        else:
            self.help_panel.hide()

    def show_error_popup(self) -> None:
        if self.popup_panel.hidden():
            self.popup_panel.show()
            self.popup_panel.top()

    # Drawing
    def draw_maze(
        self,
        maze: "MazeGenerator",
        animator: "Animator",
        walls_color_idx: int,
        toggle_animation: bool,
    ) -> None:
        mw = self.maze_win
        mw.erase()
        mw.box()

        start_x = (self.maze_width  - (maze.width  * 2 + 1)) // 2
        start_y = 2
        cell_char = "█"
        cell_color = walls_color_idx

        # draw solid grid 
        for y in range(maze.height * 2 + 1):
            for x in range(maze.width * 2 + 1):
                ch = cell_char if (x % 2 == 0 or y % 2 == 0) else ' '
                try:
                    mw.addstr(start_y + y, start_x + x, ch,
                               curses.color_pair(cell_color) if ch == cell_char else curses.A_NORMAL)
                except curses.error:
                    pass

        # apply animation steps (reveal passages) 
        for i in range(min(animator.maze_animation_step, len(animator.maze_timeline))):
            for (rel_y, rel_x) in animator.maze_timeline[i]:
                try:
                    mw.addstr(start_y + rel_y, start_x + rel_x, " ")
                except curses.error:
                    pass


        # force-clear 42 pattern
        for (cx, cy) in maze._pattern_42:
            real_x = (cx * 2) + 1
            real_y = (cy * 2) + 1
            try:
                mw.addstr(start_y + real_y, start_x + real_x, cell_char, curses.color_pair(8)|curses.A_BOLD)
            except curses.error:
                        pass


        # entry / exit markers 
        def cell_screen(cx: int, cy: int) -> tuple[int, int]:
            return start_x + cx * 2 + 1, start_y + cy * 2 + 1

        ex, ey = cell_screen(*maze.entry_point)
        xx, xy = cell_screen(*maze.exit_point)
        try:
            mw.addstr(ey, ex, cell_char, curses.color_pair((cell_color + 2) % 7 or 1))
            mw.addstr(xy, xx, cell_char, curses.color_pair((cell_color + 1) % 7 or 1))
        except curses.error:
            pass

        # status bar 
        anim_field = f"[animation {toggle_animation}]"
        seed_field  = f"[seed={maze.seed}]"
        try:
            mw.addstr(self.maze_height - 1, 1, "infos:")
            mw.addstr(self.maze_height - 1, 8, anim_field, curses.color_pair(3) | curses.A_BOLD)
            mw.addstr(self.maze_height - 1, 8 + len(anim_field) + 1, seed_field, curses.color_pair(3))
        except curses.error:
            pass

    def draw_path(
        self,
        maze: "MazeGenerator",
        path: str,
        animator: "Animator",
        walls_color_idx: int,
        initial_state: bool,
        path_shown: bool,
    ) -> None:
        if not path_shown or initial_state:
            return

        mw = self.maze_win
        start_x = (self.maze_width - (maze.width * 2 + 1)) // 2
        start_y = 2
        #♛
        cell_char = "▚"
        path_color = (walls_color_idx + 3) % 7 or 1

        ex, ey = maze.entry_point
        cur_x = start_x + ex * 2 + 1
        cur_y = start_y + ey * 2 + 1

        for i, direction in enumerate(path):
            if i >= animator.path_animation_step and animator.path_is_animating:
                break
            try:
                mw.addstr(cur_y, cur_x, cell_char, curses.color_pair(path_color))
                if direction == "N":
                    mw.addstr(cur_y - 1, cur_x, cell_char, curses.color_pair(path_color))
                    cur_y -= 2
                elif direction == "S":
                    mw.addstr(cur_y + 1, cur_x, cell_char, curses.color_pair(path_color))
                    cur_y += 2
                elif direction == "W":
                    mw.addstr(cur_y, cur_x - 1, cell_char, curses.color_pair(path_color))
                    cur_x -= 2
                elif direction == "E":
                    mw.addstr(cur_y, cur_x + 1, cell_char, curses.color_pair(path_color))
                    cur_x += 2
            except curses.error:
                pass

    def draw_menu(self, menu: "Menu", menu_state: str) -> None:
        mw = self.menu_win
        mw.erase()
        mw.box()

        try:
            mw.addstr(0, 2, f"{menu_state}:", curses.A_DIM | curses.A_REVERSE)
            mw.addstr(self.menu_height - 1, 2, "(?=help)", curses.A_DIM)
        except curses.error:
            pass

        for i, (label, _kind, selected) in enumerate(menu.render_items()):
            prefix = "> " if selected else "  "
            attr   = curses.A_REVERSE | curses.A_BOLD if selected else curses.A_NORMAL
            p_attr = curses.A_BLINK | (curses.A_REVERSE if selected else curses.A_NORMAL)
            try:
                mw.addstr(i + 2, 2, prefix, p_attr)
                mw.addstr(i + 2, 4, label,  attr)
            except curses.error:
                pass

    # Input box passthrough (reading handled by UI layer)
    def gather_input(self) -> str:
        return self.input_box.gather()

    def feed_key_to_input(self, key: int) -> None:
        self.sub_input_win.leaveok(True)
        self.input_box.do_command(key)

    # Resize
    def check_resized(self) -> bool:
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
            self.create_maze_win()
            self.create_menu_win()
            self.create_input_popup("")
            self.create_help_win()
            self.create_error_popup()
            self.error_mod = True
        except curses.error:
            self.create_error_popup()
            self.error_mod = True
