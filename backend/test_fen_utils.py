"""
Test FEN conversion utilities.
"""

import numpy as np
from app.engine_core.fen_utils import (
    fen_to_arrays, arrays_to_fen, fen_to_board_2d, STARTING_FEN
)
from app.engine_core.chess_utils import (
    PIECE_PAWN, PIECE_KNIGHT, PIECE_ROOK, PIECE_KING,
    COLOR_WHITE, COLOR_BLACK
)


def test_starting_position():
    """Test conversion of starting position."""
    print("Test: Starting position FEN conversion")
    
    piece_arr, color_arr, stm = fen_to_arrays(STARTING_FEN)
    
    # Check white pieces
    assert piece_arr[0] == PIECE_ROOK, "a1 should be white rook"
    assert piece_arr[1] == PIECE_KNIGHT, "b1 should be white knight"
    assert piece_arr[4] == PIECE_KING, "e1 should be white king"
    assert color_arr[0] == COLOR_WHITE
    
    # Check white pawns
    for sq in range(8, 16):
        assert piece_arr[sq] == PIECE_PAWN, f"Square {sq} should be white pawn"
        assert color_arr[sq] == COLOR_WHITE
    
    # Check black pieces
    assert piece_arr[56] == PIECE_ROOK, "a8 should be black rook"
    assert piece_arr[60] == PIECE_KING, "e8 should be black king"
    assert color_arr[56] == COLOR_BLACK
    
    # Check side to move
    assert stm == COLOR_WHITE, "White should be to move"
    
    print("✓ Passed")


def test_round_trip():
    """Test FEN → arrays → FEN round trip."""
    print("\nTest: FEN round trip conversion")
    
    original_fen = STARTING_FEN
    
    # Convert to arrays
    piece_arr, color_arr, stm = fen_to_arrays(original_fen)
    
    # Convert back to FEN
    new_fen = arrays_to_fen(piece_arr, color_arr, stm)
    
    print(f"  Original: {original_fen}")
    print(f"  New:      {new_fen}")
    
    # Parse both FENs and compare positions
    piece_arr2, color_arr2, stm2 = fen_to_arrays(new_fen)
    
    assert np.array_equal(piece_arr, piece_arr2), "Piece arrays should match"
    assert np.array_equal(color_arr, color_arr2), "Color arrays should match"
    assert stm == stm2, "Side to move should match"
    
    print("✓ Passed")


def test_custom_position():
    """Test a custom position."""
    print("\nTest: Custom position")
    
    # Position after 1. e4
    fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
    
    piece_arr, color_arr, stm = fen_to_arrays(fen)
    
    # Check that e4 (square 28) has white pawn
    assert piece_arr[28] == PIECE_PAWN, "e4 should have pawn"
    assert color_arr[28] == COLOR_WHITE, "e4 pawn should be white"
    
    # Check that e2 (square 12) is empty
    assert piece_arr[12] == 0, "e2 should be empty"
    
    # Check side to move
    assert stm == COLOR_BLACK, "Black should be to move"
    
    print("✓ Passed")


def test_board_2d():
    """Test 2D board representation."""
    print("\nTest: 2D board representation")
    
    board = fen_to_board_2d(STARTING_FEN)
    
    # Check dimensions
    assert len(board) == 8, "Should have 8 ranks"
    assert all(len(row) == 8 for row in board), "Each rank should have 8 files"
    
    # Check first rank (rank 8 in chess notation)
    assert board[0][0] == 'r', "a8 should be black rook"
    assert board[0][4] == 'k', "e8 should be black king"
    
    # Check last rank (rank 1 in chess notation)
    assert board[7][0] == 'R', "a1 should be white rook"
    assert board[7][4] == 'K', "e1 should be white king"
    
    # Check pawns
    assert all(board[1][i] == 'p' for i in range(8)), "Rank 7 should have black pawns"
    assert all(board[6][i] == 'P' for i in range(8)), "Rank 2 should have white pawns"
    
    # Check empty squares
    assert all(board[3][i] is None for i in range(8)), "Rank 5 should be empty"
    
    print("✓ Passed")


def test_empty_board():
    """Test empty board."""
    print("\nTest: Empty board")
    
    fen = "8/8/8/8/8/8/8/8 w - - 0 1"
    
    piece_arr, color_arr, stm = fen_to_arrays(fen)
    
    # All squares should be empty
    assert np.all(piece_arr == 0), "All squares should be empty"
    assert np.all(color_arr == -1), "All colors should be empty"
    
    print("✓ Passed")


def run_all_tests():
    """Run all FEN utility tests."""
    print("=" * 60)
    print("Running FEN Utility Tests")
    print("=" * 60)
    
    test_starting_position()
    test_round_trip()
    test_custom_position()
    test_board_2d()
    test_empty_board()
    
    print("\n" + "=" * 60)
    print("All FEN utility tests passed! ✓")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()

