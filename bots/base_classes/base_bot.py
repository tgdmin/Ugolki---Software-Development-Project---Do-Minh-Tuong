from __future__ import annotations
from typing import List, Tuple, Optional

# Move representation is (piece, (row, col)).
Move = Tuple["ArenaPiece", Tuple[int, int]]  # type: ignore[name-defined]


class BaseBot:
    """Minimal base class to satisfy friend bot expectations."""

    def __init__(self):
        self._forced_piece: Optional[Tuple[int, int]] = None

    # The stadium sets a forced piece when a capture chain is underway.
    def set_forced_piece_constraint(self, coords: Optional[Tuple[int, int]]):
        self._forced_piece = coords

    def clear_forced_piece_constraint(self):
        self._forced_piece = None

    def get_all_possible_moves(self, board, piece_type) -> List[Move]:
        moves: List[Move] = []
        for piece in board.get_all_pieces(piece_type):
            if self._forced_piece and (piece.row, piece.col) != self._forced_piece:
                continue
            for dest in piece.get_legals_moves(board.board):
                moves.append((piece, dest))
        return moves
