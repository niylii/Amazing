from __future__ import annotations

from pathlib import Path

from solver import SolverResult



class WriterError(OSError):
    """Raised when the output file cannot be written."""


def write_output(
    output_file: str | Path,
    hex_grid: list[list[str]],
    entry: tuple[int, int],
    exit_p: tuple[int, int],
    result: SolverResult,
) -> None:
    
    dest = Path(output_file)

    lines: list[str] = []

    # --- Hex grid ---
    for row in hex_grid:
        lines.append(" ".join(row))

    # --- Blank separator ---
    lines.append("")

    # --- Entry / exit ---
    lines.append(f"{entry[0]},{entry[1]}")
    lines.append(f"{exit_p[0]},{exit_p[1]}")

    # --- Direction string ---
    lines.append(result.directions)

    # --- Write to disk ---
    try:
        dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError as exc:
        raise WriterError(
            f"Failed to write output file '{dest}': {exc}"
        ) from exc