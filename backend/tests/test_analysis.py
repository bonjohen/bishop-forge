from __future__ import annotations

import chess
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_analysis_valid_start_position():
    board = chess.Board()  # starting FEN
    res = client.post(
        "/analysis/",
        json={"fen": board.fen(), "max_depth": 4},
    )
    assert res.status_code == 200
    data = res.json()
    assert "best_move" in data
    assert data["best_move"]["uci"] is not None


def test_analysis_invalid_fen():
    res = client.post(
        "/analysis/",
        json={"fen": "invalid fen string", "max_depth": 4},
    )
    assert res.status_code == 400
    assert "Invalid FEN" in res.json()["detail"]


def test_analysis_game_over():
    """Test that game over position returns error"""
    # Fool's mate position
    board = chess.Board()
    board.push_san("f3")
    board.push_san("e5")
    board.push_san("g4")
    board.push_san("Qh4")  # Checkmate

    res = client.post(
        "/analysis/",
        json={"fen": board.fen(), "max_depth": 4},
    )
    assert res.status_code == 400
    assert "already over" in res.json()["detail"].lower()


def test_analysis_different_depths():
    """Test analysis with different depth values"""
    board = chess.Board()

    # Test with depth 1
    res1 = client.post(
        "/analysis/",
        json={"fen": board.fen(), "max_depth": 1},
    )
    assert res1.status_code == 200

    # Test with depth 20
    res2 = client.post(
        "/analysis/",
        json={"fen": board.fen(), "max_depth": 20},
    )
    assert res2.status_code == 200


def test_analysis_mid_game_position():
    """Test analysis of a mid-game position"""
    # Position after 1. e4 e5 2. Nf3 Nc6 3. Bb5
    board = chess.Board()
    board.push_san("e4")
    board.push_san("e5")
    board.push_san("Nf3")
    board.push_san("Nc6")
    board.push_san("Bb5")

    res = client.post(
        "/analysis/",
        json={"fen": board.fen(), "max_depth": 8},
    )
    assert res.status_code == 200
    data = res.json()
    assert "best_move" in data
    assert data["best_move"]["uci"] is not None
    assert data["best_move"]["san"] is not None


def test_analysis_response_structure():
    """Test that response has correct structure"""
    board = chess.Board()
    res = client.post(
        "/analysis/",
        json={"fen": board.fen(), "max_depth": 4},
    )
    assert res.status_code == 200
    data = res.json()

    # Check structure
    assert "best_move" in data
    best_move = data["best_move"]
    assert "uci" in best_move
    assert "san" in best_move
    assert "score_cp" in best_move
    assert "mate" in best_move


def test_analysis_caching():
    """Test that caching works (if enabled)"""
    board = chess.Board()

    # First request
    res1 = client.post(
        "/analysis/",
        json={"fen": board.fen(), "max_depth": 4},
    )
    assert res1.status_code == 200
    data1 = res1.json()

    # Second request (should be cached if caching enabled)
    res2 = client.post(
        "/analysis/",
        json={"fen": board.fen(), "max_depth": 4},
    )
    assert res2.status_code == 200
    data2 = res2.json()

    # Results should be identical
    assert data1 == data2


def test_analysis_endgame_position():
    """Test analysis of an endgame position"""
    # King and pawn endgame
    fen = "8/8/8/4k3/8/4K3/4P3/8 w - - 0 1"

    res = client.post(
        "/analysis/",
        json={"fen": fen, "max_depth": 8},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["best_move"]["uci"] is not None
