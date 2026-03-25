"""config_parser.py – Parse and validate the A-Maze-ing configuration file.

Config format (KEY=VALUE, comments start with ``#``):

    # example config
    WIDTH=20
    HEIGHT=15
    ENTRY=0,0
    EXIT=19,14
    OUTPUT_FILE=maze_output.txt
    PERFECT=True
    SEED=42          # optional
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from pathlib import Path



@dataclass
class MazeConfig:
    

    width: int
    height: int
    entry: tuple[int, int]
    exit_p: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int = field(default_factory=lambda: random.randint(0, 2**31 - 1))



class ConfigError(ValueError):
    """Raised for any configuration parsing or validation error."""



_REQUIRED_KEYS: frozenset[str] = frozenset(
    {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}
)


def _parse_int(value: str, key: str) -> int:
    
    try:
        result = int(value)
    except ValueError:
        raise ConfigError(
            f"'{key}' must be an integer, got: '{value}'"
        ) from None
    if result < 2:
        raise ConfigError(
            f"'{key}' must be >= 2, got: {result}"
        )
    return result


def _parse_coord(value: str, key: str) -> tuple[int, int]:

    parts = value.split(",")
    if len(parts) != 2:
        raise ConfigError(
            f"'{key}' must be in 'x,y' format, got: '{value}'"
        )
    try:
        x, y = int(parts[0].strip()), int(parts[1].strip())
    except ValueError:
        raise ConfigError(
            f"'{key}' coordinates must be integers, got: '{value}'"
        ) from None
    if x < 0 or y < 0:
        raise ConfigError(
            f"'{key}' coordinates must be non-negative, got: ({x}, {y})"
        )
    return (x, y)


def _parse_bool(value: str, key: str) -> bool:
   
    normalised = value.strip().lower()
    if normalised == "true":
        return True
    if normalised == "false":
        return False
    raise ConfigError(
        f"'{key}' must be 'True' or 'False', got: '{value}'"
    )


def _parse_seed(value: str, key: str = "SEED") -> int:
   
    try:
        seed = int(value)
    except ValueError:
        raise ConfigError(
            f"'{key}' must be an integer, got: '{value}'"
        ) from None
    if seed < 0:
        raise ConfigError(f"'{key}' must be >= 0, got: {seed}")
    return seed


def _validate_bounds(
    coord: tuple[int, int],
    width: int,
    height: int,
    name: str,
) -> None:
    
    x, y = coord
    if not (0 <= x < width and 0 <= y < height):
        raise ConfigError(
            f"'{name}' ({x}, {y}) is out of bounds "
            f"for a {width}x{height} maze."
        )


def parse_config(path: str | Path) -> MazeConfig:
    
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: '{config_path}'")
    if not config_path.is_file():
        raise ConfigError(f"'{config_path}' is not a regular file.")

    raw: dict[str, str] = {}

    with config_path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            if "=" not in line:
                raise ConfigError(
                    f"Line {lineno}: expected 'KEY=VALUE', got: '{line}'"
                )
            key, _, value = line.partition("=")
            key = key.strip().upper()
            value = value.strip()
            if not key:
                raise ConfigError(f"Line {lineno}: empty key.")
            raw[key] = value

    missing = _REQUIRED_KEYS - raw.keys()
    if missing:
        raise ConfigError(
            f"Missing required config key(s): {', '.join(sorted(missing))}"
        )

    width = _parse_int(raw["WIDTH"], "WIDTH")
    height = _parse_int(raw["HEIGHT"], "HEIGHT")
    entry = _parse_coord(raw["ENTRY"], "ENTRY")
    exit_p = _parse_coord(raw["EXIT"], "EXIT")
    output_file = raw["OUTPUT_FILE"]
    perfect = _parse_bool(raw["PERFECT"], "PERFECT")

    if not output_file:
        raise ConfigError("'OUTPUT_FILE' must not be empty.")

    _validate_bounds(entry, width, height, "ENTRY")
    _validate_bounds(exit_p, width, height, "EXIT")

    if entry == exit_p:
        raise ConfigError("'ENTRY' and 'EXIT' must be different cells.")

    if "SEED" in raw:
        seed = _parse_seed(raw["SEED"])
        return MazeConfig(
            width=width,
            height=height,
            entry=entry,
            exit_p=exit_p,
            output_file=output_file,
            perfect=perfect,
            seed=seed,
        )

    return MazeConfig(
        width=width,
        height=height,
        entry=entry,
        exit_p=exit_p,
        output_file=output_file,
        perfect=perfect,
    )