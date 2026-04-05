"""
main.py
Entry point — parses config, builds maze, launches UI.
"""

from __future__ import annotations

import curses
import sys
import signal
from typing import Any, Dict

from config.LOADER import load_config
from maze.generator import MazeGenerator
from maze.writer import MazeWriter
from display.UI import run_ui


def main() -> None:
    signal.signal(signal.SIGQUIT, signal.SIG_IGN)
    try:
        config: Dict[str, Any] = load_config(sys.argv)

        maze = MazeGenerator(
            width=config["WIDTH"],
            height=config["HEIGHT"],
            seed=config["SEED"],
            perfect=config["PERFECT"],
            entry_point=config["ENTRY"],
            exit_point=config["EXIT"],
        )
        maze.generate()
        MazeWriter(maze, config["OUTPUT_FILE"]).write()

        curses.wrapper(run_ui, maze)

    except KeyboardInterrupt:
        print("AMAZING SAID GOOD BYE")
        sys.exit(0)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
