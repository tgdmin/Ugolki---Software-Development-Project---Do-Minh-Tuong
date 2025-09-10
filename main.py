import pygame
from sys import exit

pygame.init()
WIDTH, HEIGHT = 600, 600
N = 8  
CAMP = 4 
EMPTY, P1, P2 = 0, 1, 2

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ugolki - Software Development Project - Do Minh Tuong")
clock = pygame.time.Clock()

# Board and Pieces set up
try:
    board_img = pygame.image.load("Board.png").convert_alpha()
    wp_img = pygame.image.load("WP.png").convert_alpha()
    bp_img = pygame.image.load("BP.png").convert_alpha()
    icon_img = pygame.image.load("BP.png").convert_alpha()
    pygame.display.set_icon(icon_img)
except pygame.error as e:
    print(f"Error loading board image: {e}")
    pygame.quit()
    exit()

# Scale
board_img = pygame.transform.smoothscale(board_img, (WIDTH, HEIGHT))
SQUARE = WIDTH // 8

scale_factor = 0.75
piece_size = int(SQUARE * scale_factor)
offset = (SQUARE - piece_size) // 2

wp_img = pygame.transform.smoothscale(wp_img, (piece_size, piece_size))
bp_img = pygame.transform.smoothscale(bp_img, (piece_size, piece_size))


board = [[EMPTY for _ in range(N)] for _ in range(N)]

# P1 left corner
for row in range(N - CAMP + 1, N):
    for col in range(CAMP): 
        board[row][col] = P1
        
# P2 right corner
for row in range(CAMP - 1):
    for col in range(N - CAMP , N):
        board[row][col] = P2

selected_piece = None
current_player = P1  

def is_adjacent(selected_piece, target_piece):
    selected_row, selected_col = selected_piece
    target_row, target_col = target_piece
    return (abs(selected_row - target_row) == 1 and selected_col == target_col) or \
           (abs(selected_col - target_col) == 1 and selected_row == target_row)

def get_valid_moves(selected_piece):
    moves = []
    if not selected_piece:
        return moves
    row, col = selected_piece
    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < N and 0 <= new_col < N:
            if board[new_row][new_col] == EMPTY:
                moves.append((new_row, new_col))
    return moves

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            col, row = mouse_x // SQUARE, mouse_y // SQUARE
            # Check if the square is clicked
            if selected_piece is None and board[row][col] == current_player:
                selected_piece = (row, col)
            # Click again to deselect
            elif selected_piece == (row, col):
                selected_piece = None
            # Move the piece to nearby empty
            elif selected_piece:
                if board[row][col] == EMPTY and is_adjacent(selected_piece, (row, col)):
                    selected_row, selected_col = selected_piece
                    board[row][col] = board[selected_row][selected_col]
                    board[selected_row][selected_col] = EMPTY
                    selected_piece = None
                    # Change player
                    current_player = P2 if current_player == P1 else P1
    
    # Draw the board
    screen.blit(board_img, (0, 0))
    
    # Draw the pieces
    for row in range(N):
        for col in range(N):
            if board[row][col] == P1:
                screen.blit(wp_img, (col * SQUARE + offset, row * SQUARE + offset))
            elif board[row][col] == P2:
                screen.blit(bp_img, (col * SQUARE + offset, row * SQUARE + offset))

    # Highlight valid moves
    if selected_piece:
        for move_row, move_col in get_valid_moves(selected_piece):
            pygame.draw.rect(
                screen,
                (0, 255, 0),  
                (move_col * SQUARE, move_row * SQUARE, SQUARE, SQUARE),
                5
            )

    # Highlight selected piece
    if selected_piece:
        sel_row, sel_col = selected_piece
        pygame.draw.rect(screen, (255, 255, 0), (sel_col * SQUARE, sel_row * SQUARE, SQUARE, SQUARE), 5)

    pygame.display.update()
    clock.tick(60)


    #them dong nay vao de test github
