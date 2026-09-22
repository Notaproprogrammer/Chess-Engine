"""This file is used to define the basic chess concepts, squares, 
moves, the piece base class, the individual piece types.
"""

from __future__ import annotations
"""This delays evaluation of type hints until runtime is finished. 
It is useful because later in the file, Move refers to Piece, and 
Piece refers to Board, if you don't have this, it'd create forward-reference issues.
"""
from dataclasses import dataclass#dataclass lets us define Move with minimal boilerplate.

from typing import List, Optional, Tuple, TYPE_CHECKING
#List, Optional, Tuple are type annotations.
#TYPE_CHECKING is being used to avoid circular imports at runtime.

if TYPE_CHECKING:
    from board import Board
#This import is only used by static type checkers. prevents circular import problem 
# between pieces.py and board.py.

Square = Tuple[int, int]#Defines a square as a pair of integers (row, col).



def in_bounds(r: int, c: int) -> bool:
    #Checks whether a coordinate is on the 8×8 board.

    return 0 <= r < 8 and 0 <= c < 8


def square_name(r: int, c: int) -> str:
    #Converts internal board coordinates like (6, 4) into chess notation like e2.
    return f"{chr(ord('a') + c)}{8 - r}"


def parse_square(text: str) -> Square:
    #Converts notation like "e2" into internal coordinates

    text = text.strip().lower()
    if len(text) != 2:
        raise ValueError(f"Invalid square: {text}")
    file_ch, rank_ch = text[0], text[1]
    if file_ch < "a" or file_ch > "h" or rank_ch < "1" or rank_ch > "8":
        raise ValueError(f"Invalid square: {text}")
    c = ord(file_ch) - ord("a")
    r = 8 - int(rank_ch)
    return r, c


@dataclass
class Move:
    src: Square#Starting square
    dst: Square#Ending square
    promotion: Optional[str] = None#Promotion
    moved_piece: Optional["Piece"] = None#Moved piece
    captured_piece: Optional["Piece"] = None#Captured piece
    prev_turn: Optional[str] = None#Turn before the move, for undo

    def uci(self) -> str:
        #Returns the move in coordinate format like e2e4 or e7e8q.

        text = square_name(*self.src) + square_name(*self.dst)
        if self.promotion:
            text += self.promotion.lower()
        return text

    def __str__(self) -> str:
        return self.uci()


class Piece:
    #Default piece type and value. Subclasses override these.
    kind = "?"
    value = 0

    def __init__(self, color: str):
        #Creates a piece with color "w" or "b".
        if color not in ("w", "b"):
            raise ValueError("color must be 'w' or 'b'")
        self.color = color

    @property
    def symbol(self) -> str:
        #Returns the printed character for this piece. white=uppercase, black=lower
        return self.kind.upper() if self.color == "w" else self.kind.lower()

    def copy(self) -> "Piece":
        #Creates a new piece of the same type and color,used when cloning boards.
        return type(self)(self.color)

    def _slide_moves(self, board: "Board", r: int, c: int, dirs: List[Tuple[int, int]]) -> List[Move]:
        """
        Generate moves for pieces that move continuously in a direction (sliding pieces).

        Parameters:
            board: the current board object
            r: current row of the piece
            c: current column of the piece
            directions: list of (row_change, col_change) pairs representing directions

        Output:
            A list of Move objects representing valid moves.

        Rules:
            - For each direction, keep moving until:
                • You go out of bounds
                • You hit another piece
            - If a square is empty -> add move and continue
            - If it has an enemy piece -> add move and STOP in that direction
            - If it has your own piece -> STOP immediately (do not add move)
            - Do not modify the board

        Hint:
            Use a loop to continue stepping in each direction.
        """
        # TODO: Implement sliding movement logic
        move = []
        for direction in dirs: #each direction is a tuple 
            nr = r
            nc = c
            while True:
                nr += direction[0] #change the coordinates based on direction
                nc += direction[1]
                if in_bounds(nr,nc) : # check nr and nc after move to make sure the move is valid
                    if board.grid[nr][nc] == None: #run when no piece in that coordinate
                        move.append(Move(src= (r,c), dst= (nr,nc), promotion= None, moved_piece= board.grid[r][c],  captured_piece= None, prev_turn= board.turn))
                        # add possible move object to the move list
                    elif board.grid[nr][nc] != None: #when their is a piece in the way
                        if board.grid[nr][nc].color == self.color: #check color
                            break # same color means cannot move there so not append the move to the list
                        else:
                            move.append(Move(src= (r,c), dst= (nr,nc), promotion= None, moved_piece= board.grid[r][c],  captured_piece= board.grid[nr][nc], prev_turn=board.turn))
                            break #different color means can capture but cannot move futher so add the move and break out of the while loop
                else: break
        return move


    

    def _step_moves(self, board: "Board", r: int, c: int, deltas: List[Tuple[int, int]]) -> List[Move]:

        """
        Generate moves for pieces that move a fixed distance (one step per direction).

        Parameters:
            board: the current board object (used to check positions and pieces)
            r: current row of the piece
            c: current column of the piece
            steps: list of (row_change, col_change) pairs representing possible moves

        Output:
            A list of Move objects representing valid moves for this piece.

        Rules:
            - Each step represents a single possible move (no looping).
            - The move must stay inside the board.
            - If the destination square is empty -> add the move.
            - If the destination has an enemy piece -> add the move.
            - If the destination has your own piece -> do NOT add the move.
            - Do not modify the board.

        Hint:
            Loop through each (dr, dc) in steps and check the resulting square.
        """
        # TODO: Implement step-based movement logic
        moves = []
        for change_row, change_column in deltas: #Looping through the deltas list to find the row and column to move next to
            target_row = r + change_row
            target_column = c + change_column # finding out the next poisition to go to
            if in_bounds(target_row,target_column): # checks if the targeted square is within boundes by calling in_bounds function
                target_square = board.grid[target_row][target_column]
                if target_square is None:
                    moves.append(Move(src=(r,c), dst=(target_row,target_column))) # if targeted square is empty, adds that square as a possible move to the moves list as a Move object
                elif target_square.color != self.color:
                    moves.append(Move(src=(r,c),dst=(target_row,target_column),captured_piece=target_square)) # or if the square has an enemy piece, it returns the squre as a move object to the moves list, but also
                                                                                                              # records the capture if capture is possible or if it is captured. 
                else: 
                    continue 
            else:
                continue
        return moves # returns the list containing Move objects



        
       

    def pseudo_legal_moves(self, board: "Board", r: int, c: int) -> List[Move]:
        #Abstract method implemented by subclasses
        raise NotImplementedError

    def attacks(self, board: "Board", r: int, c: int) -> List[Square]:
        #Returns all attacked squares on p-l moves, used for check detection
        return [mv.dst for mv in self.pseudo_legal_moves(board, r, c)]


