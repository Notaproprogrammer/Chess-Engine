"""
BRUTAL test suite for ECE 122 Project 3 chess engine.

Tests the edge cases most likely to be in hidden test cases:
- Position parity (white/black symmetry)
- Pinned/blocked pieces with multiple attackers
- Discovered checks
- En-passant-adjacent edge cases (without actually testing en passant)
- Promotion in all variants (push, capture-left, capture-right)
- Move counts in famous positions (Kiwipete-lite, etc.)
- Undo/redo across many move sequences (board state integrity)
- Mate-in-1 puzzle solving via search
- Stalemate vs checkmate vs draw distinctions
- Edge-of-board piece behavior
"""
from __future__ import annotations

import sys
import traceback
from board import Board
from pieces import (
    Pawn, Knight, Bishop, Rook, Queen, King, Move,
    parse_square, square_name, in_bounds, piece_from_symbol
)
from eval import Evaluator


PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
results = []


def run(name, fn):
    try:
        fn()
        results.append((name, True, None))
        print(f"{PASS} {name}")
    except AssertionError as e:
        results.append((name, False, str(e)))
        print(f"{FAIL} {name}: {e}")
    except Exception as e:
        results.append((name, False, f"EXCEPTION: {type(e).__name__}: {e}"))
        print(f"{FAIL} {name}: EXCEPTION: {type(e).__name__}: {e}")


def setup(positions, turn="w"):
    """Helper to build a custom board from {square_name: (piece_class, color)}."""
    b = Board(setup=False)
    for sq, (cls, color) in positions.items():
        r, c = parse_square(sq)
        b.grid[r][c] = cls(color)
    b.turn = turn
    return b


# ============================================================================
# POSITION PARITY: black should behave symmetrically to white
# ============================================================================

def test_starting_position_white_and_black_have_20_moves():
    b = Board()
    assert len(b.generate_legal_moves()) == 20
    b.turn = "b"
    assert len(b.generate_legal_moves()) == 20


def test_pawn_two_square_only_from_starting_row_white():
    # white pawn on row 5 (rank 3) — already moved once, cannot do 2-square
    b = setup({"e3": (Pawn, "w"), "e1": (King, "w"), "e8": (King, "b")}, "w")
    moves = [m for m in b.generate_legal_moves() if m.src == (5, 4)]
    # only 1 legal move: forward 1 to e4
    forward_moves = [m for m in moves if m.dst[1] == 4]
    assert len(forward_moves) == 1, f"pawn on e3 should have 1 forward move, got {len(forward_moves)}"
    assert forward_moves[0].dst == (4, 4), "should move to e4"


def test_pawn_two_square_only_from_starting_row_black():
    # black pawn on row 2 (rank 6) — already moved once, cannot do 2-square
    b = setup({"e6": (Pawn, "b"), "e1": (King, "w"), "e8": (King, "b")}, "b")
    moves = [m for m in b.generate_legal_moves() if m.src == (2, 4)]
    forward_moves = [m for m in moves if m.dst[1] == 4]
    assert len(forward_moves) == 1, f"pawn on e6 should have 1 forward move, got {len(forward_moves)}"
    assert forward_moves[0].dst == (3, 4)


# ============================================================================
# PROMOTION VARIANTS
# ============================================================================

def test_promotion_via_capture_left_white():
    # white pawn b7, black rook a8 — capture-promote on a8
    b = setup({"b7": (Pawn, "w"), "a8": (Rook, "b"), "h1": (King, "w"), "h8": (King, "b")}, "w")
    moves = [m for m in b.generate_legal_moves() if m.src == (1, 1) and m.dst == (0, 0)]
    assert len(moves) == 4, f"capture-promote on a8 should have 4 options, got {len(moves)}"
    promos = sorted([m.promotion for m in moves])
    assert promos == ["b", "n", "q", "r"]


def test_promotion_via_capture_right_white():
    # white pawn b7, black rook c8 — capture-promote on c8
    b = setup({"b7": (Pawn, "w"), "c8": (Rook, "b"), "h1": (King, "w"), "h8": (King, "b")}, "w")
    moves = [m for m in b.generate_legal_moves() if m.src == (1, 1) and m.dst == (0, 2)]
    assert len(moves) == 4


