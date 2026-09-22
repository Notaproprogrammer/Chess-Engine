from board import Board
from pieces import Move

def run_student1_audit():
    print("--- Starting Student 1 Logic Audit ---")
    b = Board()

    # 1. Test Coordinate Parsing & Legality
    # This checks if your try_parse_move() correctly rejects teleportation
    print("\n[1/3] Testing try_parse_move validation...")
    try:
        b.try_parse_move("e2e5") # Valid coordinates, but illegal move for a pawn
        print("FAIL: Illegal move e2e5 was accepted.")
    except ValueError as e:
        print(f"PASS: Caught illegal move. Error: {e}")

    # 2. Test Pawn Movement (Your pseudo_legal_moves logic)
    print("\n[2/3] Testing Pawn double-step and bounds...")
    moves = b.generate_pseudo_legal_moves()
    e2_moves = [m.uci() for m in moves if m.uci().startswith("e2")]
    if "e2e3" in e2_moves and "e2e4" in e2_moves:
        print("PASS: Pawn correctly identified 1-step and 2-step options.")
    else:
        print(f"FAIL: Pawn move generation issue. Found: {e2_moves}")

    # 3. Test Move Application & Undo (Your apply_move logic)
    print("\n[3/3] Testing Board Update & History...")
    original_state = b.position_key()
    move = b.try_parse_move("g1f3") # Knight move
    b.apply_move(move)
    
    if b.grid[5][5] is not None and b.grid[7][6] is None and b.turn == 'b':
        print("PASS: Board updated correctly and turn switched.")
    else:
        print("FAIL: Board state or turn not updated correctly.")

    b.undo_last()
    if b.position_key() == original_state:
        print("PASS: Undo restored the board perfectly.")
    else:
        print("FAIL: Undo failed to restore original state.")

if __name__ == "__main__":
    try:
        run_student1_audit()
        print("\nSUMMARY: Your core logic is looking solid!")
    except Exception as e:
        print(f"\nCRITICAL BUG DETECTED: {e}")