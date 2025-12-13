from typing import List, Tuple
from settings import N, EMPTY

Pos = Tuple[int, int]

class BaseBoard:
    def __init__(self):
        # 8×8 grid shared 
        self.grid: List[List[int]] = [[EMPTY for _ in range(N)] for _ in range(N)]

    # helpers for board manipulation
    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < N and 0 <= c < N

    def get(self, r: int, c: int) -> int:
        return self.grid[r][c]

    def set(self, r: int, c: int, v: int) -> None:
        self.grid[r][c] = v

    def is_empty(self, r: int, c: int) -> bool:
        return self.grid[r][c] == EMPTY
