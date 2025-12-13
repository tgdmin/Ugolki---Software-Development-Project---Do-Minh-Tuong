# pod_game.py
from typing import Optional, Tuple, Set, List
import random
import pygame
from pod_board import PodBoard, Pos
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
    def __init__(self, vs_bot: bool = False):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Poddavki")
        self.clock = pygame.time.Clock()

        self.vs_bot = vs_bot
        self.board = PodBoard()
        self.selected: Optional[Pos] = None
        self.current_player = P1
        self.winner: Optional[int] = None

        # trạng thái chuỗi ăn
        self.jump_mode = False
        self.captured_in_chain: Set[Pos] = set()

        self._load_assets()
        self.font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 28)
        self.hint_font = pygame.font.SysFont(None, 22)

    # ---------- assets ----------
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

    # ---------- helpers ----------
    def _screen_to_grid(self, pos) -> Pos:
        x, y = pos
        return (y // SQUARE, x // SQUARE)

    def _valid_moves_for_selected(self) -> List[Pos]:
        """
        Bắt buộc ăn theo QUÂN:

        - Nếu đang ở giữa chain (jump_mode=True) thì luôn phải ăn tiếp nếu còn.
        - Nếu chưa ở trong chain:
            + Check xem QUÂN ĐANG CHỌN có capture không.
            + Nếu có -> force_captures=True cho quân này.
            + Nếu không -> đi simple moves bình thường.
        """
        if not self.selected:
            return []

        captured = self.captured_in_chain if self.jump_mode else set()

        if self.jump_mode:
            force_caps = True
        else:
            piece_caps = self.board._captures_from(self.current_player, self.selected, set())
            force_caps = bool(piece_caps)

        return self.board.get_valid_moves_for_piece(
            self.current_player,
            self.selected,
            force_captures=force_caps,
            captured_in_chain=captured,
        )

    def _end_turn(self):
        # sau khi kết thúc chuỗi ăn, remove các quân bị ăn
        for pos in self.captured_in_chain:
            self.board.remove_piece(pos)

        self.jump_mode = False
        self.captured_in_chain.clear()
        self.selected = None

        # đổi lượt
        self.current_player = P2 if self.current_player == P1 else P1

        # Poddavki: player WIN nếu chính player đó không còn move nào
        if not self.board.has_any_move(self.current_player):
            self.winner = self.current_player

    # ---------- BOT logic (P2) ----------
    def _bot_take_turn(self):
        """
        Bot rất đơn giản:
        - Nếu P2 không còn nước đi -> P2 thắng ngay (theo luật).
        - Nếu có nước ăn:
            + Chọn ngẫu nhiên một nước ăn (src, dst),
              sau đó chơi full chuỗi multi-jump cho quân đó.
        - Nếu không có nước ăn:
            + Tìm các simple moves.
            + Ưu tiên nước đi tiến (tăng row) nếu có, rồi random.
        """
        if self.winner:
            return
        if self.current_player != P2:
            return

        # nếu P2 không còn move P2 thắng luôn
        if not self.board.has_any_move(P2):
            self.winner = P2
            return

        capture_options: List[Tuple[Pos, Pos]] = []
        simple_options: List[Tuple[Pos, Pos]] = []
        forward_options: List[Tuple[Pos, Pos]] = []

        # duyệt các quân của P2
        for r in range(len(self.board.grid)):
            for c in range(len(self.board.grid[r])):
                if self.board.get(r, c) == P2:
                    pos = (r, c)
                    caps = self.board._captures_from(P2, pos, set())
                    if caps:
                        for dst in caps:
                            capture_options.append((pos, dst))
                    else:
                        moves = self.board._simple_moves_from(P2, pos)
                        for dst in moves:
                            simple_options.append((pos, dst))
                            # ưu tiên move tiến (row tăng)
                            if dst[0] > r:
                                forward_options.append((pos, dst))

        if capture_options:
            src, dst = random.choice(capture_options)
            self._bot_play_capture_chain(src, dst)
            return

        if simple_options:
            if forward_options:
                src, dst = random.choice(forward_options)
            else:
                src, dst = random.choice(simple_options)

            # thực hiện simple move
            was_king = self.board.is_king(src)
            self.board.move_piece(src, dst)
            if not was_king and self.board.in_kings_row(P2, dst[0]):
                self.board.make_king(dst)

            self.captured_in_chain = set()
            self.jump_mode = False
            self.selected = None
            self._end_turn()
            return

        self.winner = P2

    def _bot_play_capture_chain(self, src: Pos, first_dst: Pos):
        """
        Cho P2 chơi full chuỗi multi-jump bắt đầu từ src to first_dst.
        """
        captured: Set[Pos] = set()
        cur = src
        dst = first_dst

        while True:
            was_king = self.board.is_king(cur)
            is_cap, enemy_pos = self.board.is_capture_move(P2, cur, dst, captured)
            if not is_cap or enemy_pos is None:
                break

            # move
            self.board.move_piece(cur, dst)
            if not was_king and self.board.in_kings_row(P2, dst[0]):
                self.board.make_king(dst)

            captured.add(enemy_pos)

            # tìm các capture tiếp theo cho quân này
            more = self.board.get_valid_moves_for_piece(
                P2,
                dst,
                force_captures=True,
                captured_in_chain=captured,
            )
            if not more:
                break

            cur = dst
            dst = random.choice(more)

        # kết thúc lượt bot
        self.captured_in_chain = captured
        self.jump_mode = False
        self.selected = None
        self._end_turn()

    # ---------- input (human) ----------
    def _handle_left_click(self, pos):
        if self.winner:
            # click bất kỳ sau khi thắng -> về menu
            return "menu"

        if self.vs_bot and self.current_player == P2:
            return None  # đang là lượt bot, ignore click

        row, col = self._screen_to_grid(pos)

        # CHỌN QUÂN
        if self.selected is None:
            if self.board.get(row, col) == self.current_player:
                self.selected = (row, col)
                self.jump_mode = False
                self.captured_in_chain.clear()
            return None

        # click lại vào chính nó để bỏ chọn (nếu chưa ở trong chain)
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

        # di chuyển quân
        was_king = self.board.is_king(src)
        self.board.move_piece(src, dest)
        self.selected = dest

        # phong Vua nếu cần (Man chạm hàng cuối)
        if not was_king and self.board.in_kings_row(self.current_player, dest[0]):
            self.board.make_king(dest)

        if is_cap and enemy_pos is not None:
            # đã ăn 1 quân thì vào chain
            self.jump_mode = True
            self.captured_in_chain.add(enemy_pos)

            # xem còn ăn tiếp được không
            more = self.board.get_valid_moves_for_piece(
                self.current_player,
                self.selected,
                force_captures=True,  # trong chain: còn là phải ăn
                captured_in_chain=self.captured_in_chain,
            )
            if not more:
                self._end_turn()
        else:
            # simple move: chỉ xảy ra khi quân này không có capture
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

        # highlight nước đi
        if self.selected and not self.winner:
            for (mr, mc) in self._valid_moves_for_selected():
                pygame.draw.rect(
                    self.screen,
                    (0, 255, 0),
                    (mc * SQUARE, mr * SQUARE, SQUARE, SQUARE),
                    5,
                )
            sr, sc = self.selected
            pygame.draw.rect(
                self.screen,
                (255, 255, 0),
                (sc * SQUARE, sr * SQUARE, SQUARE, SQUARE),
                5,
            )

            # hint: chỉ hiện nếu quân đang chọn có thể ăn hoặc đang ở trong chain
            piece_caps_now = self.board._captures_from(
                self.current_player, self.selected, set()
            )
            if self.jump_mode or piece_caps_now:
                hint = self.hint_font.render(
                    "This piece must capture if it can",
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
                    pygame.quit()
                    raise SystemExit(0)
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    return "menu"
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    res = self.handle_mouse(e)
                    if res == "menu":
                        return "menu"

            # cho bot chơi tự động khi tới lượt
            if self.vs_bot and not self.winner and self.current_player == P2:
                self._bot_take_turn()

            self.draw()
            pygame.display.update()
            self.clock.tick(FPS)
