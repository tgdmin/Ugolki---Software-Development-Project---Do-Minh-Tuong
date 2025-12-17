# pod_board.py
from typing import Set, List
from base_board import BaseBoard, Pos
from settings import N, EMPTY, P1, P2


def is_dark(r: int, c: int) -> bool:
    """Dark squares (only these are playable)."""
    return (r + c) % 2 == 1


class PodBoard(BaseBoard):
    """
    Poddavki / giveaway checkers board:
    - Men move one square diagonally forward.
    - Men capture two squares diagonally forward (no backward capture).
    - Kings move one square diagonally in any direction.
    - Kings capture like men but in all four diagonal directions (still two-square jumps).
    """

    def __init__(self):
        super().__init__()

        # Fill the top and bottom three rows, only on dark squares
        for r in range(3):  # top 3 rows: P2
            for c in range(N):
                if is_dark(r, c):
                    self.grid[r][c] = P2

        for r in range(N - 3, N):  # bottom 3 rows: P1
            for c in range(N):
                if is_dark(r, c):
                    self.grid[r][c] = P1

        # Kings are tracked via a set of positions
        self.kings: Set[Pos] = set()

    # -------- basic helpers --------
    def own(self, player: int, r: int, c: int) -> bool:
        return self.in_bounds(r, c) and self.get(r, c) == player

    def enemy(self, player: int, r: int, c: int) -> bool:
        if not self.in_bounds(r, c):
            return False
        v = self.get(r, c)
        return v != EMPTY and v != player

    def is_king(self, pos: Pos) -> bool:
        return pos in self.kings

    def make_king(self, pos: Pos):
        self.kings.add(pos)

    def remove_piece(self, pos: Pos):
        r, c = pos
        self.grid[r][c] = EMPTY
        if pos in self.kings:
            self.kings.remove(pos)

    def move_piece(self, src: Pos, dst: Pos):
        src_row, src_col = src
        dst_row, dst_col = dst
        value = self.get(src_row, src_col)
        self.set(dst_row, dst_col, value)
        self.set(src_row, src_col, EMPTY)
        if src in self.kings:
            self.kings.remove(src)
            self.kings.add(dst)

    def forward_dir(self, player: int) -> int:
        # P1 starts at bottom moving up (-1), P2 starts at top moving down (+1)
        return -1 if player == P1 else 1

    def in_kings_row(self, player: int, r: int) -> bool:
        return (player == P1 and r == 0) or (player == P2 and r == N - 1)

    # -------- simple moves (non-captures) --------
    def _simple_moves_from(self, player: int, pos: Pos) -> List[Pos]:
        """
        Men: move one square diagonally forward (never backward).
        Kings: move one square diagonally in any direction (no flying moves).
        """
        row, col = pos
        if not self.own(player, row, col):
            return []
        moves: List[Pos] = []

        if self.is_king(pos):
            # King: one diagonal step, four directions
            for row_delta in (-1, 1):
                for col_delta in (-1, 1):
                    next_row = row + row_delta
                    next_col = col + col_delta
                    if self.in_bounds(next_row, next_col) and self.is_empty(next_row, next_col):
                        moves.append((next_row, next_col))
        else:
            # Man: one forward diagonal step only
            forward_step = self.forward_dir(player)
            for col_delta in (-1, 1):
                next_row = row + forward_step
                next_col = col + col_delta
                if self.in_bounds(next_row, next_col) and self.is_empty(next_row, next_col):
                    moves.append((next_row, next_col))

        return moves

    # -------- captures from a single piece --------
    def _captures_from(self, player: int, pos: Pos, captured_in_chain: Set[Pos]) -> List[Pos]:
        """
        Return landing squares for every capture originating from pos,
        respecting the set of already-captured pieces in the chain.
        """
        if not self.own(player, pos[0], pos[1]):
            return []
        if self.is_king(pos):
            return self._king_captures(player, pos, captured_in_chain)
        else:
            return self._man_captures(player, pos, captured_in_chain)

    def _man_captures(self, player: int, pos: Pos, captured_in_chain: Set[Pos]) -> List[Pos]:
        """
        Men capture only forward:
        - Jump two squares diagonally forward over one enemy and land on the empty cell beyond.
        """
        row, col = pos
        res: List[Pos] = []
        forward_step = self.forward_dir(player)  # forward direction only (no backward capture)

        for col_delta in (-1, 1):
            mid_row = row + forward_step
            mid_col = col + col_delta
            landing_row = row + 2 * forward_step
            landing_col = col + 2 * col_delta
            if not self.in_bounds(landing_row, landing_col):
                continue
            if not self.enemy(player, mid_row, mid_col):
                continue
            if (mid_row, mid_col) in captured_in_chain:
                continue
            if not self.is_empty(landing_row, landing_col):
                continue
            res.append((landing_row, landing_col))

        return res

    def _king_captures(self, player: int, pos: Pos, captured_in_chain: Set[Pos]) -> List[Pos]:
        """
        Kings capture like men but in all four directions:
        - Jump exactly two diagonal squares (no flying),
        - Must hop over exactly one enemy piece that has not been captured yet.
        """
        row, col = pos
        res: List[Pos] = []

        for row_delta in (-1, 1):
            for col_delta in (-1, 1):
                mid_row = row + row_delta
                mid_col = col + col_delta
                landing_row = row + 2 * row_delta
                landing_col = col + 2 * col_delta

                if not self.in_bounds(landing_row, landing_col):
                    continue
                if not self.enemy(player, mid_row, mid_col):
                    continue
                if (mid_row, mid_col) in captured_in_chain:
                    continue
                if not self.is_empty(landing_row, landing_col):
                    continue

                res.append((landing_row, landing_col))

        return res

    # -------- general helpers --------
    def has_any_capture(self, player: int) -> bool:
        """Check whether any capture remains (used for win conditions)."""
        for row in range(N):
            for col in range(N):
                if self.own(player, row, col):
                    if self._captures_from(player, (row, col), set()):
                        return True
        return False

    def has_any_move(self, player: int) -> bool:
        """
        Determine whether the player still has any legal move (capture or simple).
        Used for the Poddavki win condition: whoever cannot move wins.
        """
        if self.has_any_capture(player):
            return True
        for row in range(N):
            for col in range(N):
                if self.own(player, row, col):
                    if self._simple_moves_from(player, (row, col)):
                        return True
        return False

    def get_valid_moves_for_piece(
        self,
        player: int,
        pos: Pos,
        force_captures: bool,
        captured_in_chain: Set[Pos],
    ) -> List[Pos]:
        """
        Return legal destination squares for the piece at pos.

        - force_captures = True  => only captures are returned.
        - force_captures = False => captures are returned if available,
          otherwise simple moves are returned.
        """
        if not self.own(player, pos[0], pos[1]):
            return []

        caps = self._captures_from(player, pos, captured_in_chain)
        if force_captures:
            return caps
        else:
            if caps:
                return caps
            return self._simple_moves_from(player, pos)

    def is_capture_move(self, player: int, src: Pos, dst: Pos, captured_in_chain: Set[Pos]):
        """
        Check whether the move src->dst is a valid capture,
        returning the enemy position if it is.
        (Applies to both men and kings since both jump exactly 2 squares.)
        """
        src_row, src_col = src
        dst_row, dst_col = dst

        # Captures must be exactly two diagonal squares
        if abs(src_row - dst_row) != 2 or abs(src_col - dst_col) != 2:
            return False, None

        mid_row = (src_row + dst_row) // 2
        mid_col = (src_col + dst_col) // 2

        if not self.enemy(player, mid_row, mid_col):
            return False, None
        if (mid_row, mid_col) in captured_in_chain:
            return False, None

        return True, (mid_row, mid_col)