class Pawn(Piece):
    #Pawn behavior
    kind = "P"
    value = 100 #Worth 100 in evaluation function

    def pseudo_legal_moves(self, board: "Board", r: int, c: int) -> List[Move]:
        """
        Generate all pseudo-legal moves for a pawn.

        Parameters:
            board: the current board object
            r: current row of the pawn
            c: current column of the pawn

        Output:
            A list of Move objects for this pawn.

        Rules:
            - Pawn moves depend on color:
                • White moves up (row decreases)
                • Black moves down (row increases)
            - Forward move:
                • Can move 1 square forward if empty
            - Capture move:
                • Can move diagonally forward if an enemy piece is present

            ● pawn may move 2 squares from starting position
            ● promotion must include q, r, b, n
            - Do NOT allow moving off the board
            - Do NOT modify the board

        Hint:
            Check forward square and diagonal squares separately.
        """
        # TODO: Implement pawn movement logic
        #creating list of move objects
        moves_list = [] 
        if self.color == "w": #initiliasing starting row, direction of movement, and the promotional row for pawn with 
                              #specific color

            start_row = 6 #white pawns start from index 6
            movement_direction = -1 #white pawns go to a lower row index
            promotion_row = 0 #white pawns get promoted when the reach the row with index 0

        else: 
            start_row = 1 #black pawns start from index 1 
            movement_direction = 1 #black pawns go to a higher index
            promotion_row = 7 #they are promoted when the reach the row with index 7
        
        #Now for the movement for the pawns: 
        #initialising the target row for the pawn to move
        t_row = r + movement_direction
        #Checking if the move is in bounds or not and the target square is empty or not: 
        if in_bounds(t_row,c) and board.grid[t_row][c] is None:
            #checking if it is a promotional row or not:
            if t_row == promotion_row: 
                for promotion in ["n","b","r","q"]:
                    moves_list.append(Move(src=(r,c),dst=(t_row,c),promotion=promotion))
            else: 
                moves_list.append(Move(src=(r,c),dst=(t_row,c)))
        #Now for moving two squares if its the pawns starting move:
        #checking if its the start_row or not
        if r == start_row:
            t_row_2square = r + 2 * movement_direction #creating a new variable, with twice the movement direction now
            
            if in_bounds(t_row_2square,c) and board.grid[t_row][c] is None and board.grid[t_row_2square][c] is None: # checking if the next square in front of the pawn is empty or not otherwise can not move two squares. 
                moves_list.append(Move(src=(r,c),dst=(t_row_2square,c))) #appends the list with possible move of moving 2 squares in front
        #Now checking diagonal capture: 
        #white captures in diagonal of -1,1 and -1, -1 where format is (row, column)
        #black captures in diagonal of 1,1 and 1, -1 where format is again (row, column)
        #so both move diagonally left and right therefore: 
        t_col1 = c - 1 
        t_col2 = c + 1
        #checking for left diagonal capture which is t_col1 
        #t_row is the ranking up of the pawn, where the pawn moves a square in front of it, and then decides to capture diagonally or not
        if in_bounds(t_row,t_col1): #not counting t_row_2square as it is only used to move 2 squares without any capture. Checks if the diagonal capture is within bounds or not. 
        #The process is similar for both the left and right sides. 
            t_square = board.grid[t_row][t_col1] #extracting the piece from the grid of the targeted square
            if t_square is not None and t_square.color != self.color: #checking if the grid has a piece(not empty)and also if it is of the opposite color
                if t_row == promotion_row: #checks if it has reached the row for promotion 
                    for promotion in ["n","b","r","q"]:
                        moves_list.append(Move(src=(r,c),dst=(t_row,t_col1),promotion=promotion,captured_piece=t_square)) #appends the possible promotional moves 
                else: 
                    moves_list.append(Move(src=(r,c),dst=(t_row,t_col1),captured_piece=t_square)) #else, just appends the current square, targetted square, and the possible captured piece 
        if in_bounds(t_row,t_col2): #follows the same path as for the same left direction. 
            t_square = board.grid[t_row][t_col2]
            if t_square is not None and t_square.color != self.color:
                if t_row == promotion_row: 
                    for promotion in ["n","b","r","q"]:
                        moves_list.append(Move(src=(r,c),dst=(t_row,t_col2),promotion=promotion, captured_piece=t_square))
                else: 
                    moves_list.append(Move(src=(r,c),dst=(t_row,t_col2),captured_piece=t_square))
        return moves_list
            




