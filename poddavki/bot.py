# poddavki/bot.py
import random
from typing import List, Set, Tuple, TYPE_CHECKING

from .board import Pos
from settings import P1, P2

if TYPE_CHECKING:
    from .game import PodGame


class PodBot:
    """
    The bot can play as either side.
    """

    def __init__(self, player: int = P2, difficulty: str = "easy"):
        self.player = player if player in (P1, P2) else P2
        self.enemy = P1 if self.player == P2 else P2
        self.difficulty = (difficulty or "easy").lower()

    def take_turn(self, game: "PodGame"):
        """
        Execute a full bot turn, including chaining captures when required.
        """
        bot_player = self.player
        if game.winner or game.current_player != bot_player:
            return

        if not game.board.has_any_move(bot_player):
            # Poddavki rules: player wins if they cannot move.
            game.winner = bot_player
            return

        capture_options: List[Tuple[Pos, Pos]] = []
        simple_options: List[Tuple[Pos, Pos]] = []
        forward_options: List[Tuple[Pos, Pos]] = []

        for r in range(len(game.board.grid)):
            for c in range(len(game.board.grid[r])):
                if game.board.get(r, c) == bot_player:
                    pos = (r, c)
                    captures = game.board._captures_from(bot_player, pos, set())
                    if captures:
                        for dst in captures:
                            capture_options.append((pos, dst))
                    else:
                        moves = game.board._simple_moves_from(bot_player, pos)
                        for dst in moves:
                            simple_options.append((pos, dst))
                            if (
                                not game.board.is_king(pos)
                                and dst[0] - r == game.board.forward_dir(bot_player)
                            ):
                                forward_options.append((pos, dst))

        if capture_options:
            src, dst = random.choice(capture_options)
            self._play_capture_chain(game, src, dst)
            return

        if simple_options:
            if self.difficulty == "hard":
                src, dst = self._choose_passive_move(game, simple_options)
            else:
                if forward_options:
                    src, dst = random.choice(forward_options)
                else:
                    src, dst = random.choice(simple_options)

            self._finish_simple_move(game, src, dst)
            return

        game.winner = bot_player

    def _finish_simple_move(self, game: "PodGame", src: Pos, dst: Pos):
        self._move_piece(game, src, dst)
        game.captured_in_chain = set()
        game.jump_mode = False
        game.selected = None
        game._end_turn()

    def _move_piece(self, game: "PodGame", src: Pos, dst: Pos):
        was_king = game.board.is_king(src)
        game.board.move_piece(src, dst)
        if not was_king and game.board.in_kings_row(self.player, dst[0]):
            game.board.make_king(dst)

    def _play_capture_chain(self, game: "PodGame", src: Pos, first_dst: Pos):
        """
        Resolve a chain of captures starting from src -> first_dst.
        """
        bot_player = self.player
        captured: Set[Pos] = set()
        cur = src
        dst = first_dst

        while True:
            was_king = game.board.is_king(cur)
            is_cap, enemy_pos = game.board.is_capture_move(bot_player, cur, dst, captured)
            if not is_cap or enemy_pos is None:
                break

            game.board.move_piece(cur, dst)
            if not was_king and game.board.in_kings_row(bot_player, dst[0]):
                game.board.make_king(dst)

            captured.add(enemy_pos)

            more = game.board.get_valid_moves_for_piece(
                bot_player,
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

    # ----- hard difficulty helpers -----
    def _choose_passive_move(
        self, game: "PodGame", options: List[Tuple[Pos, Pos]]
    ) -> Tuple[Pos, Pos]:
        best_score = None
        best_moves: List[Tuple[Pos, Pos]] = []

        for src, dst in options:
            score = self._score_simple_move(game, src, dst)
            if best_score is None or score > best_score:
                best_score = score
                best_moves = [(src, dst)]
            elif score == best_score:
                best_moves.append((src, dst))

        return random.choice(best_moves)

    def _score_simple_move(self, game: "PodGame", src: Pos, dst: Pos) -> int:
        board = game.board
        threats = self._count_enemy_capture_threats(board, dst, self.enemy)
        score = threats * 10
        if board.in_kings_row(self.player, dst[0]):
            score -= 5  # avoid promoting to king (more mobility = harder to lose)

        board_max = len(board.grid) - 1
        if self.player == P2:
            score -= dst[0]
        else:
            score -= (board_max - dst[0])
        return score

    def _count_enemy_capture_threats(self, board, dst: Pos, enemy: int) -> int:
        r, c = dst
        threats = 0

        forward = board.forward_dir(enemy)
        # enemy men capture only forward
        for dc in (-1, 1):
            attacker_row = r - forward
            attacker_col = c - dc
            landing_row = r + forward
            landing_col = c + dc
            if not board.in_bounds(attacker_row, attacker_col):
                continue
            if board.get(attacker_row, attacker_col) != enemy:
                continue
            if board.is_king((attacker_row, attacker_col)):
                continue
            if not board.in_bounds(landing_row, landing_col):
                continue
            if not board.is_empty(landing_row, landing_col):
                continue
            threats += 1

        # kings capture in all four diagonal directions
        for dr in (-1, 1):
            for dc in (-1, 1):
                attacker_row = r - dr
                attacker_col = c - dc
                landing_row = r + dr
                landing_col = c + dc
                if not board.in_bounds(attacker_row, attacker_col):
                    continue
                if board.get(attacker_row, attacker_col) != enemy:
                    continue
                if not board.is_king((attacker_row, attacker_col)):
                    continue
                if not board.in_bounds(landing_row, landing_col):
                    continue
                if not board.is_empty(landing_row, landing_col):
                    continue
                threats += 1
        return threats
