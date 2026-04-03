"""
display/ui_utils.py
Stateless curses utility helpers — no class, no state.
"""

import curses
import curses.panel


def create_win_with_panel(
    height: int,
    width: int,
    y: int,
    x: int,
    title: str,
    color_pair: int,
) -> tuple:
    """Create a bordered curses window + panel and return both."""
    win = curses.newwin(height, width, y, x)
    win.box()
    if title:
        win.addstr(0, 2, title, curses.color_pair(color_pair))
    panel = curses.panel.new_panel(win)
    panel.hide()
    curses.panel.update_panels()
    return win, panel


def center_text_win(win, text: str) -> None:
    """Write *text* centred inside *win* (single line, vertically centred)."""
    height, width = win.getmaxyx()
    lines = text.splitlines()
    start_y = max(1, (height - len(lines)) // 2)
    for i, line in enumerate(lines):
        x = max(1, (width - len(line)) // 2)
        try:
            win.addstr(start_y + i, x, line)
        except curses.error:
            pass


def center_text(stdscr, text: str) -> None:
    """Write *text* centred on *stdscr*."""
    center_text_win(stdscr, text)
