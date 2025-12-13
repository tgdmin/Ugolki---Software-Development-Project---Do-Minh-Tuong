# pod_bot.py
import random
from typing import List, Set, Tuple, TYPE_CHECKING

from pod_board import Pos
from settings import P2

if TYPE_CHECKING:
    from pod_game import PodGame


class PodBot:
    """
    Encapsulates Poddavki bot logic so PodGame can stay focused on UI/input.
    The bot always plays as player 2.
    """

    def take_turn(self, game: "PodGame"):
        """
        Execute a full bot turn, including chaining captures when required.
        """
        if game.winner or game.current_player != P2:
            return

        if not game.board.has_any_move(P2):
            # Poddavki rules: player wins if they cannot move.
            game.winner = P2
            return

        capture_options: List[Tuple[Pos, Pos]] = []
        simple_options: List[Tuple[Pos, Pos]] = []
        forward_options: List[Tuple[Pos, Pos]] = []

        for r in range(len(game.board.grid)):
            for c in range(len(game.board.grid[r])):
                if game.board.get(r, c) == P2:
                    pos = (r, c)
                    captures = game.board._captures_from(P2, pos, set())
                    if captures:
                        for dst in captures:
                            capture_options.append((pos, dst))
                    else:
                        moves = game.board._simple_moves_from(P2, pos)
                        for dst in moves:
                            simple_options.append((pos, dst))
                            if dst[0] > r:
                                forward_options.append((pos, dst))

        if capture_options:
            src, dst = random.choice(capture_options)
            self._play_capture_chain(game, src, dst)
            return

        if simple_options:
            if forward_options:
                src, dst = random.choice(forward_options)
            else:
                src, dst = random.choice(simple_options)

            self._move_piece(game, src, dst)
            game.captured_in_chain = set()
            game.jump_mode = False
            game.selected = None
            game._end_turn()
            return

        game.winner = P2

    def _move_piece(self, game: "PodGame", src: Pos, dst: Pos):
        was_king = game.board.is_king(src)
        game.board.move_piece(src, dst)
        if not was_king and game.board.in_kings_row(P2, dst[0]):
            game.board.make_king(dst)

    def _play_capture_chain(self, game: "PodGame", src: Pos, first_dst: Pos):
        """
        Resolve a chain of captures starting from src -> first_dst.
        """
        captured: Set[Pos] = set()
        cur = src
        dst = first_dst

        while True:
            was_king = game.board.is_king(cur)
            is_cap, enemy_pos = game.board.is_capture_move(P2, cur, dst, captured)
            if not is_cap or enemy_pos is None:
                break

            game.board.move_piece(cur, dst)
            if not was_king and game.board.in_kings_row(P2, dst[0]):
                game.board.make_king(dst)

            captured.add(enemy_pos)

            more = game.board.get_valid_moves_for_piece(
                P2,
                dst,
                force_captures=True,
                captured_in_chain=captured,
            )
            if not more:
                break

            cur = dst
            dst = random.choice(more)

        game.captured_in_chain = captured
        game.jump_mode = False
        game.selected = None
        game._end_turn()
