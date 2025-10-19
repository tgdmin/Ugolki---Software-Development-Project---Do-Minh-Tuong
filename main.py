import pygame
from sys import exit

pygame.init()

WIDTH, HEIGHT = 600, 600
N = 8
CAMP = 4
EMPTY, P1, P2 = 0, 1, 2

SQUARE = WIDTH // N
P1_START_ROWS = range(N - CAMP + 1, N)
P1_START_COLS = range(CAMP)
P2_START_ROWS = range(CAMP - 1)
P2_START_COLS = range(N - CAMP, N)
PLAYER_TARGETS = {
    P1: (P2_START_ROWS, P2_START_COLS),
    P2: (P1_START_ROWS, P1_START_COLS),
}

class Piece:
    def __init__(self, player):
        self.player = player

class Board:
    """board state and related logic"""
    def __init__(self):
        self.grid = [[EMPTY for _ in range(N)] for _ in range(N)]
        # P1's pieces in the bottom left corner
        for row in P1_START_ROWS:
            for col in P1_START_COLS:
                self.grid[row][col] = P1
        # P 2's pieces in the top-right corner
        for row in P2_START_ROWS:
            for col in P2_START_COLS:
                self.grid[row][col] = P2

    def get(self, row, col):
        """value at a specific board position"""
        return self.grid[row][col]

    def set(self, row, col, value):
        """set the value at a specific board position"""
        self.grid[row][col] = value

    def is_empty(self, row, col):
        """a board position is empty or not"""
        return self.grid[row][col] == EMPTY

    def is_adjacent(self, src, dst):
        """check if two positions are adjacent"""
        sr, sc = src
        dr, dc = dst
        return (abs(sr - dr) == 1 and sc == dc) or (abs(sc - dc) == 1 and sr == dr)

    def get_valid_moves(self, pos):
        """list of valid moves for a piece at the given position"""
        moves = []
        if not pos:
            return moves
        row, col = pos
        # check all four directions
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < N and 0 <= nc < N and self.is_empty(nr, nc):
                moves.append((nr, nc))
        return moves

    def is_target_camp_filled(self, player):
        """check if the destination camp is fully occupied by the player"""
        rows, cols = PLAYER_TARGETS[player]
        return all(self.get(r, c) == player for r in rows for c in cols)

class Game:
    """Manages the game logic and user interface."""
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Ugolki - Software Development Project - Do Minh Tuong")
        self.clock = pygame.time.Clock()
        self.load_assets()
        self.board = Board()
        self.selected_piece = None
        self.current_player = P1
        self.winner = None
        self.font = pygame.font.SysFont(None, 48)

    def load_assets(self):
        """load images for the board and piece"""
        try:
            self.board_img = pygame.image.load("Board.png").convert_alpha()
            self.wp_img = pygame.image.load("WP.png").convert_alpha()
            self.bp_img = pygame.image.load("BP.png").convert_alpha()
            icon_img = pygame.image.load("BP.png").convert_alpha()
            pygame.display.set_icon(icon_img)
        except pygame.error as e:
            print(f"Error loading image: {e}")
            pygame.quit()
            exit()
        # scale 
        self.board_img = pygame.transform.smoothscale(self.board_img, (WIDTH, HEIGHT))
        scale_factor = 0.75
        piece_size = int(SQUARE * scale_factor)
        self.offset = (SQUARE - piece_size) // 2
        self.wp_img = pygame.transform.smoothscale(self.wp_img, (piece_size, piece_size))
        self.bp_img = pygame.transform.smoothscale(self.bp_img, (piece_size, piece_size))

    def handle_mouse(self, pos):
        """mouse click events for selecting and moving"""
        if self.winner:
            return
        col, row = pos[0] // SQUARE, pos[1] // SQUARE
        if self.selected_piece is None and self.board.get(row, col) == self.current_player:
            self.selected_piece = (row, col)
        elif self.selected_piece == (row, col):
            self.selected_piece = None
        elif self.selected_piece:
            if self.board.get(row, col) == EMPTY and self.board.is_adjacent(self.selected_piece, (row, col)):
                sr, sc = self.selected_piece
                # move 
                self.board.set(row, col, self.board.get(sr, sc))
                self.board.set(sr, sc, EMPTY)
                self.selected_piece = None
                # check for a winner before switching player
                if self.board.is_target_camp_filled(self.current_player):
                    self.winner = self.current_player
                else:
                    # switch player's turn
                    self.current_player = P2 if self.current_player == P1 else P1

    def draw(self):
        """draw the board, pieces, and highlight"""
        self.screen.blit(self.board_img, (0, 0))
        for row in range(N):
            for col in range(N):
                val = self.board.get(row, col)
                if val == P1:
                    self.screen.blit(self.wp_img, (col * SQUARE + self.offset, row * SQUARE + self.offset))
                elif val == P2:
                    self.screen.blit(self.bp_img, (col * SQUARE + self.offset, row * SQUARE + self.offset))
        # highlight its valid moves 
        if self.selected_piece:
            for move_row, move_col in self.board.get_valid_moves(self.selected_piece):
                pygame.draw.rect(
                    self.screen,
                    (0, 255, 0),  
                    (move_col * SQUARE, move_row * SQUARE, SQUARE, SQUARE),
                    5
                )
        #highlight the selected piece 
        if self.selected_piece:
            sel_row, sel_col = self.selected_piece
            pygame.draw.rect(self.screen, (255, 255, 0), (sel_col * SQUARE, sel_row * SQUARE, SQUARE, SQUARE), 5)
        if self.winner:
            message = "Player 1 wins!" if self.winner == P1 else "Player 2 wins!"
            text_surface = self.font.render(message, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            background_rect = text_rect.inflate(20, 20)
            pygame.draw.rect(self.screen, (0, 0, 0), background_rect)
            self.screen.blit(text_surface, text_rect)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse(pygame.mouse.get_pos())
            self.draw()
            pygame.display.update()
            self.clock.tick(60)

if __name__ == "__main__":
    Game().run()