#Same template now for rest
class Knight(Piece):
    kind = "N"
    value = 320

    def pseudo_legal_moves(self, board: "Board", r: int, c: int) -> List[Move]:
        """
        Generate all pseudo-legal moves for a knight.

        Parameters:
            board: the current board object
            r: current row of the knight
            c: current column of the knight

        Output:
            A list of Move objects.

        Rules:
            - Knight moves in L-shapes:
                (±2, ±1) and (±1, ±2)
            - Knight can jump over pieces
            - If destination is empty → add move
            - If destination has enemy piece → add move
            - If destination has own piece → do NOT add
            - Must stay within board bounds

        Hint:
            Use a predefined list of 8 possible moves.
        """
        # TODO: Implement knight movement logic using step moves
        current_row=r #assigning current_row variable to current row parameter
        current_column=c #assinging current_column variable to current column parameter
        return self._step_moves(board,current_row,current_column,[(1,2),(2,1),(-1,2),(-2,1),(1,-2),(2,-1),(-1,-2),(-2,-1)]) #return step_moves as knight moves in specific squares like kings with parameters 
                                                                                                                             #current row, column and list of tules containing the possible squares it can move to.
        


class Bishop(Piece):
    kind = "B"
    value = 330

    def pseudo_legal_moves(self, board: "Board", r: int, c: int) -> List[Move]:
        return self._slide_moves(board, r, c, [(-1, -1), (-1, 1), (1, -1), (1, 1)])


class Rook(Piece):
    kind = "R"
    value = 500

    def pseudo_legal_moves(self, board: "Board", r: int, c: int) -> List[Move]:
        """
        Generate all pseudo-legal moves for a rook.

        Parameters:
            board: the current board object
            r: current row of the rook
            c: current column of the rook

        Output:
            A list of Move objects.

        Rules:
            - Rook moves in straight lines:
                 Up, Down, Left, Right
            - Must continue moving until blocked
            - Use sliding movement logic
            - Do not modify the board

        Hint:
            Call the sliding move helper with the correct directions.
        """
        # TODO: Implement rook movement using sliding moves
        return self._slide_moves(board,r,c,[ #call the _slide_moves() method to create list of moves 
            (-1,0),(1,0),(0,-1),(0,1) # input four directions for the rook to move
        ])





class Queen(Piece):
    kind = "Q"
    value = 900

    def pseudo_legal_moves(self, board: "Board", r: int, c: int) -> List[Move]:
        return self._slide_moves(board, r, c, [
            (-1, -1), (-1, 1), (1, -1), (1, 1),
            (-1, 0), (1, 0), (0, -1), (0, 1),
        ])


class King(Piece):
    kind = "K"
    value = 20000

    def pseudo_legal_moves(self, board: "Board", r: int, c: int) -> List[Move]:
        return self._step_moves(board, r, c, [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1),
        ])

#Maps piece symbol to class
PIECE_MAP = {
    "p": Pawn,
    "n": Knight,
    "b": Bishop,
    "r": Rook,
    "q": Queen,
    "k": King,
}

#Converts char from text board file into a piece object/None
def piece_from_symbol(ch: str) -> Optional[Piece]:
    if ch == ".":
        return None
    if len(ch) != 1 or ch.lower() not in PIECE_MAP:
        raise ValueError(f"Unknown piece symbol: {ch}")
    cls = PIECE_MAP[ch.lower()]
    color = "w" if ch.isupper() else "b"
    return cls(color)

#Other way round.
def symbol_from_piece(piece: Optional[Piece]) -> str:
    return "." if piece is None else piece.symbol
