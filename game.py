# game.py
from typing import Optional, Tuple, Set, List
import random
import pygame
from board import Board
from settings import (
    WIDTH, HEIGHT, FPS, SQUARE, EMPTY, P1, P2,
    BOARD_IMG_PATH, WP_IMG_PATH, BP_IMG_PATH,
    WINDOW_TITLE, ICON_PATH
)

Pos = Tuple[int, int]

class Game:
    # supports Vs Bot or Vs Player 2
    def __init__(self, vs_bot: bool = True):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()

        self.vs_bot = vs_bot  # True => P2 is bot
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
            print("Image load error:", e)
            pygame.quit()
            raise SystemExit(1)

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
        if self.winner or not self.vs_bot or self.current_player != P2:
            return

        # collect P2 pieces 
        pieces: List[Pos] = [(r, c)
                             for r in range(len(self.board.grid))
                             for c in range(len(self.board.grid[r]))
                             if self.board.get(r, c) == P2]
        random.shuffle(pieces)

        # try jump first (take the first chain we can)
        for pos in pieces:
            all_moves = self.board.get_valid_moves(P2, pos, force_jumps=False)
            jump_moves = [m for m in all_moves if abs(m[0] - pos[0]) + abs(m[1] - pos[1]) == 2]
            if jump_moves:
                self._bot_play_jump_chain(pos, jump_moves[0])
                return

        # else do first step we see
        for pos in pieces:
            all_moves = self.board.get_valid_moves(P2, pos, force_jumps=False)
            step_moves = [m for m in all_moves if abs(m[0] - pos[0]) + abs(m[1] - pos[1]) == 1]
            if step_moves:
                self._bot_move_piece(pos, step_moves[0])
                self._finish_bot_turn()
                return


    def _bot_move_piece(self, src: Pos, dst: Pos):
        sr, sc = src
        dr, dc = dst
        self.board.set(dr, dc, self.board.get(sr, sc))
        self.board.set(sr, sc, EMPTY)

    def _bot_play_jump_chain(self, start: Pos, first_dst: Pos):
        self._bot_move_piece(start, first_dst)
        visited = {start, first_dst}
        cur = first_dst

        # keep chaining jumps; always pick the first available
        while True:
            more = self.board.get_valid_moves(P2, cur, force_jumps=True, forbid_dests=visited)
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
        if self.board.is_target_camp_filled(P2):
            self.winner = P2
            return
        self.current_player = P1
    

    # input (human)
    def _handle_left_click(self, pos):
        if self.winner:
            mx, my = pos
            if self.btn_replay.collidepoint(mx, my):
                self._reset_game()
            elif self.btn_menu.collidepoint(mx, my):
                return "menu"
            return None

        # ignore clicks on bot's turn
        if self.vs_bot and self.current_player == P2:
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

            sr, sc = self.selected
            self.board.set(row, col, self.board.get(sr, sc))
            self.board.set(sr, sc, EMPTY)
            self.selected = (row, col)

            is_jump = abs(sr - row) + abs(sc - col) == 2
            if is_jump:
                self.jump_mode = True
                self.visited_in_chain.add((sr, sc))
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
        if self.vs_bot and self.current_player == P2:
            return None  # can't interact on bot's turn
        if not self.jump_mode or not self.selected:
            return None

        row, col = self._screen_to_grid(pos)
        if (row, col) == self.selected:
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

        for r in range(len(self.board.grid)):
            for c in range(len(self.board.grid[r])):
                v = self.board.get(r, c)
                if v == P1:
                    self.screen.blit(self.wp_img, (c * SQUARE + self.offset, r * SQUARE + self.offset))
                elif v == P2:
                    self.screen.blit(self.bp_img, (c * SQUARE + self.offset, r * SQUARE + self.offset))

        # highlights for the human turn
        if self.selected and not self.winner and (not self.vs_bot or self.current_player == P1):
            for mr, mc in self._valid_moves_for_selected():
                pygame.draw.rect(self.screen, (0, 255, 0), (mc * SQUARE, mr * SQUARE, SQUARE, SQUARE), 5)
            sr, sc = self.selected
            pygame.draw.rect(self.screen, (255, 255, 0), (sc * SQUARE, sr * SQUARE, SQUARE, SQUARE), 5)
            if self.jump_mode:
                hint = self.hint_font.render("Right-click current piece to stop jumping", True, (255, 255, 255))
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
                    pygame.quit()
                    raise SystemExit(0)
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    if self.winner:
                        return "menu"
                    else:
                        pygame.quit()
                        raise SystemExit(0)
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    res = self.handle_mouse(e)
                    if res == "menu":
                        return "menu"

            # let bot play automatically when it's its turn
            if self.vs_bot and not self.winner and self.current_player == P2:
                self._bot_take_turn()

            self.draw()
            pygame.display.update()
            self.clock.tick(FPS)
