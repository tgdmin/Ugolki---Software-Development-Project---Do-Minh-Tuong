# board.py
from typing import Tuple, Optional, Set
from settings import (
    N, EMPTY, P1, P2,
    P1_START_ROWS, P1_START_COLS,
    P2_START_ROWS, P2_START_COLS,
    PLAYER_TARGETS, ENFORCE_CAMP_RULE
)
from base_board import BaseBoard, Pos

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right


class Board(BaseBoard):
    # board + rules for Ugolki
    def __init__(self):
        super().__init__()

        self._camp_cache = {
            player: {(row, col) for row in rows for col in cols}
            for player, (rows, cols) in PLAYER_TARGETS.items()
        }

        # P1 bottom-left
        for row in P1_START_ROWS:
            for col in P1_START_COLS:
                self.grid[row][col] = P1

        # P2 top-right
        for row in P2_START_ROWS:
            for col in P2_START_COLS:
                self.grid[row][col] = P2

    # camps
    def _camp_cells(self, player) -> Set[Pos]:
        return self._camp_cache[player]

    def in_target_camp(self, player, row, col):
        return (row, col) in self._camp_cells(player)

    # 1-step moves
    def _step_moves(self, pos: Pos):
        row, col = pos
        out = []
        for row_delta, col_delta in DIRS:
            next_row = row + row_delta
            next_col = col + col_delta
            if self.in_bounds(next_row, next_col) and self.is_empty(next_row, next_col):
                out.append((next_row, next_col))
        return out

    # multi-jump with live pruning
    def _jump_landings(
        self,
        start: Pos,
        player: int,
        forbid: Optional[Set[Pos]],
        camp_cells: Optional[Set[Pos]],
    ) -> Set[Pos]:
        """
        collect all landings reachable by chaining jumps.
        - forbid: cells we can't land on (visited in current chain)
        - camp rule (ENFORCE_CAMP_RULE):
            if during the chain we ever enter camp_cells, all *next* landings must stay in camp
        """
        result: Set[Pos] = set()
        seen_land: Set[Pos] = set()  # avoid infinite loops on landings

        def ok_land(cell: Pos, must_stay: bool) -> bool:
            if forbid and cell in forbid:
                return False
            if camp_cells is not None and must_stay and cell not in camp_cells:
                return False
            return True

        def dfs(cur: Pos, must_stay: bool):
            # must_stay == True means we're already inside camp somewhere in this path,
            # so from now on landings must be in camp.
            if cur in seen_land:
                return
            seen_land.add(cur)

            row, col = cur
            for row_delta, col_delta in DIRS:
                mid_row = row + row_delta
                mid_col = col + col_delta      # middle (must have a piece)
                landing_row = row + 2 * row_delta
                landing_col = col + 2 * col_delta  # landing (must be empty)
                if not self.in_bounds(landing_row, landing_col):
                    continue
                if self.is_empty(mid_row, mid_col):
                    continue
                if not self.is_empty(landing_row, landing_col):
                    continue

                landing = (landing_row, landing_col)

                # if we land into camp, then next moves must stay inside
                next_must_stay = must_stay
                if ENFORCE_CAMP_RULE and camp_cells is not None:
                    if (landing in camp_cells) or (cur in camp_cells):
                        next_must_stay = True

                # landing validation (forbid set + camp stay if needed)
                if not ok_land(landing, next_must_stay):
                    continue

                if landing not in result:
                    result.add(landing)
                    dfs(landing, next_must_stay)

        # start: we haven't "entered camp" yet unless start is already in camp
        camp_cells = self._camp_cells(player) if ENFORCE_CAMP_RULE else None
        start_must_stay = ENFORCE_CAMP_RULE and (camp_cells is not None) and (start in camp_cells)
        dfs(start, start_must_stay)
        return result

    # public
    def get_valid_moves(
        self,
        player,
        pos: Optional[Pos],
        force_jumps: bool = False,
        forbid_dests: Optional[Set[Pos]] = None,
    ):
        if not pos:
            return []

        row, col = pos
        # if piece is in camp at THIS moment, it can't move out (also for steps)
        restrict_now = ENFORCE_CAMP_RULE and self.in_target_camp(player, row, col)
        camp_cells = self._camp_cells(player) if restrict_now else None

        # compute jumps fresh on current board, with live camp-stay handling
        jumps = list(self._jump_landings(pos, player, forbid=forbid_dests, camp_cells=camp_cells))

        if force_jumps:
            return jumps

        steps = self._step_moves(pos)
        if restrict_now and camp_cells is not None:
            steps = [p for p in steps if p in camp_cells]
        if forbid_dests:
            steps = [p for p in steps if p not in forbid_dests]

        return steps + jumps

    def is_target_camp_filled(self, player):
        rows, cols = PLAYER_TARGETS[player]
        return all(self.get(r, c) == player for r in rows for c in cols)
