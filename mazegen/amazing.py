from __future__ import annotations

import argparse
import sys

from config_parser import ConfigError, MazeConfig, parse_config
from generator import MazeGenerator
from solver import SolverError, solve
from writer import WriterError, write_output


def _build_parser() -> argparse.ArgumentParser:
   
    parser = argparse.ArgumentParser(
        prog="a_maze_ing",
        description="Generate a maze, solve it, and write the result to a file.",
    )
    parser.add_argument(
        "config_file",
        metavar="CONFIG_FILE",
        help="Path to the KEY=VALUE configuration file.",
    )
    parser.add_argument(
        "--show-ascii",
        action="store_true",
        default=False,
        help="Print the ASCII maze (with solution path) to stdout.",
    )
    return parser


def _run(config: MazeConfig, show_ascii: bool) -> None:
   
    print(
        f"[*] Generating {'perfect' if config.perfect else 'imperfect'} maze "
        f"({config.width}x{config.height}, seed={config.seed}) …"
    )
    mg = MazeGenerator(
        width=config.width,
        height=config.height,
        seed=config.seed,
        entry=config.entry,
        exit_p=config.exit_p,
        perfect=config.perfect,
    )
    mg.generate()

    print("[*] Solving maze …")
    result = solve(mg.maze, config.entry, config.exit_p)
    print(f"[+] Solution found: {len(result.path)} cells, {len(result.directions)} steps.")

    hex_grid = mg.to_hex_grid()
    write_output(
        output_file=config.output_file,
        hex_grid=hex_grid,
        entry=config.entry,
        exit_p=config.exit_p,
        result=result,
    )
    print(f"[+] Output written to '{config.output_file}'.")

    if show_ascii:
        print()
        mg.afficher_ascii(show_path=result.path)

def main() -> None:
   
    parser = _build_parser()
    args = parser.parse_args()

    try:
        config = parse_config(args.config_file)
    except FileNotFoundError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)
    except ConfigError as exc:
        print(f"[ERROR] Configuration error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        _run(config, show_ascii=args.show_ascii)
    except SolverError as exc:
        print(f"[ERROR] Solver error: {exc}", file=sys.stderr)
        sys.exit(1)
    except WriterError as exc:
        print(f"[ERROR] Writer error: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"[ERROR] Maze generation error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:  
        print(f"[ERROR] Unexpected error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()