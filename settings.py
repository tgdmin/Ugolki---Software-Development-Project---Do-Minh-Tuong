import pygame

# window size
WIDTH, HEIGHT = 600, 600
FPS = 60

# board stuff
N = 8               
CAMP = 4            
EMPTY, P1, P2 = 0, 1, 2
SQUARE = WIDTH // N

# camps 
P1_START_ROWS = range(N - CAMP + 1, N)  
P1_START_COLS = range(CAMP)              
P2_START_ROWS = range(CAMP - 1)          
P2_START_COLS = range(N - CAMP, N)       

# where each player needs to go
PLAYER_TARGETS = {
    P1: (P2_START_ROWS, P2_START_COLS),
    P2: (P1_START_ROWS, P1_START_COLS),
}

# once a piece enters its target camp, it stays inside
ENFORCE_CAMP_RULE = True

# image paths 
BOARD_IMG_PATH = "assets/Board.png"
WP_IMG_PATH = "assets/WP.png"
BP_IMG_PATH = "assets/BP.png"

WINDOW_TITLE = "Ugolki - Software Development Project - Do Minh Tuong"
ICON_PATH = BP_IMG_PATH
