from __future__ import annotations

import chess
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_moves_starting_position():
    """Test legal moves from starting position"""
    board = chess.Board()
    res = client.post(
        "/moves/",
        json={"fen": board.fen()},
    )
    assert res.status_code == 200
    data = res.json()
    assert "moves_san" in data
    assert "moves_uci" in data
    # Starting position has 20 legal moves
    assert len(data["moves_san"]) == 20
    assert len(data["moves_uci"]) == 20
    # Check some expected moves
    assert "e4" in data["moves_san"]
    assert "Nf3" in data["moves_san"]
    assert "e2e4" in data["moves_uci"]


def test_moves_with_square_filter():
    """Test filtering moves by from-square"""
    board = chess.Board()
    res = client.post(
        "/moves/",
        json={"fen": board.fen(), "square": "e2"},
    )
    assert res.status_code == 200
    data = res.json()
    # e2 pawn can move to e3 or e4
    assert len(data["moves_san"]) == 2
    assert "e3" in data["moves_san"]
    assert "e4" in data["moves_san"]
    assert "e2e3" in data["moves_uci"]
    assert "e2e4" in data["moves_uci"]


def test_moves_invalid_fen():
    """Test error handling for invalid FEN"""
    res = client.post(
        "/moves/",
        json={"fen": "invalid fen string"},
    )
    assert res.status_code == 400
    assert "Invalid FEN" in res.json()["detail"]


def test_moves_game_over():
    """Test that game over position returns empty move list"""
    # Fool's mate position
    board = chess.Board()
    board.push_san("f3")
    board.push_san("e5")
    board.push_san("g4")
    board.push_san("Qh4")  # Checkmate
    
    res = client.post(
        "/moves/",
        json={"fen": board.fen()},
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["moves_san"]) == 0
    assert len(data["moves_uci"]) == 0


def test_moves_square_with_no_moves():
    """Test filtering by square that has no legal moves"""
    board = chess.Board()
    # a1 rook has no legal moves in starting position
    res = client.post(
        "/moves/",
        json={"fen": board.fen(), "square": "a1"},
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["moves_san"]) == 0
    assert len(data["moves_uci"]) == 0


def test_moves_complex_position():
    """Test moves in a more complex mid-game position"""
    # Position after 1. e4 e5 2. Nf3 Nc6 3. Bb5
    board = chess.Board()
    board.push_san("e4")
    board.push_san("e5")
    board.push_san("Nf3")
    board.push_san("Nc6")
    board.push_san("Bb5")
    
    res = client.post(
        "/moves/",
        json={"fen": board.fen()},
    )
    assert res.status_code == 200
    data = res.json()
    # Should have multiple legal moves
    assert len(data["moves_san"]) > 0
    assert len(data["moves_uci"]) > 0
    # Verify some expected moves for Black
    assert "a6" in data["moves_san"]  # Attack the bishop
    assert "Nf6" in data["moves_san"]  # Develop knight

