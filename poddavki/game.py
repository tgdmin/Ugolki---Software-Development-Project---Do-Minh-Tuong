# poddavki/game.py
from typing import Optional, Tuple, Set, List
import pygame
import settings
from .board import PodBoard, Pos
from .bot import PodBot
from settings import (
    WIDTH,
    HEIGHT,
    FPS,
    SQUARE,
    EMPTY,
    P1,
    P2,
    BOARD_IMG_PATH,
    WP_IMG_PATH,
    BP_IMG_PATH,
    ICON_PATH,
)


class PodGame:
    def __init__(self, vs_bot: bool = False, bot_difficulty: str = "easy", human_player: int = P1):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Poddavki")
        self.clock = pygame.time.Clock()

        self.vs_bot = vs_bot
        self.bot_difficulty = bot_difficulty
        self.board = PodBoard()
        self.human_player = human_player if vs_bot else None
        self.bot_player = None
        if self.vs_bot:
            self.bot_player = P2 if self.human_player == P1 else P1
            self.bot = PodBot(player=self.bot_player, difficulty=bot_difficulty)
        else:
            self.bot = None
        self.selected: Optional[Pos] = None
        self.current_player = P1
        self.winner: Optional[int] = None

        # capture-chain state
        self.jump_mode = False
        self.captured_in_chain: Set[Pos] = set()
        self.forced_capture_sources: Set[Pos] = set()

        self._load_assets()
        self.font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 28)
        self.hint_font = pygame.font.SysFont(None, 22)
        self._update_forced_capture_sources()

    # ---------- assets ----------
    def _load_assets(self):
        try:
            self.board_img = pygame.image.load(BOARD_IMG_PATH).convert_alpha()
            self.wp_img = pygame.image.load(WP_IMG_PATH).convert_alpha()
            self.bp_img = pygame.image.load(BP_IMG_PATH).convert_alpha()
            icon_img = pygame.image.load(ICON_PATH).convert_alpha()
            pygame.display.set_icon(icon_img)
        except pygame.error as e:
            raise RuntimeError(f"Failed to load Poddavki assets: {e}")

        self.board_img = pygame.transform.smoothscale(self.board_img, (WIDTH, HEIGHT))
        scale = 0.75
        piece_size = int(SQUARE * scale)
        self.offset = (SQUARE - piece_size) // 2
        self.wp_img = pygame.transform.smoothscale(self.wp_img, (piece_size, piece_size))
        self.bp_img = pygame.transform.smoothscale(self.bp_img, (piece_size, piece_size))

    # ---------- helpers ----------
    def _screen_to_grid(self, pos) -> Pos:
        x, y = pos
        return (y // SQUARE, x // SQUARE)

    def _is_human_turn(self) -> bool:
        if not self.vs_bot:
            return True
        return (self.human_player is not None) and (self.current_player == self.human_player)

    def _capture_sources_for_player(self, player: int) -> Set[Pos]:
        sources: Set[Pos] = set()
        for r in range(len(self.board.grid)):
            for c in range(len(self.board.grid[r])):
                if self.board.get(r, c) != player:
                    continue
                if self.board._captures_from(player, (r, c), set()):
                    sources.add((r, c))
        return sources

    def _update_forced_capture_sources(self):
        if self.winner:
            self.forced_capture_sources = set()
            return
        self.forced_capture_sources = self._capture_sources_for_player(self.current_player)

    def _valid_moves_for_selected(self) -> List[Pos]:
        """
        During a turn:
        - If already mid-chain, captures remain mandatory for that piece.
        - Otherwise, if ANY piece can capture, only those pieces may move and they must capture.
        - If no captures exist for the player, fall back to simple moves for the selected piece.
        """
        if not self.selected:
            return []

        if self.jump_mode:
            return self.board.get_valid_moves_for_piece(
                self.current_player,
                self.selected,
                force_captures=True,
                captured_in_chain=self.captured_in_chain,
            )

        if self.forced_capture_sources:
            if self.selected not in self.forced_capture_sources:
                return []
            return self.board.get_valid_moves_for_piece(
                self.current_player,
                self.selected,
                force_captures=True,
                captured_in_chain=set(),
            )

        piece_caps = self.board._captures_from(self.current_player, self.selected, set())
        force_caps = bool(piece_caps)
        return self.board.get_valid_moves_for_piece(
            self.current_player,
            self.selected,
            force_captures=force_caps,
            captured_in_chain=set(),
        )

    def _end_turn(self):
        # after finishing a capture chain remove all captured pieces
        for pos in self.captured_in_chain:
            self.board.remove_piece(pos)

        self.jump_mode = False
        self.captured_in_chain.clear()
        self.selected = None

        # switch players
        self.current_player = P2 if self.current_player == P1 else P1
        self._update_forced_capture_sources()

        # Poddavki: a player wins if they themselves have no legal moves left
        if not self.board.has_any_move(self.current_player):
            self.winner = self.current_player

    # ---------- input (human) ----------
    def _handle_left_click(self, pos):
        if self.winner:
            # any click after a win goes back to the menu
            return settings.RESTART_MENU

        if not self._is_human_turn():
            return None  # ignore clicks during the bot's turn

        row, col = self._screen_to_grid(pos)

        # SELECT PIECE
        if self.selected is None:
            if self.board.get(row, col) == self.current_player:
                if self.forced_capture_sources and (row, col) not in self.forced_capture_sources:
                    return None
                self.selected = (row, col)
                self.jump_mode = False
                self.captured_in_chain.clear()
            return None

        # clicking the same piece again deselects it (only when not in a chain)
        if self.selected == (row, col) and not self.jump_mode:
            self.selected = None
            self.captured_in_chain.clear()
            return None

        valid = self._valid_moves_for_selected()
        dest = (row, col)
        if dest not in valid:
            return None

        src = self.selected
        is_cap, enemy_pos = self.board.is_capture_move(
            self.current_player, src, dest, self.captured_in_chain
        )

        # move the piece
        was_king = self.board.is_king(src)
        self.board.move_piece(src, dest)
        self.selected = dest

        # crown to King if a man reaches the last row
        if not was_king and self.board.in_kings_row(self.current_player, dest[0]):
            self.board.make_king(dest)

        if is_cap and enemy_pos is not None:
            # once a piece captures it enters chain mode
            self.jump_mode = True
            self.captured_in_chain.add(enemy_pos)

            # check if further captures are available
            more = self.board.get_valid_moves_for_piece(
                self.current_player,
                self.selected,
                force_captures=True,  # while chaining, captures stay mandatory
                captured_in_chain=self.captured_in_chain,
            )
            if not more:
                self._end_turn()
        else:
            # simple move occurs only when this piece has no capture
            self._end_turn()

        return None

    def handle_mouse(self, e):
        if e.button == 1:
            return self._handle_left_click(e.pos)
        return None

    # ---------- draw ----------
    def draw(self):
        self.screen.blit(self.board_img, (0, 0))

        for r in range(len(self.board.grid)):
            for c in range(len(self.board.grid[r])):
                v = self.board.get(r, c)
                if v == P1:
                    self.screen.blit(
                        self.wp_img,
                        (c * SQUARE + self.offset, r * SQUARE + self.offset),
                    )
                elif v == P2:
                    self.screen.blit(
                        self.bp_img,
                        (c * SQUARE + self.offset, r * SQUARE + self.offset),
                    )

        # highlight valid moves
        if self.selected and not self.winner and self._is_human_turn():
            for (move_row, move_col) in self._valid_moves_for_selected():
                pygame.draw.rect(
                    self.screen,
                    (0, 255, 0),
                    (move_col * SQUARE, move_row * SQUARE, SQUARE, SQUARE),
                    5,
                )
            sel_row, sel_col = self.selected
            pygame.draw.rect(
                self.screen,
                (255, 255, 0),
                (sel_col * SQUARE, sel_row * SQUARE, SQUARE, SQUARE),
                5,
            )

            # hint shows only if the selected piece can capture or is mid-chain
            piece_caps_now = self.board._captures_from(
                self.current_player, self.selected, set()
            )
            if self.jump_mode or piece_caps_now or self.forced_capture_sources:
                hint = self.hint_font.render(
                    "Captures are mandatory when available",
                    True,
                    (255, 255, 255),
                )
                bg = hint.get_rect()
                bg.topleft = (10, 10)
                pad = 8
                pygame.draw.rect(
                    self.screen,
                    (0, 0, 0, 160),
                    (bg.x - pad, bg.y - pad, bg.w + 2 * pad, bg.h + 2 * pad),
                )
                self.screen.blit(hint, (bg.x, bg.y))

        # winner overlay
        if self.winner:
            dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 160))
            self.screen.blit(dim, (0, 0))
            msg = "Player 1 wins!" if self.winner == P1 else "Player 2 wins!"
            text = self.font.render(msg, True, (255, 255, 255))
            self.screen.blit(
                text,
                text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)),
            )

    # ---------- main loop ----------
    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return settings.QUIT_GAME
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    return settings.RESTART_MENU
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    res = self.handle_mouse(e)
                    if res == settings.RESTART_MENU:
                        return settings.RESTART_MENU

            # let the bot act automatically on its turn
            if (
                self.vs_bot
                and self.bot
                and not self.winner
                and self.bot_player is not None
                and self.current_player == self.bot_player
            ):
                self.bot.take_turn(self)

            self.draw()
            pygame.display.update()
            self.clock.tick(FPS)
