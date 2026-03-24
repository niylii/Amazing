import curses
from ui.ui_utils import create_win_with_panel, center_text_win

class Menu:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.selected_vertical_index = 0
        self.menu_options = {}
        self.selectors_data = {}
        self.selectors_indexes = {}
        self.menu_state = "main"

    def handle_menu_input(self):
        menu_options = list(self.menu_options.keys())
        current_name, current_type = menu_options[self.selected_vertical_index]
        curses.set_escdelay(1)

        if not self.maze_is_animating and not self.path_is_animating:
            self.menu_win.nodelay(False)
            self.input_win.nodelay(False)
        else:
            self.menu_win.nodelay(True)
            self.input_win.nodelay(True)

        try:
            key = self.menu_win.getch()
        except curses.error:
            return None


        if self.input_mod:
            self.sub_input_win.leaveok(True)
            if key in (10, 13, 7):
                self.input_mod = False
                self.input_panel.hide()
                self.input_done = True
                self.handle_input_box()
            else:
                self.input_box.do_command(key)
            return None

        if key == curses.KEY_UP or key == ord('k'):
            self.selected_vertical_index = (self.selected_vertical_index - 1) % len(self.menu_options)

        if key == curses.KEY_DOWN or key == ord('j'):
            self.selected_vertical_index = (self.selected_vertical_index + 1) % len(self.menu_options)

        if current_type == "selector":
            if key in [curses.KEY_LEFT, ord('h')]:
                self.selectors_indexes[current_name] = (self.selectors_indexes[current_name] - 1) % len(self.selectors_data[current_name])
            elif key in [curses.KEY_RIGHT, ord('l')]:
                self.selectors_indexes[current_name] = (self.selectors_indexes[current_name] + 1) % len(self.selectors_data[current_name])

        else:
            if key in [curses.KEY_ENTER, ord('\n')]:
                return menu_options[self.selected_vertical_index][0]

        if key == ord(' '):
            self.togle_animation = not self.togle_animation

        if key == ord('?'):
            self.show_help()

        if key == 27:
            self.back_to_main_menu()

        return None


    def draw_menu(self):
        menu_win = self.menu_win
        menu_win.erase()
        menu_win.box()


        menu_win.addstr(0, 2, f"{self.menu_state}:", curses.A_DIM | curses.A_REVERSE)
        menu_win.addstr(self.menu_height - 1, 2, f"(?=help)", curses.A_DIM)
        for i, (item, item_type) in enumerate(self.menu_options):
            prefix = "> " if i == self.selected_vertical_index else "  "

            if item_type == "selector":
                val = self.selectors_data[item][self.selectors_indexes[item]][0]
                if val == "white" and self.theme == "light":
                    val = "black"
                text = f"{item}: < {val} >"
            else:
                text = f"{item}"

            x =  2

            menu_win.addstr(i + 2, x, prefix, curses.A_BLINK | (curses.A_REVERSE if i == self.selected_vertical_index else curses.A_NORMAL))
            menu_win.addstr(i + 2, x + 2, text, curses.A_REVERSE | curses.A_BOLD if i == self.selected_vertical_index else curses.A_NORMAL)