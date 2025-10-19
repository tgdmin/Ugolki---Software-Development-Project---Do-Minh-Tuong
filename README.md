# Ugolki---Software-Development-Project---Do-Minh-Tuong
* Game description: Ugolki (Russian: [ʊɡɐɫˈkʲi], Russian: уголки, English: corners) is a two-player board game, similar to halma, that is typically played on an 8×8 grid board with 16 game pieces per player. 
It is said to have been invented in Europe in the late 18th century. Variations on the size of the board and the number of game pieces also exist.
---------------
* Game rules:
Both players start off with square arrangements of 16 game pieces in opposing corners of the gameboard. Each player's goal is to move all their pieces from the starting corner to the corner occupied by the opponent at the start of the game.
Players take turns moving one game piece. A piece may move only away from the starting location into a destination that is empty, provided either of the following conditions are met:
the destination square is adjacent to the starting square
the destination square can be reached by consecutive "jumps" over other game pieces belonging to either player.
The game ends when both players have no available moves left. Game pieces are counted within the square bounds of the final formation, and the player with more pieces wins.
---------------
* Materials:
Board.png - The graphic of the board
WP.png - Player 1 pieces
BP.png - Player 2 pieces
---------------
* Ideas:
The board is basically a 2D matrix 8x8, index from 0 to 7 where all boxes are marked EMPTY
We ll place all the pieces of the 2 players in the bottom left and top right conner marked as 1 and 2
For each moves, the algorithm must check:
    - If the adjacent box is empty or not
    - If it is empty, then you can move there only vertically or horizontally
    - if it is not empty then check if the next box adjacent to it is empty or not
    - If yes, then you can make the jump to that box
    - Check if in the position after the jump, could you jump anymore, if yes then repeat jumping process until you no longer can jump anywhere
    - Players take turn everytime, except for the continuos jump
Winning condition:2D matrix from col 5 (index 4) to col 8 (index 7), row 1 (index 0) to row 3 (index 2) marked as 1 or the opposite marked as 2
---------------
* UML-style box format (Still updating..)
- Piece : repersents a game piece
    + player : int
    + piece(player:int)

- Board : manage all the state of the board (position of pieces, valid moves,..)
    + grid : list[list[int]]
    + board()
    + get(row:int, col:int) : int
    + set(row:int, col:int, value:int) : void
    + is_empty(row:int, col:int) : bool
    + is_adjacent(src:tuple, dst:tuple) : bool
    + get_valid_moves(pos:tuple) : list[tuple]
    + is_target_camp_filled(player:int) : bool

- Game : control the game loop, drawing everything you see, input and turns and check the winner
    + screen : pygame.Surface
    + clock : pygame.time.Clock
    + board : Board
    + selected_piece : tuple[int,int] or None
    + current_player : int
    + winner : int or None
    + font : pygame.font.Font
    + board_img : pygame.Surface
    + wp_img : pygame.Surface
    + bp_img : pygame.Surface
    + offset : int
    + game()
    + load_assets() : void
    + handle_mouse(pos:tuple[int,int]) : void
    + draw() : void
    + run() : void