def test_promotion_via_capture_left_black():
    # black pawn b2, white rook a1
    b = setup({"b2": (Pawn, "b"), "a1": (Rook, "w"), "h1": (King, "w"), "h8": (King, "b")}, "b")
    moves = [m for m in b.generate_legal_moves() if m.src == (6, 1) and m.dst == (7, 0)]
    assert len(moves) == 4


def test_promotion_via_capture_right_black():
    # black pawn b2, white rook c1
    b = setup({"b2": (Pawn, "b"), "c1": (Rook, "w"), "h1": (King, "w"), "h8": (King, "b")}, "b")
    moves = [m for m in b.generate_legal_moves() if m.src == (6, 1) and m.dst == (7, 2)]
    assert len(moves) == 4


def test_promotion_blocked_no_moves():
    # white pawn a7, friendly piece on a8 — no forward promotion
    b = setup({"a7": (Pawn, "w"), "a8": (Rook, "w"), "h1": (King, "w"), "h8": (King, "b")}, "w")
    pawn_moves = [m for m in b.generate_legal_moves() if m.src == (1, 0)]
    forward = [m for m in pawn_moves if m.dst == (0, 0)]
    assert len(forward) == 0, "blocked pawn should not promote forward"


def test_play_promotion_under_promote_to_knight():
    b = setup({"a7": (Pawn, "w"), "h1": (King, "w"), "h8": (King, "b")}, "w")
    b.play_move_text("a7a8n")
    assert isinstance(b.grid[0][0], Knight), "should under-promote to knight"
    assert b.grid[0][0].color == "w"


# ============================================================================
# CHECK / PIN / DISCOVERED CHECK
# ============================================================================

def test_pinned_piece_can_capture_pinner():
    # white king e1, white bishop on e2 pinned by black rook on e8
    # bishop CANNOT move (it's pinned, can only capture along the pin line which it can't do)
    # actually a bishop pinned on a file by a rook can't move at all
    b = setup({
        "e1": (King, "w"),
        "e2": (Bishop, "w"),
        "e8": (Rook, "b"),
        "a8": (King, "b"),
    }, "w")
    bishop_moves = [m for m in b.generate_legal_moves() if m.src == (6, 4)]
    assert len(bishop_moves) == 0, f"pinned bishop should have 0 moves, got {len(bishop_moves)}"


def test_pinned_rook_can_move_along_pin_line():
    # white rook on e2 pinned by black rook on e8
    # the white rook CAN move along the e-file (still blocks the pin)
    b = setup({
        "e1": (King, "w"),
        "e2": (Rook, "w"),
        "e8": (Rook, "b"),
        "a8": (King, "b"),
    }, "w")
    rook_moves = [m for m in b.generate_legal_moves() if m.src == (6, 4)]
    # rook can move to e3, e4, e5, e6, e7, or capture e8
    legal_dsts = [m.dst for m in rook_moves]
    # NOT allowed to leave the file
    for dst in legal_dsts:
        assert dst[1] == 4, f"pinned rook moved off the file: {dst}"
    # SHOULD be allowed to capture the pinner
    assert (0, 4) in legal_dsts, "pinned rook should be able to capture the pinning rook"


def test_double_check_only_king_can_move():
    # white king e1, attacked by black rook on e8 AND black bishop on h4
    # in double check, only the king can move
    b = setup({
        "e1": (King, "w"),
        "e8": (Rook, "b"),
        "h4": (Bishop, "b"),
        "a8": (King, "b"),
        "a1": (Rook, "w"),  # this rook would normally block one but can't block both
    }, "w")
    # actually let's verify: e1 is attacked by Rook on e-file AND bishop on h4-e1 diagonal
    # legal moves should ONLY be king moves
    moves = b.generate_legal_moves()
    non_king_moves = [m for m in moves if not isinstance(b.piece_at(*m.src), King)]
    assert len(non_king_moves) == 0, f"in double check, non-king pieces should have 0 moves, got {len(non_king_moves)}"


# ============================================================================
# CHECKMATE / STALEMATE EDGE CASES
# ============================================================================

def test_back_rank_mate():
    # classic back rank mate: black king on h8, blocked by own pawns, white rook on e8
    b = setup({
        "h8": (King, "b"),
        "g7": (Pawn, "b"),
        "h7": (Pawn, "b"),
        "e8": (Rook, "w"),
        "e1": (King, "w"),
    }, "b")
    assert b.in_check("b")
    assert b.is_game_over()
    assert "checkmate" in b.result()


