"""
Integration test for the public engine API.
"""

import numpy as np
from app import engine
from app.engine_core.chess_utils import (
    PIECE_NONE, PIECE_PAWN, PIECE_KNIGHT, PIECE_BISHOP,
    PIECE_ROOK, PIECE_QUEEN, PIECE_KING,
    COLOR_EMPTY, COLOR_WHITE, COLOR_BLACK
)


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


def test_backend_name():
    """Test backend name reporting."""
    print("Test: Backend name")
    name = engine.backend_name()
    print(f"  Backend: {name}")
    assert name in ["CPU (NumPy + Numba)", "GPU (CuPy)"]
    print("✓ Passed")


def test_evaluate_position_single():
    """Test single position evaluation."""
    print("\nTest: Single position evaluation")
    piece_arr, color_arr = create_starting_position()
    
    result = engine.evaluate_position_single(piece_arr, color_arr)
    
    print(f"  White: offensive={result.white_off}, defensive={result.white_def}")
    print(f"  Black: offensive={result.black_off}, defensive={result.black_def}")
    
    assert result.white_off > 0
    assert result.black_off > 0
    assert abs(result.white_off - result.black_off) < 100
    print("✓ Passed")


def test_evaluate_position_batch():
    """Test batch position evaluation."""
    print("\nTest: Batch position evaluation")
    piece_arr, color_arr = create_starting_position()
    
    # Create batch of 3 identical positions
    piece_batch = np.stack([piece_arr] * 3)
    color_batch = np.stack([color_arr] * 3)
    
    result = engine.evaluate_position_batch(piece_batch, color_batch)
    
    print(f"  Batch size: {len(result.white_off)}")
    print(f"  White offensive: {result.white_off}")
    print(f"  Black offensive: {result.black_off}")
    
    assert result.white_off.shape == (3,)
    assert result.black_off.shape == (3,)
    # All positions are identical, so scores should be the same
    assert np.all(result.white_off == result.white_off[0])
    assert np.all(result.black_off == result.black_off[0])
    print("✓ Passed")


def test_attack_maps_single():
    """Test single position attack maps."""
    print("\nTest: Single position attack maps")
    piece_arr, color_arr = create_starting_position()
    
    white_att, black_att = engine.attack_maps_single(piece_arr, color_arr)
    
    print(f"  White attacks: {white_att.sum()} squares")
    print(f"  Black attacks: {black_att.sum()} squares")
    
    assert white_att.shape == (64,)
    assert black_att.shape == (64,)
    assert white_att.sum() > 0
    assert black_att.sum() > 0
    print("✓ Passed")


def test_attack_maps_batch():
    """Test batch attack maps."""
    print("\nTest: Batch attack maps")
    piece_arr, color_arr = create_starting_position()
    
    # Create batch of 2 positions
    piece_batch = np.stack([piece_arr] * 2)
    color_batch = np.stack([color_arr] * 2)
    
    white_att, black_att = engine.attack_maps_batch(piece_batch, color_batch)
    
    print(f"  Batch shape: {white_att.shape}")
    
    assert white_att.shape == (2, 64)
    assert black_att.shape == (2, 64)
    print("✓ Passed")


def test_generate_moves_single():
    """Test single position move generation."""
    print("\nTest: Single position move generation")
    piece_arr, color_arr = create_starting_position()
    
    moves = engine.generate_moves_single(piece_arr, color_arr, COLOR_WHITE)
    
    print(f"  Generated {len(moves)} moves")
    
    assert len(moves) == 20
    # Check move structure
    assert all(hasattr(m, 'from_sq') for m in moves)
    assert all(hasattr(m, 'to_sq') for m in moves)
    assert all(hasattr(m, 'promo') for m in moves)
    assert all(hasattr(m, 'flags') for m in moves)
    print("✓ Passed")


def test_generate_moves_batch():
    """Test batch move generation."""
    print("\nTest: Batch move generation")
    piece_arr, color_arr = create_starting_position()
    
    # Create batch of 2 positions
    piece_batch = np.stack([piece_arr] * 2)
    color_batch = np.stack([color_arr] * 2)
    stm_batch = np.array([COLOR_WHITE, COLOR_WHITE], dtype=np.int8)
    
    moves = engine.generate_moves_batch(piece_batch, color_batch, stm_batch)
    
    print(f"  Generated {len(moves)} total moves")
    
    # Should be 40 moves total (20 per position)
    assert len(moves) == 40
    # Check that moves have board_idx
    assert all(hasattr(m, 'board_idx') for m in moves)
    print("✓ Passed")


def run_all_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("Running Engine Integration Tests")
    print("=" * 60)
    
    test_backend_name()
    test_evaluate_position_single()
    test_evaluate_position_batch()
    test_attack_maps_single()
    test_attack_maps_batch()
    test_generate_moves_single()
    test_generate_moves_batch()
    
    print("\n" + "=" * 60)
    print("All integration tests passed! ✓")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()

