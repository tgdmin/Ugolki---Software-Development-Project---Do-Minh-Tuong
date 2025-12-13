import pygame

# window size
WIDTH, HEIGHT = 600, 600
FPS = 60

# board stuff
N = 8               # 8x8 board
CAMP = 4            # Ugolki camp size
EMPTY, P1, P2 = 0, 1, 2
SQUARE = WIDTH // N

# camps for Ugolki
P1_START_ROWS = range(N - CAMP + 1, N)  # bottom rows
P1_START_COLS = range(CAMP)             # left cols
P2_START_ROWS = range(CAMP - 1)         # top rows
P2_START_COLS = range(N - CAMP, N)      # right cols

# where each player needs to go in Ugolki
PLAYER_TARGETS = {
    P1: (P2_START_ROWS, P2_START_COLS),
    P2: (P1_START_ROWS, P1_START_COLS),
}

# once a piece enters its target camp, it stays inside (Ugolki)
ENFORCE_CAMP_RULE = True

# image paths
BOARD_IMG_PATH = "assets/Board.png"
WP_IMG_PATH = "assets/WP.png"
BP_IMG_PATH = "assets/BP.png"

WINDOW_TITLE = "Ugolki - Software Development Project - Do Minh Tuong"
ICON_PATH = BP_IMG_PATH
LOGO_PATH = "assets/logo.png"