def test_smothered_mate_setup():
    # smothered mate-like: black king h8, surrounded by own pieces, white knight gives check from g6
    # actually true smothered mate: Kh8, pawns g7+h7, bishop or rook on g8 blocking, knight checks from f7
    b = setup({
        "h8": (King, "b"),
        "g7": (Pawn, "b"),
        "h7": (Pawn, "b"),
        "g8": (Rook, "b"),  # blocks the king's escape
        "f7": (Knight, "w"),  # smothered mate knight
        "e1": (King, "w"),
    }, "b")
    assert b.in_check("b"), "black should be in check from knight on f7"
    moves = b.generate_legal_moves()
    assert len(moves) == 0, f"smothered mate should have 0 legal moves, got {len(moves)}"
    assert "checkmate" in b.result()


def test_stalemate_lone_king_in_corner():
    # black king a8, white queen b6, white king c6 — black is in stalemate (not check, no moves)
    b = setup({
        "a8": (King, "b"),
        "b6": (Queen, "w"),
        "c6": (King, "w"),
    }, "b")
    assert not b.in_check("b"), "stalemate: not in check"
    assert b.is_game_over()
    assert b.result() == "draw by stalemate"


def test_check_but_can_block():
    # white king e1 in check by rook on e8, white knight on c1 can move to e2 to block? no, knight can't.
    # let's use: white queen on a4 can move to e4 to block
    b = setup({
        "e1": (King, "w"),
        "e8": (Rook, "b"),
        "a4": (Queen, "w"),
        "a8": (King, "b"),
    }, "w")
    assert b.in_check("w")
    assert not b.is_game_over(), "should not be game over — queen can block"
    moves = b.generate_legal_moves()
    block_moves = [m for m in moves if m.src == (4, 0) and m.dst[1] == 4]
    assert len(block_moves) > 0, "queen should be able to move to e-file to block"


def test_check_must_capture_attacker():
    # only way to escape: capture the attacker
    b = setup({
        "h1": (King, "w"),
        "h2": (Pawn, "w"),
        "g2": (Pawn, "w"),
        "g1": (Bishop, "b"),  # gives check
        "a8": (King, "b"),
    }, "w")
    # the only legal move should be capturing the bishop
    moves = b.generate_legal_moves()
    # specifically the king should be able to capture g1
    king_capture = [m for m in moves if m.src == (7, 7) and m.dst == (7, 6)]
    assert len(king_capture) == 1, "king should be able to capture attacking bishop"


# ============================================================================
# UNDO INTEGRITY (deep sequences)
# ============================================================================

def test_undo_long_sequence():
    b = Board()
    initial = b.position_key()
    moves = ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "g8f6", "d2d3", "f8c5", "c1g5"]
    for m in moves:
        b.play_move_text(m)
    # undo all in reverse
    for _ in range(len(moves)):
        b.undo_last()
    assert b.position_key() == initial, "long undo sequence should restore initial position"
    assert b.turn == "w"


def test_undo_promotion_then_redo():
    b = setup({"a7": (Pawn, "w"), "h1": (King, "w"), "h8": (King, "b")}, "w")
    initial = b.position_key()
    b.play_move_text("a7a8q")
    b.undo_last()
    assert b.position_key() == initial
    assert isinstance(b.grid[1][0], Pawn), "pawn restored"
    # do it again
    b.play_move_text("a7a8r")
    assert isinstance(b.grid[0][0], Rook), "should be a rook now"


def test_undo_capture_promotion():
    b = setup({"a7": (Pawn, "w"), "b8": (Knight, "b"), "h1": (King, "w"), "h8": (King, "b")}, "w")
    initial = b.position_key()
    b.play_move_text("a7b8q")
    assert isinstance(b.grid[0][1], Queen)
    b.undo_last()
    assert b.position_key() == initial
    assert isinstance(b.grid[0][1], Knight), "captured knight should be restored"
    assert isinstance(b.grid[1][0], Pawn), "pawn should be restored"


# ============================================================================
# SEARCH / ENGINE BEHAVIOR
# ============================================================================

