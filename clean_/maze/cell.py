from typing import Dict, List


# Represents one square in the maze grid
class Cell:
    def __init__(self, x: int, y: int) -> None:

        self.x: int = x
        self.y: int = y
        self.walls: Dict[str, bool] = {
            "N": False,
            "E": False,
            "S": False,
            "W": False,
        }
        self.visited: bool = False

    def to_hex(self) -> str:

        HEX: str = "0123456789ABCDEF"
        BIT_INDEX: Dict[str, int] = {"N": 0, "E": 1, "S": 2, "W": 3}
        bits: List[str] = ["1", "1", "1", "1"]

        for direction, index in BIT_INDEX.items():
            if self.walls[direction]:  # open wall -> bit 0
                bits[index] = "0"

        return HEX[int("".join(reversed(bits)), 2)]
