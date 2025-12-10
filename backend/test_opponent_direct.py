"""
Direct test of opponent AI logic without API server.
"""
import chess
from app.routers.opponent import _select_strategic_move

def test_opponent_profiles():
    """Test all opponent profiles."""
    board = chess.Board()  # Starting position
    legal_moves = list(board.legal_moves)
    
    profiles = ["aggressive", "defensive", "moderate", "defensive_passive"]
    
    print("=" * 60)
    print("Testing Opponent AI Profiles")
    print("=" * 60)
    
    for profile in profiles:
        print(f"\n{profile.upper()}:")
        move, evaluation = _select_strategic_move(board, legal_moves, profile)
        print(f"  Selected move: {board.san(move)} ({move.uci()})")
        print(f"  Evaluation: {evaluation}")
    
    print("\n" + "=" * 60)
    print("✅ All profiles tested successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_opponent_profiles()