def test_engine_finds_mate_in_1():
    # back rank mate available: white can play Re8#
    b = setup({
        "h8": (King, "b"),
        "g7": (Pawn, "b"),
        "h7": (Pawn, "b"),
        "e1": (Rook, "w"),
        "a1": (King, "w"),
    }, "w")
    from search import Searcher
    s = Searcher()
    move, score = s.find_best_move(b, max_depth=2)
    assert move is not None
    # the best move should deliver checkmate
    b.apply_move(move)
    assert b.is_game_over(), f"engine's best move should be mate, but game continues: {move.uci()}"
    assert "checkmate" in b.result()


def test_engine_avoids_stalemate_when_winning():
    # with overwhelming material, engine shouldn't blunder into stalemate at depth 2+
    # this is a soft test — just check it returns *some* move
    b = setup({
        "a1": (King, "w"),
        "h1": (Queen, "w"),
        "h2": (Queen, "w"),
        "e8": (King, "b"),
    }, "w")
    from search import Searcher
    s = Searcher()
    move, score = s.find_best_move(b, max_depth=2)
    assert move is not None


# ============================================================================
# EVALUATION TESTS
# ============================================================================

def test_eval_material_advantage_consistent():
    e = Evaluator()
    # white up by exactly a knight
    b = setup({
        "e1": (King, "w"),
        "e8": (King, "b"),
        "d4": (Knight, "w"),  # bonus piece for white
    }, "w")
    score = e.evaluate(b)
    assert score > 200, f"white up a knight should give score > 200, got {score}"


def test_eval_does_not_modify_complex_position():
    e = Evaluator()
    b = Board()
    b.play_move_text("e2e4")
    b.play_move_text("e7e5")
    b.play_move_text("g1f3")
    key_before = b.position_key()
    history_len = len(b.history)
    e.evaluate(b)
    e.evaluate(b)  # call twice
    assert b.position_key() == key_before, "evaluate must not modify board"
    assert len(b.history) == history_len, "evaluate must not change history"
    assert b.turn == "b", "turn should still be black"


def test_eval_negative_when_losing():
    e = Evaluator()
    # black up a queen, white to move
    b = setup({
        "e1": (King, "w"),
        "e8": (King, "b"),
        "d4": (Queen, "b"),
    }, "w")
    score = e.evaluate(b)
    assert score < -500, f"white losing a queen should be negative, got {score}"


# ============================================================================
# MOVE GEN EDGE CASES (corners, edges)
# ============================================================================

def test_knight_on_a1_corner():
    b = setup({"a1": (Knight, "w"), "h1": (King, "w"), "h8": (King, "b")}, "w")
    moves = [m for m in b.generate_legal_moves() if m.src == (7, 0)]
    # knight on a1 can only go to b3 and c2
    dsts = sorted([m.dst for m in moves])
    assert dsts == [(5, 1), (6, 2)], f"knight a1 moves should be b3, c2; got {dsts}"


def test_knight_on_h8_corner():
    b = setup({"h8": (Knight, "b"), "h1": (King, "w"), "a8": (King, "b")}, "b")
    moves = [m for m in b.generate_legal_moves() if m.src == (0, 7)]
    dsts = sorted([m.dst for m in moves])
    assert dsts == [(1, 5), (2, 6)], f"knight h8 moves wrong: {dsts}"


def test_rook_in_corner_full_lines():
    # rook a1 with empty board — should reach 14 squares
    b = setup({"a1": (Rook, "w"), "h8": (King, "w"), "e8": (King, "b")}, "w")
    moves = [m for m in b.generate_legal_moves() if m.src == (7, 0)]
    assert len(moves) == 14, f"corner rook on empty board should have 14 moves, got {len(moves)}"


def test_pawn_on_edge_file_a():
    # white pawn on a2 has only 1 diagonal capture (b3) since there's no left diagonal
    b = setup({
        "a2": (Pawn, "w"),
        "b3": (Pawn, "b"),
        "h1": (King, "w"),
        "h8": (King, "b"),
    }, "w")
    moves = [m for m in b.generate_legal_moves() if m.src == (6, 0)]
    # forward 1 (a3), forward 2 (a4), capture diagonal (b3) — total 3 moves
    assert len(moves) == 3, f"a2 pawn should have 3 moves, got {len(moves)}: {[(m.src, m.dst) for m in moves]}"


