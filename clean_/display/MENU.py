"""
display/menu.py
Menu state, selector values, and navigation logic.

Rules
-----
"""

from __future__ import annotations

import curses
from enum import Enum, auto
from typing import Callable
import sys


# ------------------------------------------------------------------
# Actions the menu can emit
# ------------------------------------------------------------------

class Action(Enum):
    NONE         = auto()
    GENERATE     = auto()
    SHOW_PATH    = auto()
    OPEN_CONFIG  = auto()
    OPEN_CUSTOM  = auto()
    BACK         = auto()
    EXIT         = lambda: sys.exit(0)


# ------------------------------------------------------------------
# Menu
# ------------------------------------------------------------------

class Menu:
    """
    Owns all menu state and key-handling.
    Returns Action values; never touches the screen.
    """

    def __init__(self, maze_config: dict) -> None:
        # ---- selector data & indexes ----
        self.selectors_data: dict[str, list] = {
            "animation":   [
                "line by line",
                "cell by cell",
                "random",
                "prim",
                "spread",
                "oil effect",
            ],
            "walls color": ["white", "cyan", "blue", "green", "red", "yellow", "magenta"],
            "perfect":    ["on", "off"],
        }
        self.selectors_indexes: dict[str, int] = {k: 0 for k in self.selectors_data}

        # ---- config (mirrors maze parameters) ----
        self.config: dict = dict(maze_config)

        # ---- menu state ----
        self.state: str = "MENU"
        self.selected_index: int = 0

        # ---- input-popup state ----
        self.input_mode: bool = False
        self.input_source: str = ""          # which config key we're editing
        self.pending_action: Action = Action.NONE

        # ---- build menus ----
        self._build_menus()

    # ------------------------------------------------------------------
    # Properties — convenient single-value accessors
    # ------------------------------------------------------------------

    @property
    def current_animation(self) -> str:
        return self.selectors_data["animation"][self.selectors_indexes["animation"]]

    @property
    def walls_color_index(self) -> int:
        return self.selectors_indexes["walls color"]

    @property
    def perfect(self) -> bool:
        return self.selectors_data["perfect"][self.selectors_indexes["perfect"]] == "on"
    # ------------------------------------------------------------------
    # Menu structure
    # ------------------------------------------------------------------

    def _build_menus(self) -> None:
        c = self.config

        self.main_items: list[tuple[str, str]] = [
            ("generate",      "button"),
            ("show path",     "button"),
            ("maze config",   "button"),
            ("custom option", "button"),
            ("exit maze",     "button"),
        ]

        self.config_items: list[tuple[str, str]] = [
            (f"width : {c.get('width', '?')}",   "button"),
            (f"height : {c.get('height', '?')}", "button"),
            (f"entry : {c.get('entry', '?')}",   "button"),
            (f"exit : {c.get('exit', '?')}",     "button"),
            ("back",                             "button"),
        ]

        self.custom_items: list[tuple[str, str]] = [
            ("animation",   "selector"),
            ("walls color", "selector"),
            ("perfect",     "selector"), 
            ("seed",        "button"),
            ("back",        "button"),
        ]

        self._apply_state()

    def _rebuild_config_items(self) -> None:
        c = self.config
        self.config_items = [
            (f"width : {c.get('width', '?')}",                         "button"),
            (f"height : {c.get('height', '?')}",                       "button"),
            (f"entry : {c.get('entry', '?')}",                         "button"),
            (f"exit : {c.get('exit', '?')}",                           "button"),
            ("perfect",                                               "selector"),
            (f"seed : {c.get('seed') if c.get('seed') else 'random'}", "button"),
            ("back",                                                   "button"),
        ]
        if self.state == "config":
            self.current_items = self.config_items

    def _apply_state(self) -> None:
        if self.state == "MENU":
            self.current_items = self.main_items
        elif self.state == "config":
            self.current_items = self.config_items
        elif self.state == "custom":
            self.current_items = self.custom_items

    # ------------------------------------------------------------------
    # Key handling  (call from the UI event loop)
    # ------------------------------------------------------------------

    def handle_key(self, key: int) -> Action:
        """
        Process a single keypress.
        Returns an Action the UI controller should act on.
        Does NOT modify curses state.
        """
        if not self.current_items:
            return Action.NONE
        items = self.current_items
        name, kind = items[self.selected_index]
        # ---- vertical navigation ----
        if key == curses.KEY_UP:
            self.selected_index = (self.selected_index - 1) % len(items)
            return Action.NONE

        if key == curses.KEY_DOWN:
            self.selected_index = (self.selected_index + 1) % len(items)
            return Action.NONE

        # ---- selector left/right ----
        if kind == "selector":
            if key == curses.KEY_LEFT:
                self.selectors_indexes[name] = (
                    self.selectors_indexes[name] - 1
                ) % len(self.selectors_data[name])
            elif key == curses.KEY_RIGHT:
                self.selectors_indexes[name] = (
                    self.selectors_indexes[name] + 1
                ) % len(self.selectors_data[name])
            return Action.NONE
        
        # if name.strip() == "perfect":
        #     self.config["perfect"] = self.perfect

        # ---- button enter ----
        if key in (curses.KEY_ENTER, ord('\n'), 10, 13):
            return self._activate(name)

        return Action.NONE

    def _activate(self, name: str) -> Action:
        """Map a button name to an Action."""
        _map: dict[str, Action] = {
            "generate":      Action.GENERATE,
            "show path":     Action.SHOW_PATH,
            "maze config":   Action.OPEN_CONFIG,
            "custom option": Action.OPEN_CUSTOM,
            "exit maze":     Action.EXIT,
            "back":          Action.BACK,
        }

        # config sub-buttons → request input popup via pending_action
        config_inputs = {
            "width",
            "height",
            "entry",
            "exit",
            "seed",
        }
        # strip trailing label (e.g. "width : 10" → "width")
        base = name.split(" : ")[0].strip()
        if base in config_inputs:
            self.input_source = base
            self.input_mode = True
            return Action.NONE

        action = _map.get(name, Action.NONE)
        if action == Action.OPEN_CONFIG:
            self.state = "config"
            self.selected_index = 0
            self._apply_state()
            return Action.NONE        # UI re-draws; action handled internally
        if action == Action.OPEN_CUSTOM:
            self.state = "custom"
            self.selected_index = 0
            self._apply_state()
            return Action.NONE
        if action == Action.BACK:
            return self._go_back()

        return action

    def _go_back(self) -> Action:
        self.state = "MENU"
        self.selected_index = 0
        self._apply_state()
        return Action.NONE

    # ------------------------------------------------------------------
    # Input-popup callbacks
    # ------------------------------------------------------------------

    def commit_input(self, raw: str) -> bool:
        """
        Called by UI once the user confirms the input popup.
        Returns True if the value was valid, False otherwise.
        """
        raw = raw.strip()
        if not raw:
            return False
        key = self.input_source

        if key == "seed":
            if raw.lower() == "random":
                self.config["seed"] = None
            else:
                try:
                    val = int(raw)
                except (ValueError, TypeError):
                    return False
                if val <= 0 or val > 500:
                    return False
                self.config["seed"] = val

        elif key in ("width", "height"):
            if raw.isdecimal() and int(raw) > 0:
                self.config[key] = int(raw)
            else:
                return False

        elif key in ("entry", "exit"):
            coord = self._parse_coords(raw, editing=key)
            # coord = self._parse_coords(raw)
            if coord == (-1, -1):
                return False
            self.config[key] = coord

        self.input_mode = False
        self._rebuild_config_items()
        return True

    def cancel_input(self) -> None:
        self.input_mode = False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _parse_coords(self, s: str, editing: str = "") -> tuple[int, int]:
    # def _parse_coords(self, s: str) -> tuple[int, int]:
        try:
            parts = s.split(',')
            if len(parts) != 2:
                return (-1, -1)
            x, y = int(parts[0].strip()), int(parts[1].strip())
            if (x, y) in (self.config.get("entry"), self.config.get("exit")):
                return (-1, -1)
            if x >= self.config.get("width", 0) or y >= self.config.get("height", 0):
                return (-1, -1)
            if x < 0 or y < 0:
                return (-1, -1)
            return (x, y)
        except (ValueError, AttributeError):
            return (-1, -1)

    # ------------------------------------------------------------------
    # Read-only view for the renderer
    # ------------------------------------------------------------------

    def render_items(self) -> list[tuple[str, str, bool]]:
        """
        Return [(label, kind, is_selected), ...] for the current menu.
        Selectors have their current value embedded in the label.
        """
        result = []
        for i, (name, kind) in enumerate(self.current_items):
            if kind == "selector":
                val = self.selectors_data[name][self.selectors_indexes[name]]
                label = f"{name}: < {val} >"
            else:
                label = name
            result.append((label, kind, i == self.selected_index))
        return result
