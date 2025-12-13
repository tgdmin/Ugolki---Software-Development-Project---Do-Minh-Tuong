# pod_board.py
from typing import Set, List
from base_board import BaseBoard, Pos
from settings import N, EMPTY, P1, P2


def is_dark(r: int, c: int) -> bool:
    """Ô đen (chỉ chơi trên ô đen)."""
    return (r + c) % 2 == 1


class PodBoard(BaseBoard):
    """
    Bàn cờ cho Poddavki / giveaway checkers :
    - Man đi chéo lên phía trước 1 ô.
    - Man ăn chéo lên phía trước 2 ô (không được ăn lùi).
    - King đi chéo 1 ô (cả 4 hướng).
    - King ăn như Man nhưng được ăn cả 4 hướng (cũng chỉ 2 ô, không bay).
    """

    def __init__(self):
        super().__init__()

        # Setup 3 hàng trên và 3 hàng dưới, chỉ trên ô đen
        for r in range(3):  # top 3 rows: P2
            for c in range(N):
                if is_dark(r, c):
                    self.grid[r][c] = P2

        for r in range(N - 3, N):  # bottom 3 rows: P1
            for c in range(N):
                if is_dark(r, c):
                    self.grid[r][c] = P1

        # King được lưu bằng set vị trí
        self.kings: Set[Pos] = set()

    # -------- tiện ích cơ bản --------
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
        sr, sc = src
        dr, dc = dst
        v = self.get(sr, sc)
        self.set(dr, dc, v)
        self.set(sr, sc, EMPTY)
        if src in self.kings:
            self.kings.remove(src)
            self.kings.add(dst)

    def forward_dir(self, player: int) -> int:
        # P1 ở dưới đi lên (-1), P2 ở trên đi xuống (+1)
        return -1 if player == P1 else 1

    def in_kings_row(self, player: int, r: int) -> bool:
        return (player == P1 and r == 0) or (player == P2 and r == N - 1)

    # -------- simple moves (không ăn) --------
    def _simple_moves_from(self, player: int, pos: Pos) -> List[Pos]:
        """
        Man: đi chéo lên phía trước 1 ô (không bao giờ đi lùi).
        King: đi chéo 1 ô theo mọi hướng (không bay trong nước đi thường).
        """
        r, c = pos
        if not self.own(player, r, c):
            return []
        moves: List[Pos] = []

        if self.is_king(pos):
            # King: 1 ô chéo, 4 hướng
            for dr in (-1, 1):
                for dc in (-1, 1):
                    nr, nc = r + dr, c + dc
                    if self.in_bounds(nr, nc) and self.is_empty(nr, nc):
                        moves.append((nr, nc))
        else:
            # Man: chỉ đi lên phía trước 1 ô chéo
            d = self.forward_dir(player)
            for dc in (-1, 1):
                nr, nc = r + d, c + dc
                if self.in_bounds(nr, nc) and self.is_empty(nr, nc):
                    moves.append((nr, nc))

        return moves

    # -------- captures từ 1 quân --------
    def _captures_from(self, player: int, pos: Pos, captured_in_chain: Set[Pos]) -> List[Pos]:
        """
        Trả về danh sách ô đáp (landing) cho mọi nước ăn từ pos,
        với danh sách quân đã ăn trong chain (captured_in_chain).
        """
        if not self.own(player, pos[0], pos[1]):
            return []
        if self.is_king(pos):
            return self._king_captures(player, pos, captured_in_chain)
        else:
            return self._man_captures(player, pos, captured_in_chain)

    def _man_captures(self, player: int, pos: Pos, captured_in_chain: Set[Pos]) -> List[Pos]:
        """
        Man CHỈ được ăn tiến:
        - Nhảy chéo 2 ô về phía trước, qua đầu 1 quân địch, đáp tại ô trống sau nó.
        """
        r, c = pos
        res: List[Pos] = []
        d = self.forward_dir(player)  # chỉ hướng tới (không ăn lùi)

        for dc in (-1, 1):
            mr, mc = r + d, c + dc
            lr, lc = r + 2 * d, c + 2 * dc
            if not self.in_bounds(lr, lc):
                continue
            if not self.enemy(player, mr, mc):
                continue
            if (mr, mc) in captured_in_chain:
                continue
            if not self.is_empty(lr, lc):
                continue
            res.append((lr, lc))

        return res

    def _king_captures(self, player: int, pos: Pos, captured_in_chain: Set[Pos]) -> List[Pos]:
        """
        King ăn GIỐNG Man nhưng được ăn cả 4 hướng:
        - Nhảy đúng 2 ô chéo (không bay),
        - Phải qua đúng 1 quân địch chưa bị ăn trước đó.
        """
        r, c = pos
        res: List[Pos] = []

        for dr in (-1, 1):
            for dc in (-1, 1):
                mr, mc = r + dr, c + dc
                lr, lc = r + 2 * dr, c + 2 * dc

                if not self.in_bounds(lr, lc):
                    continue
                if not self.enemy(player, mr, mc):
                    continue
                if (mr, mc) in captured_in_chain:
                    continue
                if not self.is_empty(lr, lc):
                    continue

                res.append((lr, lc))

        return res

    # -------- helpers tổng quát --------
    def has_any_capture(self, player: int) -> bool:
        """Dùng để check còn nước ăn nào không (cho điều kiện thắng)."""
        for r in range(N):
            for c in range(N):
                if self.own(player, r, c):
                    if self._captures_from(player, (r, c), set()):
                        return True
        return False

    def has_any_move(self, player: int) -> bool:
        """
        Kiểm tra player còn nước đi hợp lệ nào không (ăn hoặc đi thường).
        Dùng cho điều kiện thắng Poddavki: ai không còn move thì WIN.
        """
        if self.has_any_capture(player):
            return True
        for r in range(N):
            for c in range(N):
                if self.own(player, r, c):
                    if self._simple_moves_from(player, (r, c)):
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
        Trả về các ô đích hợp lệ cho quân tại pos.

        - force_captures = True  => chỉ trả captures.
        - force_captures = False => nếu quân này có capture thì trả captures,
          nếu không thì trả simple moves.
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
        Kiểm tra nước src->dst có phải là nước ăn hợp lệ không,
        và nếu đúng thì trả về vị trí quân địch bị ăn.
        (Áp dụng cho cả Man và King, vì đều nhảy đúng 2 ô.)
        """
        sr, sc = src
        dr, dc = dst

        # Capture phải đúng 2 ô chéo
        if abs(sr - dr) != 2 or abs(sc - dc) != 2:
            return False, None

        mr = (sr + dr) // 2
        mc = (sc + dc) // 2

        if not self.enemy(player, mr, mc):
            return False, None
        if (mr, mc) in captured_in_chain:
            return False, None

        return True, (mr, mc)
