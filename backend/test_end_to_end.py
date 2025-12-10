"""
End-to-end test: FEN → Engine → Results
"""

from app import engine
from app.engine_core.fen_utils import fen_to_arrays, STARTING_FEN


def test_starting_position_analysis():
    """Analyze the starting position."""
    print("Test: Starting position analysis")
    print("=" * 60)
    
    piece_arr, color_arr, stm = fen_to_arrays(STARTING_FEN)
    
    # Evaluate position
    eval_result = engine.evaluate_position_single(piece_arr, color_arr)
    print(f"\nEvaluation:")
    print(f"  White: offensive={eval_result.white_off}, defensive={eval_result.white_def}")
    print(f"  Black: offensive={eval_result.black_off}, defensive={eval_result.black_def}")
    print(f"  Balance: {eval_result.white_off - eval_result.black_off}")
    
    # Generate moves
    moves = engine.generate_moves_single(piece_arr, color_arr, stm)
    print(f"\nMove Generation:")
    print(f"  Total moves: {len(moves)}")
    print(f"  First 5 moves:")
    for i, move in enumerate(moves[:5]):
        from_sq = move.from_sq
        to_sq = move.to_sq
        from_file = chr(ord('a') + (from_sq % 8))
        from_rank = (from_sq // 8) + 1
        to_file = chr(ord('a') + (to_sq % 8))
        to_rank = (to_sq // 8) + 1
        print(f"    {i+1}. {from_file}{from_rank}{to_file}{to_rank}")
    
    # Attack maps
    white_att, black_att = engine.attack_maps_single(piece_arr, color_arr)
    print(f"\nAttack Maps:")
    print(f"  White attacks: {white_att.sum()} squares")
    print(f"  Black attacks: {black_att.sum()} squares")
    
    print("\n✓ Starting position analyzed successfully")


def test_position_after_e4():
    """Analyze position after 1. e4."""
    print("\n" + "=" * 60)
    print("Test: Position after 1. e4")
    print("=" * 60)
    
    fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
    piece_arr, color_arr, stm = fen_to_arrays(fen)
    
    # Evaluate
    eval_result = engine.evaluate_position_single(piece_arr, color_arr)
    print(f"\nEvaluation:")
    print(f"  White: offensive={eval_result.white_off}, defensive={eval_result.white_def}")
    print(f"  Black: offensive={eval_result.black_off}, defensive={eval_result.black_def}")
    print(f"  Balance: {eval_result.white_off - eval_result.black_off}")
    
    # Generate moves for black
    moves = engine.generate_moves_single(piece_arr, color_arr, stm)
    print(f"\nBlack has {len(moves)} legal moves")
    
    print("\n✓ Position after e4 analyzed successfully")


def test_endgame_position():
    """Analyze a simple endgame position."""
    print("\n" + "=" * 60)
    print("Test: King and pawn endgame")
    print("=" * 60)
    
    # White: King on e1, Pawn on e2
    # Black: King on e8
    fen = "4k3/8/8/8/8/8/4P3/4K3 w - - 0 1"
    piece_arr, color_arr, stm = fen_to_arrays(fen)
    
    # Evaluate
    eval_result = engine.evaluate_position_single(piece_arr, color_arr)
    print(f"\nEvaluation:")
    print(f"  White: offensive={eval_result.white_off}, defensive={eval_result.white_def}")
    print(f"  Black: offensive={eval_result.black_off}, defensive={eval_result.black_def}")
    print(f"  Material advantage: {eval_result.white_off - eval_result.black_off}")
    
    # Generate moves
    moves = engine.generate_moves_single(piece_arr, color_arr, stm)
    print(f"\nWhite has {len(moves)} legal moves")
    
    # Attack maps
    white_att, black_att = engine.attack_maps_single(piece_arr, color_arr)
    print(f"\nAttack Maps:")
    print(f"  White attacks: {white_att.sum()} squares")
    print(f"  Black attacks: {black_att.sum()} squares")
    
    print("\n✓ Endgame position analyzed successfully")


def test_tactical_position():
    """Analyze a tactical position with pieces."""
    print("\n" + "=" * 60)
    print("Test: Tactical position")
    print("=" * 60)
    
    # Position with knights and bishops
    fen = "rnbqkb1r/pppp1ppp/5n2/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 4 3"
    piece_arr, color_arr, stm = fen_to_arrays(fen)
    
    # Evaluate
    eval_result = engine.evaluate_position_single(piece_arr, color_arr)
    print(f"\nEvaluation:")
    print(f"  White: offensive={eval_result.white_off}, defensive={eval_result.white_def}")
    print(f"  Black: offensive={eval_result.black_off}, defensive={eval_result.black_def}")
    print(f"  Balance: {eval_result.white_off - eval_result.black_off}")
    
    # Generate moves
    moves = engine.generate_moves_single(piece_arr, color_arr, stm)
    print(f"\nWhite has {len(moves)} legal moves")
    
    print("\n✓ Tactical position analyzed successfully")


def test_batch_analysis():
    """Test batch analysis of multiple positions."""
    print("\n" + "=" * 60)
    print("Test: Batch analysis")
    print("=" * 60)
    
    import numpy as np
    
    # Analyze 3 different positions
    fens = [
        STARTING_FEN,
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
        "4k3/8/8/8/8/8/4P3/4K3 w - - 0 1"
    ]
    
    piece_arrays = []
    color_arrays = []
    
    for fen in fens:
        piece_arr, color_arr, _ = fen_to_arrays(fen)
        piece_arrays.append(piece_arr)
        color_arrays.append(color_arr)
    
    piece_batch = np.stack(piece_arrays)
    color_batch = np.stack(color_arrays)
    
    # Batch evaluation
    result = engine.evaluate_position_batch(piece_batch, color_batch)
    
    print(f"\nBatch Evaluation Results:")
    for i in range(len(fens)):
        print(f"  Position {i+1}:")
        print(f"    White: off={result.white_off[i]}, def={result.white_def[i]}")
        print(f"    Black: off={result.black_off[i]}, def={result.black_def[i]}")
    
    print("\n✓ Batch analysis completed successfully")


def run_all_tests():
    """Run all end-to-end tests."""
    print("\n" + "=" * 60)
    print("END-TO-END CHESS ENGINE TESTS")
    print("=" * 60)
    print(f"Backend: {engine.backend_name()}")
    
    test_starting_position_analysis()
    test_position_after_e4()
    test_endgame_position()
    test_tactical_position()
    test_batch_analysis()
    
    print("\n" + "=" * 60)
    print("ALL END-TO-END TESTS PASSED! ✓")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()

