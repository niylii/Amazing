"""
display/ui.py
Application controller — owns the game loop and coordinates all layers.
"""

from __future__ import annotations

import curses
import curses.panel
import sys

from display.DISPLAY import Display
from display.ANIMATOR import Animator
from display.MENU import Action, Menu


class UI:
    """Coordinates Display, Animator, Menu, and Maze.  No direct drawing."""

    def __init__(self, stdscr: "curses._CursesWindow", maze) -> None:
        self.stdscr = stdscr
        self.maze = maze
        self.path: str = maze.solve()

        # sub-components
        self.display = Display(stdscr)
        self.animator = Animator(maze)
        self.menu = Menu({
            "width":  maze.width,
            "height": maze.height,
            "entry":  maze.entry_point,
            "exit":   maze.exit_point,
            "seed":   maze.seed,
            "perfect": maze.perfect,
        })

        self.initial_state: bool = True

        self.animator.current_strategy = self.menu.current_animation
        self.animator.build_maze_timeline()
        self.animator.maze_is_animating = True

    # Main loop
    def run(self) -> None:
        while True:
            self.display.color_correction()

            if self.display.check_resized():
                self.display.resize_windows()

            # check if maze fits in the maze window (not full terminal)
            needed_cols = self.maze.width * 2 + 1
            needed_rows = self.maze.height * 2 + 1 + 3
            maze_fits = (
                needed_cols <= self.display.maze_width and
                needed_rows <= self.display.maze_height
            )

            if not maze_fits:
                self.display.error_mod = True
            else:
                self.display.error_mod = False

            if not self.display.error_mod:
                self.display.popup_panel.hide()
                self.display.show_maze()
                self.display.show_menu()

                # maze small fit
                from display.ui_utils import center_text_win
                if self.maze.pattern_42_warning:
                    center_text_win(self.display.error_popup_win,
                                    self.maze.pattern_42_warning)
                    self.display.show_error_popup()

                # advance animations
                self.animator.step_maze()
                if not self.animator.maze_is_animating:
                    self.initial_state = False
                self.animator.step_path()

                # draw everything
                try:
                    self.display.draw_maze(
                        self.maze,
                        self.animator,
                        self.menu.walls_color_index + 1,
                        self.animator.toggle_animation,
                    )
                    self.display.draw_path(
                        self.maze,
                        self.path,
                        self.animator,
                        self.menu.walls_color_index + 1,
                        self.initial_state,
                        self.animator.path_shown,
                    )
                    self.display.draw_menu(self.menu, self.menu.state)
                    self.display.error_mod = False
                except (AttributeError, curses.error):
                    self.display.error_mod = True

            else:
                # hide maze and menu panels so they don't bleed through
                try:
                    self.display.maze_panel.hide()
                    self.display.menu_panel.hide()
                except Exception:
                    pass

                # redraw error popup with live accurate numbers
                try:
                    self.display.error_popup_win.erase()
                    self.display.error_popup_win.box()
                    from display.ui_utils import center_text_win
                    center_text_win(
                        self.display.error_popup_win,
                        f"Oh oh ! Terminal too small!\n"
                        f"Maze needs : {needed_cols} cols x {needed_rows} "
                        f"rows\n"
                        f"Terminal is: {self.display.maze_width} cols x "
                        f"{self.display.maze_height} rows\n"
                        f"Please Ctr+C then resize your terminal and "
                        "regenerate.",
                    )
                except curses.error:
                    pass
                self.display.show_error_popup()

            curses.panel.update_panels()
            curses.doupdate()

            self._process_input()
            curses.napms(30)

    # Input processing
    def _process_input(self) -> None:
        # toggle nodelay based on animation state
        animating = self.animator.maze_is_animating or {
            self.animator.path_is_animating}
        self.display.menu_win.nodelay(animating)

        try:
            key = self.display.menu_win.getch()
        except curses.error:
            return
        if key == -1:
            return

        # input-popup mode
        if self.menu.input_mode:
            if getattr(self, '_skip_next_enter', False):
                self._skip_next_enter = False
                if key in (10, 13, curses.KEY_ENTER):
                    return

            if key in (10, 13, curses.KEY_ENTER, 7):
                raw = self.display.gather_input()
                ok = self.menu.commit_input(raw)
                if not ok:
                    try:
                        curses.flash()
                    except curses.error:
                        pass
                    self.menu.cancel_input()
                self.display.hide_input_popup()
            elif key in (27,):
                self.menu.cancel_input()
                self.display.hide_input_popup()
            else:
                _SAFE = set(range(32, 127)) | {curses.KEY_BACKSPACE, 127, 8}
                if key in _SAFE:
                    try:
                        self.display.feed_key_to_input(key)
                    except Exception:
                        pass
            return

        #  global shortcuts
        if key == ord(' '):
            self.animator.toggle_animation = not self.animator.toggle_animation
            return

        if key == ord('?'):
            self.display.toggle_help()
            return

        if key == curses.KEY_RESIZE:
            return

        #  delegate to menu
        action = self.menu.handle_key(key)

        # check if menu just entered input mode
        if self.menu.input_mode:
            self._skip_next_enter = True
            label = f"{self.menu.input_source}:"
            self.display.show_input_popup(label)
            return

        self._handle_action(action)

    def _handle_action(self, action: Action) -> None:
        if action == Action.NONE:
            return

        elif action == Action.GENERATE:
            from maze.generator import MazeGenerator
            cfg = self.menu.config
            self.maze = MazeGenerator(
                cfg["width"],
                cfg["height"],
                cfg["seed"],
                self.menu.perfect,
                cfg["entry"],
                cfg["exit"],
            )
            self.maze.generate()
            self.path = self.maze.solve()
            self.animator.reset(
                self.maze,
                self.menu.current_animation,
                self.animator.toggle_animation,
            )
            self.initial_state = True

        elif action == Action.SHOW_PATH:
            if self.animator.maze_is_animating:
                return
            self.path = self.maze.solve()
            self.animator.path_shown = not self.animator.path_shown
            self.animator.path_is_animating = True
            self.animator.path_animation_step = 0

        elif action == Action.EXIT:
            sys.exit(0)


# Entry point called by curses.wrapper
def run_ui(stdscr: "curses._CursesWindow", maze) -> None:
    ui = UI(stdscr, maze)
    ui.run()
