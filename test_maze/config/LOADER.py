"""
config/loader.py
Configuration file parsing and validation.

Moved from the old validate() function in main.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict


# ── Custom exceptions (keep them here so imports stay clean) ─────────────────

class InvalidArgumentError(ValueError):
    pass

class InvalidFileError(ValueError):
    pass

class InvalidEntryError(ValueError):
    pass


# ── Public API ───────────────────────────────────────────────────────────────

def load_config(argv: list[str]) -> Dict[str, Any]:
    """
    Parse sys.argv, validate the config file, and return a config dict.

    Raises
    ------
    InvalidArgumentError  – wrong number of CLI arguments
    InvalidFileError      – file has wrong extension or cannot be read
    InvalidEntryError     – file content is invalid
    """
    if len(argv) != 2:
        raise InvalidArgumentError("Usage: python3 main.py config.txt")

    filename: str = argv[1]
    _, ext = os.path.splitext(filename)

    if ext != ".txt":
        raise InvalidFileError(
            "Configuration file must be plain text (e.g. config.txt)."
        )

    return validate(filename)


def validate(filename: str) -> Dict[str, Any]:
    """
    Read *filename* and return a validated config dict with keys:
        WIDTH, HEIGHT, SEED, PERFECT, ENTRY, EXIT, OUTPUT_FILE
    """
    try:
        with open(filename) as fh:
            lines = fh.readlines()
    except OSError as exc:
        raise InvalidFileError(f"Cannot read '{filename}': {exc}") from exc

    config: Dict[str, Any] = {}

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            raise InvalidEntryError(f"Malformed line (missing '='): {line!r}")

        key, _, value = line.partition("=")
        key   = key.strip().upper()
        value = value.strip()

        if key == "WIDTH":
            config["WIDTH"] = _parse_positive_int(key, value)
        elif key == "HEIGHT":
            config["HEIGHT"] = _parse_positive_int(key, value)
        elif key == "SEED":
            config["SEED"] = None if value.lower() == "random" else _parse_int(key, value)
        elif key == "PERFECT":
            config["PERFECT"] = _parse_bool(key, value)
        elif key == "ENTRY":
            config["ENTRY"] = _parse_coord(key, value)
        elif key == "EXIT":
            config["EXIT"] = _parse_coord(key, value)
        elif key == "OUTPUT_FILE":
            config["OUTPUT_FILE"] = value
        else:
            raise InvalidEntryError(f"Unknown key: {key!r}")

    _require_keys(config, ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE"])

    config.setdefault("SEED",    None)
    config.setdefault("PERFECT", True)

    return config


# ── Helpers ──────────────────────────────────────────────────────────────────

def _parse_positive_int(key: str, value: str) -> int:
    try:
        n = int(value)
    except ValueError:
        raise InvalidEntryError(f"{key} must be an integer, got {value!r}")
    if n <= 0:
        raise InvalidEntryError(f"{key} must be positive, got {n}")
    return n


def _parse_int(key: str, value: str) -> int:
    try:
        return int(value)
    except ValueError:
        raise InvalidEntryError(f"{key} must be an integer, got {value!r}")


def _parse_bool(key: str, value: str) -> bool:
    v = value.lower()
    if v in ("true", "yes", "1", "on"):
        return True
    if v in ("false", "no", "0", "off"):
        return False
    raise InvalidEntryError(f"{key} must be a boolean (true/false), got {value!r}")


def _parse_coord(key: str, value: str) -> tuple[int, int]:
    try:
        parts = value.split(",")
        if len(parts) != 2:
            raise ValueError
        return (int(parts[0].strip()), int(parts[1].strip()))
    except ValueError:
        raise InvalidEntryError(
            f"{key} must be a coordinate like '3,4', got {value!r}"
        )


def _require_keys(config: dict, keys: list[str]) -> None:
    for k in keys:
        if k not in config:
            raise InvalidEntryError(f"Required key missing: {k}")
