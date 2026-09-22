#Stores board, applies move, undo moves, check legal, serializez board state

from __future__ import annotations

from typing import List, Optional, Tuple

from pieces import (
    Bishop,
    King,
    Knight,
    Move,
    Pawn,
    Piece,
    Queen,
    Rook,
    in_bounds,
    parse_square,
    piece_from_symbol,
    symbol_from_piece,
)

Square = Tuple[int, int]


class Board:
    def __init__(self, setup: bool = True):
        self.grid: List[List[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]
        #create grid
        self.turn: str = "w" #White moves first
        self.history: List[Move] = []#Stores moves for undo and logging
        if setup:
            self.setup_start() #Initialize board

    @staticmethod
    def opposite(color: str) -> str:
        #Returns opposite side
        return "b" if color == "w" else "w"

    def setup_start(self) -> None:
        #Place piece in position
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        back_rank = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for c, cls in enumerate(back_rank):
            self.grid[7][c] = cls("w")
            self.grid[0][c] = cls("b")
        for c in range(8):
            self.grid[6][c] = Pawn("w")
            self.grid[1][c] = Pawn("b")
        self.turn = "w"
        self.history.clear()

    def clone(self) -> "Board":
        #Creates a deep copy of the board so changes to the copy do not affect the original.
        b = Board(setup=False)
        b.turn = self.turn
        b.grid = [[p.copy() if p is not None else None for p in row] for row in self.grid]
        return b

    def piece_at(self, r: int, c: int) -> Optional[Piece]:
        #Returns piece at square
        if not in_bounds(r, c):
            return None
        return self.grid[r][c]

    def king_pos(self, color: str) -> Optional[Square]:
        #Finds king for color
        for r in range(8):
            for c in range(8):
                p = self.grid[r][c]
                if p is not None and p.color == color and isinstance(p, King):
                    return (r, c)
        return None

    def square_attacked(self, r: int, c: int, by_color: str) -> bool:
        #Checkif square is attacked by color,
        #Loops through all pieces of color and checks whether any attached square matches
        for rr in range(8):
            for cc in range(8):
                p = self.grid[rr][cc]
                if p is None or p.color != by_color:
                    continue
                for ar, ac in p.attacks(self, rr, cc):
                    if (ar, ac) == (r, c):
                        return True
        return False

    def in_check(self, color: Optional[str] = None) -> bool:
        #Determine if color isin chechk
        if color is None:
            color = self.turn
        kpos = self.king_pos(color)
        if kpos is None:
            return False
        return self.square_attacked(kpos[0], kpos[1], self.opposite(color))

    def apply_move(self, move: Move) -> None:
        """
        Apply a move to the board.

        Parameters:
            move: a Move object containing start and end positions

        Output:
            None (the board is modified directly)

        Rules:
            - Move the piece from its start position to its end position
            - If a piece exists at the destination -> it is captured
            - The starting square must become empty
            - Update the board state correctly
            - Do not create a new board
            ● must store moved_piece, captured_piece, and previous turn in move
            ● must append move to history

        Hint:
            Access the piece using its starting position, then update both squares.
        """
        # TODO: Implement board update logic
        #let sr be starting row, sc be strtcolumn. let dr, be change in row, dc, be chane in column

        #unloading the tuple 
        sr, sc = move.src 
        dr, dc = move.dst 
        #current square is c_square, next square is n_square
        c_square = self.grid[sr][sc]
        n_square = self.grid[dr][dc]
        #storing the moved_piece, captured_piece, and previous turn for undo support
        move.moved_piece = c_square
        move.captured_piece = n_square
        move.prev_turn = self.turn 
        #Checking if pawn has reached the last rank or not
        if c_square is not None and c_square.kind == "P" and (dr == 0 or dr == 7): #checks if it is a pawn going to the last rank from either sides. If it is white then it would go to 
                                                          #r = 0 and if it is black it would go to 7. Checking for individual color is not necessary, as c_square.color handles that
                                                          #and as long as the pawn goes to the either ends, they woudl be promoted, and promoted piece would take the color of the current piece. 
                                                          #Also checks if the square is empty or not. 

            if move.promotion == "q":  #checks if promotion is queen
                new_piece = Queen(c_square.color) 
            elif move.promotion == "b":  #checks if promotion is bishop
                new_piece = Bishop(c_square.color) 
            elif move.promotion == "n": #checks if promotion is knight
                new_piece = Knight(c_square.color)
            elif move.promotion == "r": #checks if promotion is rook 
                new_piece = Rook(c_square.color)
            else: 
                new_piece = Queen(c_square.color) #if promotion is none or not defined, then the promotin is automatically queen
        else: 
            new_piece = c_square
           
        
        #Clearing the source square and placing the moving piece on the destination square
        self.grid[sr][sc]=None 
        self.grid[dr][dc]=new_piece

        #switching the side for the opposite color to play
        self.turn = self.opposite(self.turn)

        #appending the move history list:
        self.history.append(move)




    def undo_move(self, move: Move) -> None:
        #Restores moving piece to source, capture piece to dest, previous turn
        sr, sc = move.src
        dr, dc = move.dst
        if move.prev_turn is None:
            raise ValueError("Move does not contain undo information")
        self.turn = move.prev_turn
        self.grid[sr][sc] = move.moved_piece
        self.grid[dr][dc] = move.captured_piece
        if self.history and self.history[-1] == move:
            self.history.pop()

    def undo_last(self) -> Move:
        #Undo recent
        if not self.history:
            raise ValueError("No moves to undo")
        move = self.history[-1]
        self.undo_move(move)
        return move

    def generate_pseudo_legal_moves(self) -> List[Move]:
        """
        Generate all pseudo-legal moves for the current player.

        Parameters:
            None (uses the current board state)

        Output:
            A list of Move objects representing all possible moves.

        Rules:
            - Loop through all squares on the board
            - For each piece belonging to the current player:
                 Call its pseudo_legal_moves() function
            - Combine all moves into one list
            - Do not modify the board

        Hint:
            Check piece color before generating moves.
        """
        # TODO: Collect moves from all pieces
        pseudo_moves = []
        for r in range(8): # looping through the row
            for c in range(8): # looping through the columns for the specific row
                current_square = self.grid[r][c] #assigning the piece in that specific square to current_square
                if current_square is None or current_square.color != self.turn: #checking if the square is empty or 
                                                                                #if the piece belongs to the player who will play the next move(their turn).

                    continue
                else: 
                    pseudo_moves += current_square.pseudo_legal_moves(self, r,c) #We are not using.append as it will append 
                                                                                 #lists of Move objects instead of Move objects which we don't want. 
        return pseudo_moves #returns the list of pseudo legal moves

                

                    


                

    def generate_legal_moves(self) -> List[Move]:
        """
        Generate all legal moves for the current player.

        Parameters:
            None

        Output:
            A list of Move objects representing legal moves.

        Rules:
            - Start with pseudo-legal moves
            - For each move:
                 Apply the move temporarily
                 Check if the player is in check
                 If still in check → discard move
                 Otherwise → keep move
            - Undo the move after checking
            - Do not permanently modify the board

        Hint:
            Use apply_move() and undo functionality if available.
        """
        # TODO: Filter pseudo-legal moves into legal moves
        true_possible_move = []
        for move in self.generate_pseudo_legal_moves(): #loop over pseudo legal moves, each of the moves are a object
            self.apply_move(move) #apply the move
            if self.in_check(self.opposite(self.turn)): #check if the position of king is attacked by opposite color
                #note that after apply move, the turn changes, so the opposite color here means the opposite color before making the move
                self.undo_move(move)
                continue
            else: #go here if the king position is not attacked
                self.undo_move(move)
                true_possible_move.append(move) 
        return true_possible_move

        

    def is_game_over(self) -> bool:
        """
        Determine whether the game has ended.

        Parameters:
            None

        Output:
            True if the game is over, False otherwise.

        Rules:
            - Game is over if:
                 The current player has no legal moves
                
            - Do not modify the board

        Hint:
            Check if there are no legal moves
        """
        # TODO: Implement game-ending condition
        if len(self.generate_legal_moves()) == 0: #no moves possible means that the game is over
            # Either stalemate: no possible move and is not in check
            # Or checkmate: no possible move and is in check
            return True
        else: return False


    def result(self) -> str:

        """
        Return the result of the game.

        Parameters:
            None

        Output:
            ● "ongoing"
            ● "<opposite side> wins by checkmate"
            ● "draw by stalemate"

        Rules:
            
        - If no legal moves exist:
            If in check → opponent wins
            Otherwise → draw (stalemate)

        Hint:
            Use is_game_over() and in_check() to decide.
        """
        # TODO: Determine game result
        if self.is_game_over(): # 2 states of game over
            if self.in_check(): #1) Checkmate if one side is checked
                return "%s wins by checkmate"%(self.opposite(self.turn))
            else: #2) stalemate if the turn side is not checked
                return "draw by stalemate"
        else: return "ongoing" #If there are still posible moves, the game continues.


    def position_key(self) -> str:
        #Builds a string representation of the board plus side to move.
        rows = []
        for r in range(8):
            rows.append("".join(symbol_from_piece(p) for p in self.grid[r]))
        return f"{self.turn}|" + "/".join(rows)

    def to_text(self) -> str:
        #Serialize board to plain text
        lines = [f"turn {self.turn}"]
        for r in range(8):
            lines.append("".join(symbol_from_piece(p) for p in self.grid[r]))
        return "\n".join(lines) + "\n"

    @classmethod
    def from_text(cls, text: str) -> "Board":
        #Loads board from text
        lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")]
        if len(lines) < 9:
            raise ValueError("Position file must contain one turn line and 8 board lines")
        first = lines[0].split()
        if len(first) != 2 or first[0].lower() != "turn" or first[1] not in ("w", "b"):
            raise ValueError("First line must be 'turn w' or 'turn b'")
        board = cls(setup=False)
        board.turn = first[1]
        if len(lines[1:9]) != 8:
            raise ValueError("Board must have 8 rows")
        for r in range(8):
            row = lines[1 + r]
            if len(row) != 8:
                raise ValueError(f"Row {r+1} must have exactly 8 characters")
            for c, ch in enumerate(row):
                board.grid[r][c] = piece_from_symbol(ch)
        return board

    def __str__(self) -> str:
        #Create display
        out = []
        out.append("    a   b   c   d   e   f   g   h")
        out.append("  +---+---+---+---+---+---+---+---+")
        for r in range(8):
            rank = 8 - r
            cells = []
            for c in range(8):
                p = self.grid[r][c]
                cells.append(f" {symbol_from_piece(p)} ")
            out.append(f"{rank} |" + "|".join(cells) + f"| {rank}")
            out.append("  +---+---+---+---+---+---+---+---+")
        out.append("    a   b   c   d   e   f   g   h")
        out.append(f"Turn: {'White' if self.turn == 'w' else 'Black'}")
        if self.in_check(self.turn):
            out.append("Check!")
        return "\n".join(out)

    def try_parse_move(self, text: str) -> Move:
        """
        Convert a user input string into a Move object.

        Parameters:
            text: a string representing a move (e.g., "e2e4")

        Output:
            A Move object if valid, Raises an error if the input is invalid

        Rules:
            - Extract starting and ending positions from the string
            - Convert letters to columns (a=0, b=1, etc.)
            - Convert numbers to rows
            - Raise an error if input is invalid

        Hint:
            Carefully map chess notation to array indices.
        """
        # TODO: Parse input into move coordinates
        #splitting the coordinate string into two parts, the starting square, and the ending square. 
        #first checking if string length is equal to either 4 or not, if not raises an error
        string = text.strip().lower()
        string_len = len(string)
        if string_len != 4 and string_len !=5:
            raise ValueError("Invalid text length")
    #if the string length is 5, checks for the last value in the string, which is basically the promotional piece
        if len(string) == 5:
            promo_type = string[4]
            if promo_type not in ["q","r","b","n"]: #if it is not the appropriate letter for promotion, then it raises a value error
                raise ValueError("Promotional Piece is not defined")
            start_square = string[0:2] #splitting the string into two parts, coordinates for starting square, and end square, with 
                                       #the promotional piece set in another variable
            end_square = string[2:4]
        else:
            promo_type = None   #if the string is only 4 characters, promotional piece is None 
            start_square = string[0:2] #splitting into two parts 
            end_square = string[2:4]
        c_row, c_col = parse_square(start_square) #using the parse_square function to validate the coordinates as 
                                                  #well as return the coordinates of the squares to us
        e_row, e_col = parse_square(end_square)
        for legal_mv in self.generate_legal_moves(): #looping through the list of Move objects generated by generate legal moves
            if legal_mv.src == (c_row,c_col) and legal_mv.dst == (e_row,e_col): #checks if the coordinate belongs to the valid move list at first 
                if promo_type is None: # Now checks if the user has input any promotional piece character, if the user hasn't then promo_type is set to None 

                    if legal_mv.promotion is None or legal_mv.promotion =="q": # Now checks if the corresponding legal move has a direction for a promotional piece already or not or if its default by queen. 
                                                                               # It is used to check if both the user's promotion and the valid promotion are none or equal or not. 
                        return legal_mv #returns the legal move
                else:
                    if legal_mv.promotion == promo_type:#else, if the legal move's promotion matches with the promotion type the user inputs, then it returns the legal move with the promotion type 
                        return legal_mv 
        raise ValueError("Illegal move played") #If no moves are return, then raises a value error. 
                

    


        


    
        

    def play_move_text(self, text: str) -> Move:
        #Parse move, apply, return move
        move = self.try_parse_move(text)
        self.apply_move(move)
        return move