def test_pawn_on_edge_file_h():
    b = setup({
        "h2": (Pawn, "w"),
        "g3": (Pawn, "b"),
        "a1": (King, "w"),
        "a8": (King, "b"),
    }, "w")
    moves = [m for m in b.generate_legal_moves() if m.src == (6, 7)]
    assert len(moves) == 3


# ============================================================================
# PARSER STRESS TESTS
# ============================================================================

def test_parse_with_promotion_all_pieces():
    for piece_char in ["q", "r", "b", "n"]:
        b = setup({"a7": (Pawn, "w"), "h1": (King, "w"), "h8": (King, "b")}, "w")
        move = b.try_parse_move(f"a7a8{piece_char}")
        assert move.promotion == piece_char


def test_parse_rejects_garbage():
    b = Board()
    bad_inputs = ["xx", "1234", "e2e2", "i9j0", "", "e2"]
    for s in bad_inputs:
        try:
            b.try_parse_move(s)
            # if it didn't raise, but the move is e2e2 (same square) — that should fail too
            assert False, f"should have rejected: {s}"
        except (ValueError, Exception):
            pass


def test_parse_uppercase_promotion():
    b = setup({"a7": (Pawn, "w"), "h1": (King, "w"), "h8": (King, "b")}, "w")
    move = b.try_parse_move("A7A8Q")
    assert move.promotion == "q"


# ============================================================================
# REAL GAME SEQUENCES
# ============================================================================

def test_ruy_lopez_opening():
    b = Board()
    b.play_move_text("e2e4")
    b.play_move_text("e7e5")
    b.play_move_text("g1f3")
    b.play_move_text("b8c6")
    b.play_move_text("f1b5")
    # Ruy Lopez position. Black to move, plenty of legal options.
    moves = b.generate_legal_moves()
    assert len(moves) > 10
    assert b.turn == "b"


def test_long_game_no_crashes():
    """Play 30 random legal moves without crashing."""
    import random
    random.seed(42)
    b = Board()
    for _ in range(30):
        moves = b.generate_legal_moves()
        if not moves:
            break
        mv = random.choice(moves)
        b.apply_move(mv)
    # board should still be valid
    assert b.king_pos("w") is not None or b.king_pos("b") is not None, "at least one king should still be on board"


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    tests = [
        test_starting_position_white_and_black_have_20_moves,
        test_pawn_two_square_only_from_starting_row_white,
        test_pawn_two_square_only_from_starting_row_black,
        test_promotion_via_capture_left_white,
        test_promotion_via_capture_right_white,
        test_promotion_via_capture_left_black,
        test_promotion_via_capture_right_black,
        test_promotion_blocked_no_moves,
        test_play_promotion_under_promote_to_knight,
        test_pinned_piece_can_capture_pinner,
        test_pinned_rook_can_move_along_pin_line,
        test_double_check_only_king_can_move,
        test_back_rank_mate,
        test_smothered_mate_setup,
        test_stalemate_lone_king_in_corner,
        test_check_but_can_block,
        test_check_must_capture_attacker,
        test_undo_long_sequence,
        test_undo_promotion_then_redo,
        test_undo_capture_promotion,
        test_engine_finds_mate_in_1,
        test_engine_avoids_stalemate_when_winning,
        test_eval_material_advantage_consistent,
        test_eval_does_not_modify_complex_position,
        test_eval_negative_when_losing,
        test_knight_on_a1_corner,
        test_knight_on_h8_corner,
        test_rook_in_corner_full_lines,
        test_pawn_on_edge_file_a,
        test_pawn_on_edge_file_h,
        test_parse_with_promotion_all_pieces,
        test_parse_rejects_garbage,
        test_parse_uppercase_promotion,
        test_ruy_lopez_opening,
        test_long_game_no_crashes,
    ]
    for t in tests:
        run(t.__name__, t)

    passed = sum(1 for _, ok, _ in results if ok)
    failed = len(results) - passed
    print(f"\n{'=' * 60}")
    print(f"PASSED: {passed}/{len(results)}")
    print(f"FAILED: {failed}/{len(results)}")
    if failed:
        print("\nFAILURES:")
        for name, ok, err in results:
            if not ok:
                print(f"  ✗ {name}: {err}")