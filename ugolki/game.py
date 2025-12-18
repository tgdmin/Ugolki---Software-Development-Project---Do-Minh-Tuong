# game.py
from typing import Optional, Tuple, Set, List
import random
import pygame
from .board import Board
import settings
from settings import (
    WIDTH, HEIGHT, FPS, SQUARE, EMPTY, P1, P2,
    BOARD_IMG_PATH, WP_IMG_PATH, BP_IMG_PATH,
    WINDOW_TITLE, ICON_PATH
)

Pos = Tuple[int, int]

class Game:
    # supports Vs Bot or Vs Player 2
    def __init__(self, vs_bot: bool = True, human_player: int = P1):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()

        self.vs_bot = vs_bot  # True => P2 is bot
        self.human_player = human_player if vs_bot else None
        self.bot_player = None
        if self.vs_bot:
            self.bot_player = P2 if human_player == P1 else P1
        self.board = Board()
        self.selected: Optional[Pos] = None
        self.current_player = P1
        self.winner: Optional[int] = None

        # jump chain state (for human)
        self.jump_mode = False
        self.visited_in_chain: Set[Pos] = set()

        # win overlay buttons
        bw, bh = 180, 50
        gap = 20
        cx = WIDTH // 2 - bw - gap // 2
        cy = HEIGHT // 2 + 50
        self.btn_replay = pygame.Rect(cx, cy, bw, bh)
        self.btn_menu   = pygame.Rect(cx + bw + gap, cy, bw, bh)

        self._load_assets()
        self.font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 28)
        self.hint_font = pygame.font.SysFont(None, 22)

    def _load_assets(self):
        try:
            self.board_img = pygame.image.load(BOARD_IMG_PATH).convert_alpha()
            self.wp_img = pygame.image.load(WP_IMG_PATH).convert_alpha()
            self.bp_img = pygame.image.load(BP_IMG_PATH).convert_alpha()
            icon_img = pygame.image.load(ICON_PATH).convert_alpha()
            pygame.display.set_icon(icon_img)
        except pygame.error as e:
            raise RuntimeError(f"Failed to load game assets: {e}")

        self.board_img = pygame.transform.smoothscale(self.board_img, (WIDTH, HEIGHT))
        scale = 0.75
        piece_size = int(SQUARE * scale)
        self.offset = (SQUARE - piece_size) // 2
        self.wp_img = pygame.transform.smoothscale(self.wp_img, (piece_size, piece_size))
        self.bp_img = pygame.transform.smoothscale(self.bp_img, (piece_size, piece_size))

    def _reset_game(self):
        self.board = Board()
        self.selected = None
        self.current_player = P1
        self.winner = None
        self.jump_mode = False
        self.visited_in_chain.clear()

    def _is_human_turn(self) -> bool:
        if not self.vs_bot:
            return True
        return (self.human_player is not None) and (self.current_player == self.human_player)


    # helpers
    def _screen_to_grid(self, pos) -> Pos:
        x, y = pos
        return (y // SQUARE, x // SQUARE)

    def _valid_moves_for_selected(self):
        if not self.selected:
            return []
        forbid = self.visited_in_chain if (self.jump_mode and self.visited_in_chain) else None
        return self.board.get_valid_moves(
            self.current_player,
            self.selected,
            force_jumps=self.jump_mode,
            forbid_dests=forbid
        )

    def _end_turn(self):
        self.jump_mode = False
        self.visited_in_chain.clear()
        self.selected = None

        if self.board.is_target_camp_filled(self.current_player):
            self.winner = self.current_player
            return

        self.current_player = P2 if self.current_player == P1 else P1

    # BOT (P2)
    def _bot_take_turn(self):
        if self.winner or not self.vs_bot or self.bot_player is None or self.current_player != self.bot_player:
            return

        bot = self.bot_player
        # collect P2 pieces 
        pieces: List[Pos] = [
            (row, col)
            for row in range(len(self.board.grid))
            for col in range(len(self.board.grid[row]))
            if self.board.get(row, col) == bot
        ]
        random.shuffle(pieces)

        # try jump first (take the first chain we can)
        for pos in pieces:
            all_moves = self.board.get_valid_moves(bot, pos, force_jumps=False)
            jump_moves = [m for m in all_moves if abs(m[0] - pos[0]) + abs(m[1] - pos[1]) == 2]
            if jump_moves:
                self._bot_play_jump_chain(pos, jump_moves[0])
                return

        # else do first step we see
        for pos in pieces:
            all_moves = self.board.get_valid_moves(bot, pos, force_jumps=False)
            step_moves = [m for m in all_moves if abs(m[0] - pos[0]) + abs(m[1] - pos[1]) == 1]
            if step_moves:
                self._bot_move_piece(pos, step_moves[0])
                self._finish_bot_turn()
                return

    def _bot_move_piece(self, src: Pos, dst: Pos):
        src_row, src_col = src
        dst_row, dst_col = dst
        self.board.set(dst_row, dst_col, self.board.get(src_row, src_col))
        self.board.set(src_row, src_col, EMPTY)

    def _bot_play_jump_chain(self, start: Pos, first_dst: Pos):
        bot = self.bot_player
        if bot is None:
            return
        self._bot_move_piece(start, first_dst)
        visited = {start, first_dst}
        cur = first_dst

        # keep chaining jumps; always pick the first available
        while True:
            more = self.board.get_valid_moves(bot, cur, force_jumps=True, forbid_dests=visited)
            more = [m for m in more if abs(m[0] - cur[0]) + abs(m[1] - cur[1]) == 2]
            if not more:
                break
            nxt = more[0]
            self._bot_move_piece(cur, nxt)
            visited.add(cur)
            visited.add(nxt)
            cur = nxt

        self._finish_bot_turn()

    def _finish_bot_turn(self):
        bot = self.bot_player
        if bot is None:
            return
        if self.board.is_target_camp_filled(bot):
            self.winner = bot
            return
        if self.human_player is not None:
            self.current_player = self.human_player
        else:
            self.current_player = P1 if bot == P2 else P2
    

    # input (human)
    def _handle_left_click(self, pos):
        if self.winner:
            mx, my = pos
            if self.btn_replay.collidepoint(mx, my):
                self._reset_game()
            elif self.btn_menu.collidepoint(mx, my):
                return settings.RESTART_MENU
            return None

        # ignore clicks on bot's turn
        if not self._is_human_turn():
            return None

        row, col = self._screen_to_grid(pos)

        if self.selected is None and self.board.get(row, col) == self.current_player:
            self.selected = (row, col)
            self.jump_mode = False
            self.visited_in_chain = {self.selected}
            return None

        if self.selected == (row, col) and not self.jump_mode:
            self.selected = None
            self.visited_in_chain.clear()
            return None

        if self.selected:
            valid = self._valid_moves_for_selected()
            if (row, col) not in valid:
                return None

            sel_row, sel_col = self.selected
            self.board.set(row, col, self.board.get(sel_row, sel_col))
            self.board.set(sel_row, sel_col, EMPTY)
            self.selected = (row, col)

            is_jump = abs(sel_row - row) + abs(sel_col - col) == 2
            if is_jump:
                self.jump_mode = True
                self.visited_in_chain.add((sel_row, sel_col))
                self.visited_in_chain.add((row, col))

                more = self.board.get_valid_moves(
                    self.current_player, self.selected, force_jumps=True, forbid_dests=self.visited_in_chain
                )
                if not more:
                    self._end_turn()
                return None
            else:
                self._end_turn()
        return None

    def _handle_right_click(self, pos):
        if self.winner:
            return None
        if not self._is_human_turn():
            return None  # can't interact on bot's turn
        if not self.jump_mode or not self.selected:
            return None

        row, col = self._screen_to_grid(pos)
        if (row, col) == self.selected:
            more = self.board.get_valid_moves(
                self.current_player,
                self.selected,
                force_jumps=True,
                forbid_dests=self.visited_in_chain if self.visited_in_chain else None
            )
            if more:
                return None
            self._end_turn()
        return None

    def handle_mouse(self, e):
        if e.button == 1:
            return self._handle_left_click(e.pos)
        elif e.button == 3:
            return self._handle_right_click(e.pos)
        return None

    # draw
    def draw(self):
        self.screen.blit(self.board_img, (0, 0))

        for row in range(len(self.board.grid)):
            for col in range(len(self.board.grid[row])):
                v = self.board.get(row, col)
                if v == P1:
                    self.screen.blit(self.wp_img, (col * SQUARE + self.offset, row * SQUARE + self.offset))
                elif v == P2:
                    self.screen.blit(self.bp_img, (col * SQUARE + self.offset, row * SQUARE + self.offset))

        # highlights for the human turn
        if self.selected and not self.winner and self._is_human_turn():
            for move_row, move_col in self._valid_moves_for_selected():
                pygame.draw.rect(self.screen, (0, 255, 0), (move_col * SQUARE, move_row * SQUARE, SQUARE, SQUARE), 5)
            sel_row, sel_col = self.selected
            pygame.draw.rect(self.screen, (255, 255, 0), (sel_col * SQUARE, sel_row * SQUARE, SQUARE, SQUARE), 5)
            if self.jump_mode:
                hint = self.hint_font.render("Finish chain: right-click when no jumps remain", True, (255, 255, 255))
                bg = hint.get_rect()
                bg.topleft = (10, 10)
                pad = 8
                pygame.draw.rect(self.screen, (0, 0, 0, 160), (bg.x - pad, bg.y - pad, bg.w + 2*pad, bg.h + 2*pad))
                self.screen.blit(hint, (bg.x, bg.y))

        # winner overlay + buttons
        if self.winner:
            dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 160))
            self.screen.blit(dim, (0, 0))
            msg = "Player 1 wins!" if self.winner == P1 else "Player 2 wins!"
            text = self.font.render(msg, True, (255, 255, 255))
            self.screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
            def draw_btn(rect, label):
                pygame.draw.rect(self.screen, (240, 240, 240), rect, border_radius=10)
                t = self.small_font.render(label, True, (20, 20, 20))
                self.screen.blit(t, t.get_rect(center=rect.center))
            draw_btn(self.btn_replay, "Replay")
            draw_btn(self.btn_menu,   "Back to Menu")

    # loop
    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return settings.QUIT_GAME
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    if self.winner:
                        return settings.RESTART_MENU
                    else:
                        return settings.QUIT_GAME
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    res = self.handle_mouse(e)
                    if res == settings.RESTART_MENU:
                        return settings.RESTART_MENU

            # let bot play automatically when it's its turn
            if self.vs_bot and not self.winner and self.bot_player is not None and self.current_player == self.bot_player:
                self._bot_take_turn()

            self.draw()
            pygame.display.update()
            self.clock.tick(FPS)
