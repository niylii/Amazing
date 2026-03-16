import curses
import curses.panel
from typing import Dict
from  fake_generator import Cell, Maze, generate_fake_maze

type CWindow = curses.window

def center_text(win : CWindow, texte : str, y : int):
    _, width = win.getmaxyx()
    x = (width - len(texte)) // 2
    win.addstr(y, x, texte)

class Display:
    stdscr: CWindow
    menu_win: CWindow
    menu_panel: curses.panel.panel
    maze: Maze

    def __init__(self, maze: Maze, stdscr: CWindow) -> None:
        curses.curs_set(False)

        self.stdscr = stdscr
        self.stdscr.nodelay(True)


        self.maze = maze
        self.scr_height, self.scr_width = stdscr.getmaxyx()
        self.selected_index = 0
        self.create_maze()
        self.create_menu()

    def create_menu(self) -> None:
        self.menu_height = self.scr_height // 4
        self.menu_width  = self.scr_width // 2
        self.menu_y = self.scr_height - self.scr_height // 4
        self.menu_x = self.scr_width // 4
        self.menu_win = curses.newwin(
            self.menu_height,
            self.menu_width,
            self.menu_y,
            self.menu_x
        )
        self.menu_win.keypad(True)
        self.menu_win.border()
        self.menu_win.nodelay(True)
        self.menu_items = ["generate", "draw path", "quit"]
        self.menu_panel = curses.panel.new_panel(self.menu_win)
        self.menu_panel.bottom()
        self.menu_panel.show()

    def draw_menu(self) -> None:
        _, width = self.menu_win.getmaxyx()
        center_text(self.menu_win, "HOW TO USE", 0)
        for i, item in enumerate(self.menu_items):
            prefix = "> " if i == self.selected_index else "  "
            x = (width - 13) // 2
            self.menu_win.addstr(i + 2, x, prefix + item)

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
        return None

    def create_maze(self) -> None:
        self.maze_height = (self.scr_height  * 3) // 4 
        self.maze_width  = self.scr_width - 1
        self.maze_y = 1
        self.maze_x = 1
        self.maze_win = curses.newwin(
             self.maze_height,
            self.maze_width,
            self.maze_y,
            self.maze_x
        )
        self.maze_win.border()
        self.maze_win.nodelay(True)
        self.maze_panel = curses.panel.new_panel(self.maze_win)
        self.maze_panel.top()
        self.maze_panel.show()


    def draw_maze(self) -> None:
        # grid = self.maze.grid
        self.maze_win.addstr(0,1, "Amazing!")

    def exit_programme(self) -> None:
        import sys
        print("bye!", file=sys.stderr)
        exit(0)

    def menu(self) -> None:

        menu_options : Dict= {
            "quit": self.exit_programme(),
            "generate": None,
            "draw path": None,
        }

        option : str|None = self.handle_menu_input()
        menu_option = menu_options.get(option)
        if menu_option is None:
            return
        menu_option()



def display(stdscr : CWindow, maze : Maze) -> None:
    curses.start_color()
    displayer : Display = Display(maze, stdscr)
    while True:
        # get input
        # recalculate all logic
        # draw
        # refresh
        # continue
        displayer.menu()


        displayer.draw_maze()
        displayer.draw_menu()
        curses.panel.update_panels()
        curses.doupdate()


def main():
    maze : Maze = generate_fake_maze(25, 25)
    curses.wrapper(display, maze)


if __name__ == "__main__":
    main()
