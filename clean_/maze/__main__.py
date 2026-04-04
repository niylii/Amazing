from __future__ import annotations

from pathlib import Path

from .generator import MazeGenerator
from .writer import MazeWriter


def main() -> None:
    mg = MazeGenerator(
        width=25,
        height=15,
        seed=None,
        perfect=False,
        entry_point=(0, 0),
        exit_point=(24, 14),
    )
    mg.generate()

    directions = mg.solve()
    print(f"Solution length: {len(directions)}")
    print(
        f"Solution directions: {directions[:80]}{'...' if len(directions) > 80 else ''}"
    )

    print("\nASCII maze (with solution path):")
    mg.afficher_ascii(show_path=mg.solution_path)

    out = Path("maze_output.txt")
    MazeWriter(mg, str(out)).write()
    print(f"\nWrote: {out.resolve()}")

    c00 = mg.grid.get_cell(0, 0)
    print(f"\nEntry cell hex: {c00.to_hex()} (Cell.to_hex sanity check)")
    print(f"Entry cell walls: {c00.walls}")


if __name__ == "__main__":
    main()
