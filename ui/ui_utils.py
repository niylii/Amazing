import curses

type c_window = curses.window


def center_text(win: c_window, texte: str, y: int):
    _, width = win.getmaxyx()
    x = (width - len(texte)) // 2
    win.addstr(y, x - 1, texte)


def center_text_win(win, texte):
    height, width = win.getmaxyx()
    lignes = texte.split("\n")
    start_y = (height - len(lignes)) // 2
    for i, ligne in enumerate(lignes):
        x = (width - len(ligne)) // 2
        win.addstr(start_y + i, x, ligne)


def create_win_with_panel(h, w, y, x, title, color_pair=0):
    win = curses.newwin(h, w, y, x)
    win.bkgd(' ', curses.color_pair(color_pair))
    win.box()
    win.addstr(0, 1, title)
    panel = curses.panel.new_panel(win)
    panel.hide()
    return win, panel
