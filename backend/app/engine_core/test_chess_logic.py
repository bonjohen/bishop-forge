"""
Unit tests for chess logic implementation.
"""

import numpy as np
from .engine_cpu import EngineCPU
from .chess_utils import (
    PIECE_NONE, PIECE_PAWN, PIECE_KNIGHT, PIECE_BISHOP,
    PIECE_ROOK, PIECE_QUEEN, PIECE_KING,
    COLOR_EMPTY, COLOR_WHITE, COLOR_BLACK
)


def create_empty_board():
    """Create an empty board."""
    piece_arr = np.zeros(64, dtype=np.int8)
    color_arr = np.full(64, COLOR_EMPTY, dtype=np.int8)
    return piece_arr, color_arr


def create_starting_position():
    """Create the standard chess starting position."""
    piece_arr = np.zeros(64, dtype=np.int8)
    color_arr = np.full(64, COLOR_EMPTY, dtype=np.int8)
    
    # White pieces (rank 0-1)
    piece_arr[0:8] = [PIECE_ROOK, PIECE_KNIGHT, PIECE_BISHOP, PIECE_QUEEN,
                      PIECE_KING, PIECE_BISHOP, PIECE_KNIGHT, PIECE_ROOK]
    color_arr[0:8] = COLOR_WHITE
    piece_arr[8:16] = PIECE_PAWN
    color_arr[8:16] = COLOR_WHITE
    
    # Black pieces (rank 6-7)
    piece_arr[48:56] = PIECE_PAWN
    color_arr[48:56] = COLOR_BLACK
    piece_arr[56:64] = [PIECE_ROOK, PIECE_KNIGHT, PIECE_BISHOP, PIECE_QUEEN,
                        PIECE_KING, PIECE_BISHOP, PIECE_KNIGHT, PIECE_ROOK]
    color_arr[56:64] = COLOR_BLACK
    
    return piece_arr, color_arr


def test_attack_maps_empty_board():
    """Test attack maps on empty board."""
    print("Test: Attack maps on empty board")
    piece_arr, color_arr = create_empty_board()
    
    white_att, black_att = EngineCPU.compute_attack_maps(piece_arr, color_arr)
    
    assert not white_att.any(), "Empty board should have no white attacks"
    assert not black_att.any(), "Empty board should have no black attacks"
    print("✓ Passed")


def test_attack_maps_single_knight():
    """Test attack maps with single knight on e4."""
    print("\nTest: Attack maps with knight on e4")
    piece_arr, color_arr = create_empty_board()
    
    # Place white knight on e4 (square 28)
    piece_arr[28] = PIECE_KNIGHT
    color_arr[28] = COLOR_WHITE
    
    white_att, black_att = EngineCPU.compute_attack_maps(piece_arr, color_arr)
    
    # Knight on e4 should attack 8 squares
    assert white_att.sum() == 8, f"Knight on e4 should attack 8 squares, got {white_att.sum()}"
    assert not black_att.any(), "No black pieces, so no black attacks"
    print(f"✓ Passed - Knight attacks {white_att.sum()} squares")


def test_attack_maps_rook():
    """Test attack maps with rook on a1."""
    print("\nTest: Attack maps with rook on a1")
    piece_arr, color_arr = create_empty_board()
    
    # Place white rook on a1 (square 0)
    piece_arr[0] = PIECE_ROOK
    color_arr[0] = COLOR_WHITE
    
    white_att, black_att = EngineCPU.compute_attack_maps(piece_arr, color_arr)
    
    # Rook on a1 should attack 14 squares (7 horizontal + 7 vertical)
    assert white_att.sum() == 14, f"Rook on a1 should attack 14 squares, got {white_att.sum()}"
    print(f"✓ Passed - Rook attacks {white_att.sum()} squares")


def test_evaluation_starting_position():
    """Test evaluation of starting position."""
    print("\nTest: Evaluation of starting position")
    piece_arr, color_arr = create_starting_position()
    
    white_off, white_def, black_off, black_def = EngineCPU.evaluate(piece_arr, color_arr)
    
    print(f"  White: offensive={white_off}, defensive={white_def}")
    print(f"  Black: offensive={black_off}, defensive={black_def}")
    
    # Starting position should be roughly balanced
    assert white_off > 0, "White should have positive offensive score"
    assert black_off > 0, "Black should have positive offensive score"
    assert abs(white_off - black_off) < 100, "Starting position should be balanced"
    print("✓ Passed - Position is balanced")


def test_move_generation_starting_position():
    """Test move generation from starting position."""
    print("\nTest: Move generation from starting position")
    piece_arr, color_arr = create_starting_position()
    
    # White to move
    moves = EngineCPU.generate_pseudo_legal_moves(piece_arr, color_arr, COLOR_WHITE)
    
    print(f"  Generated {len(moves)} moves for white")
    
    # Starting position has 20 legal moves for white
    assert len(moves) == 20, f"Starting position should have 20 moves, got {len(moves)}"
    print("✓ Passed - Correct number of moves")


def test_move_generation_knight():
    """Test move generation for knight."""
    print("\nTest: Move generation for knight on e4")
    piece_arr, color_arr = create_empty_board()
    
    # Place white knight on e4 (square 28)
    piece_arr[28] = PIECE_KNIGHT
    color_arr[28] = COLOR_WHITE
    
    moves = EngineCPU.generate_pseudo_legal_moves(piece_arr, color_arr, COLOR_WHITE)
    
    print(f"  Generated {len(moves)} moves for knight")
    
    # Knight on e4 should have 8 moves
    assert len(moves) == 8, f"Knight on e4 should have 8 moves, got {len(moves)}"
    print("✓ Passed - Correct number of knight moves")


def test_pawn_promotion():
    """Test pawn promotion moves."""
    print("\nTest: Pawn promotion")
    piece_arr, color_arr = create_empty_board()
    
    # Place white pawn on 7th rank (square 48 = a7)
    piece_arr[48] = PIECE_PAWN
    color_arr[48] = COLOR_WHITE
    
    moves = EngineCPU.generate_pseudo_legal_moves(piece_arr, color_arr, COLOR_WHITE)
    
    print(f"  Generated {len(moves)} promotion moves")
    
    # Pawn on 7th rank should have 4 promotion moves (N, B, R, Q)
    assert len(moves) == 4, f"Pawn on 7th rank should have 4 promotion moves, got {len(moves)}"
    print("✓ Passed - Correct number of promotion moves")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running Chess Logic Tests")
    print("=" * 60)
    
    test_attack_maps_empty_board()
    test_attack_maps_single_knight()
    test_attack_maps_rook()
    test_evaluation_starting_position()
    test_move_generation_starting_position()
    test_move_generation_knight()
    test_pawn_promotion()
    
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()

