import curses
import time

def main(stdscr : curses.window):
    stdscr = curses.initscr()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE) 
    curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_CYAN) 
    curses.curs_set(0)       # hide cursor
    stdscr.nodelay(True)     # optional: non-blocking input
    stdscr.clear()
    maze = [
    [0,1,0,0,1,0,1,1,0,0,1,0,1,1,0,0],
    [0,1,0,1,1,0,0,1,0,1,1,0,0,1,1,0],
    [0,0,0,1,0,0,1,0,0,1,0,1,0,0,1,0],
    [1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0],
    [5,1,0,0,0,1,1,0,0,0,1,1,0,0,0,1],
    [0,1,1,0,0,1,0,0,1,0,0,1,0,1,0,0],
    [0,0,1,0,1,0,1,1,0,1,0,0,1,0,1,0],
    [1,0,0,1,0,0,0,1,0,0,1,0,0,1,0,0],
    [0,1,0,0,1,1,0,0,1,0,1,1,0,0,1,0],
    [0,1,1,0,0,1,0,1,0,0,1,0,1,0,0,1],
    [0,0,1,0,1,0,1,0,1,0,0,1,0,1,0,0],
    [1,0,0,1,0,1,0,1,0,1,0,0,1,0,1,0],
    [0,1,0,0,1,0,1,0,0,1,1,0,0,1,0,1],
    [0,1,1,0,0,1,0,1,0,0,1,0,1,0,1,0],
    [0,0,0,1,0,0,1,0,1,0,0,1,0,1,0,0],
    [1,1,0,0,1,1,0,0,1,1,0,0,1,0,0,9]]

    height, width = stdscr.getmaxyx()
 #   if (height < 5 or width > 9):

    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            char = "  🗡  " if cell == 9 else "♟" if cell == 5 else "X" if cell else " "
            stdscr.addstr(y, x*4, char*4, curses.color_pair(1))
    stdscr.refresh()
# this is very cutiee when u want to find the path u jst hit one of theeese .
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell in ("💀", "🗡"):
                continue
            char = "🎀" if cell else " "
            stdscr.addstr(y, x*4, char*4, curses.color_pair(2))
            stdscr.refresh()
            # time.sleep(0.05)  # pause to visualize
            key = stdscr.getch()
            if key == ord('q'):
                exit(1)
            
if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception:
        print("terminal toooo small")
