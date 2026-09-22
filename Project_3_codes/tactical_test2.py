from board import Board
from pieces import Pawn, Knight, King, Move

def stress_test_student1():
    print("=== ECE 122 PROJECT 3: HARD MODE AUDIT (STUDENT 1) ===")
    
    # Setting up a complex board state
    # White Pawn at e7 (one step from promotion)
    # White Knight at d4 (surrounded by mixed pieces)
    # Black King at e8
    b = Board(setup=False)
    b.grid[1][4] = Pawn("w") # White pawn on e7 (array 1,4)
    b.grid[4][3] = Knight("w") # White knight on d4 (array 4,3)
    b.grid[0][4] = King("b") # Black king on e8 (array 0,4)
    b.turn = "w"

    # --- TEST 1: The Promotion Logic ---
    print("\n[1/4] Testing Promotion & Defaulting...")
    # This checks if your try_parse_move and apply_move handle promotion correctly [cite: 98, 99]
    try:
        # Testing explicit promotion to Knight
        move_n = b.try_parse_move("e7e8n")
        if move_n.promotion == 'n':
            print("PASS: Explicit Knight promotion parsed.") 
        
        # Testing DEFAULT promotion to Queen (e7e8 with no suffix)
        move_q = b.try_parse_move("e7e8")
        if move_q.promotion == 'q':
            print("PASS: Default Queen promotion handled.") 
        else:
            print(f"FAIL: Expected 'q' promotion, got '{move_q.promotion}'")
    except Exception as e:
        print(f"FAIL: Promotion parsing crashed: {e}")

    # --- TEST 2: Illegal Knight Teleportation ---
    print("\n[2/4] Testing Illegal Move Rejection...")
    # This checks if your try_parse_move calls generate_legal_moves() to block "teleporting" [cite: 134]
    try:
        b.try_parse_move("d4d8") # Valid squares, but illegal L-shape for Knight
        print("FAIL: Knight was allowed to teleport to d8!") 
    except ValueError:
        print("PASS: Illegal Knight teleport correctly rejected.") 

    # --- TEST 3: Captures and History ---
    print("\n[3/4] Testing Capture Data & Undo...")
    # White Knight at d4 captures nothing at d5 (e.g. d4d5 is illegal for knight)
    # Let's move Knight d4 to f5 (array 3,5) where we'll put a black piece
    b.grid[3][5] = Pawn("b")
    move_cap = b.try_parse_move("d4f5")
    b.apply_move(move_cap)
    
    # check if apply_move stored the capture [cite: 97]
    if move_cap.captured_piece is not None and move_cap.captured_piece.color == "b":
        print("PASS: Capture piece recorded in Move object.") 
    else:
        print("FAIL: Captured piece not recorded.")

    b.undo_last()
    if b.grid[4][3] is not None and b.grid[3][5].color == "b":
        print("PASS: Undo restored both the attacker and the victim.") 

    # --- TEST 4: Pawn Diagonal Rejection ---
    print("\n[4/4] Testing Pawn 'Ghost' Captures...")
    # A pawn cannot move diagonally to an empty square [cite: 139]
    try:
        # e7 is at (1,4), diagonal is (0,3) or (0,5). Both are empty.
        b.try_parse_move("e7d8") 
        print("FAIL: Pawn allowed to capture an empty square diagonally.") 
    except ValueError:
        print("PASS: Diagonal ghost capture rejected.")

if __name__ == "__main__":
    stress_test_student1()