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
    + Board.png : The graphic of the board
    + WP.png : Player 1 pieces
    + BP.png : Player 2 pieces
----------------
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
* Controls

Left-click: select a piece / move to a highlighted square

Right-click (during a jump chain): stop the chain and end your turn

ESC: back (from Rules/Mode) or quit (from Main)

Replay / Menu buttons appear after a win
---------------
* Move & Jump Logic
Board is an 8×8 matrix grid[r][c] with values {0=EMPTY, 1=P1, 2=P2}.

Step: from (r,c) to (r±1,c) or (r,c±1) if target is empty.

Jump: from (r,c), if (r+dr,c+dc) has a piece and (r+2dr,c+2dc) is empty → you can jump to (r+2dr,c+2dc).

Chain: you can keep jumping as long as jump destinations exist. After each jump, valid jump squares are recalculated on the current board state.

* Jump Chain (DFS) — Explained

We use a small DFS (Depth-First Search) to discover all reachable landing squares by chaining orthogonal jumps:

From start, test the 4 directions:

middle = start + (dr,dc) must have a piece

landing = start + 2*(dr,dc) must be empty and in bounds

Record each valid landing, then DFS(landing) to explore further jumps.

Keep a visited set of cells already landed on in this turn to avoid backtracking/loops in the same chain.

When the player (or bot) actually jumps, we recompute valid jumps from the new position.

Result: highlight shows only valid next jumps at every step.
----------------
* Camp Rule (Toggleable)

In Start Menu, you’ll see a toggle: “Camp rule: ON/OFF”.

When ON: if a piece enters the opponent’s target camp, subsequent moves for that piece must stay within the camp.

When OFF: no restriction after entering camp (classic variants differ; we keep it configurable).

The menu passes this choice into settings.ENFORCE_CAMP_RULE.
----------------
* Simple Bot
A very basic bot to allow single-player:

Collect all P2 pieces.

Prefer jumps: take the first available jump and chain as long as possible.

If no jumps, step one square if possible.

If totally blocked, end turn.
This is intentionally simple (good for demonstrating the engine and turn flow).
----------------
* UML-style box format (Still updating..)
- Piece : repersents a game piece
    + player : int // 0, 1, 2
    + piece(player:int)

- Board : manage all the state of the board (position of pieces, valid moves,..)
    + grid: list[list[int]]
    + __init__()
    + get(row:int, col:int) -> int
    + set(row:int, col:int, value:int) -> None
    + is_empty(row:int, col:int) -> bool
    + in_bounds(row:int, col:int) -> bool
    + _step_moves(pos:tuple[int,int]) -> list[tuple[int,int]]
    + _jump_landings(start:tuple, forbid:set[tuple], camp_cells:set[tuple]|None) -> set[tuple]
    + get_valid_moves(player:int, pos:tuple|None, force_jumps:bool=False, forbid_dests:set|None=None) -> list[tuple]
    + is_target_camp_filled(player:int) -> bool


- Game : control the game loop, drawing everything you see, input and turns and check the winner
    + screen: pygame.Surface
    + clock: pygame.time.Clock
    + board: Board
    + selected_piece: tuple[int,int] | None
    + current_player: int
    + jump_mode: bool
    + visited_in_chain: set[tuple]
    + winner: int | None
    + vs_bot: bool
    + __init__(...)
    + load_assets() -> None
    + handle_mouse(pos, button) -> None
    + move_piece(row:int, col:int) -> None
    + end_turn() -> None
    + _maybe_bot_turn() -> None
    + _bot_take_turn() -> None
    + _bot_play_jump_chain(start, first_dst) -> None
    + _bot_move_piece(src, dst) -> None
    + draw() -> None
    + run() -> None

- StartMenu : Start, rules, mode select
    + __init__(width:int, height:int)
    + draw_main() -> None
    + draw_mode() -> None
    + draw_rules() -> None
    + run() -> dict|None   # returns {"camp_rule": bool, "vs_bot": bool} or None to quit
