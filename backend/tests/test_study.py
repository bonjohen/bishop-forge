from __future__ import annotations

import chess
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_study_check_valid_move():
    """Test validating a legal SAN move"""
    board = chess.Board()
    res = client.post(
        "/study/check",
        json={"fen": board.fen(), "san": "e4"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert data["reason"] is None


def test_study_check_valid_knight_move():
    """Test validating a legal knight move"""
    board = chess.Board()
    res = client.post(
        "/study/check",
        json={"fen": board.fen(), "san": "Nf3"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert data["reason"] is None


def test_study_check_invalid_move():
    """Test validating an illegal move"""
    board = chess.Board()
    # e5 is illegal for White in starting position
    res = client.post(
        "/study/check",
        json={"fen": board.fen(), "san": "e5"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is False
    assert data["reason"] is not None
    assert "not legal" in data["reason"].lower()


def test_study_check_malformed_san():
    """Test validating malformed SAN notation"""
    board = chess.Board()
    res = client.post(
        "/study/check",
        json={"fen": board.fen(), "san": "xyz123"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is False
    assert data["reason"] is not None


def test_study_check_invalid_fen():
    """Test error handling for invalid FEN"""
    res = client.post(
        "/study/check",
        json={"fen": "invalid fen", "san": "e4"},
    )
    assert res.status_code == 400
    assert "Invalid FEN" in res.json()["detail"]


def test_study_check_castling():
    """Test validating castling moves"""
    # Set up position where castling is legal
    board = chess.Board()
    board.push_san("e4")
    board.push_san("e5")
    board.push_san("Nf3")
    board.push_san("Nc6")
    board.push_san("Bc4")
    board.push_san("Bc5")
    
    # White can castle kingside
    res = client.post(
        "/study/check",
        json={"fen": board.fen(), "san": "O-O"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True


def test_study_check_capture():
    """Test validating a capture move"""
    # Set up position with a capture available
    board = chess.Board()
    board.push_san("e4")
    board.push_san("d5")
    
    # White can capture with exd5
    res = client.post(
        "/study/check",
        json={"fen": board.fen(), "san": "exd5"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True


def test_study_check_promotion():
    """Test validating a pawn promotion move"""
    # Set up position where promotion is possible
    # White pawn on e7, Black king on h8
    fen = "7k/4P3/8/8/8/8/8/7K w - - 0 1"
    
    res = client.post(
        "/study/check",
        json={"fen": fen, "san": "e8=Q"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True


def test_study_check_ambiguous_move():
    """Test validating moves that require disambiguation"""
    # Position with two knights that can move to same square
    fen = "rnbqkbnr/pppppppp/8/8/8/2N2N2/PPPPPPPP/R1BQKB1R w KQkq - 0 1"
    
    # Nfd4 should be valid (knight from f3 to d4)
    res = client.post(
        "/study/check",
        json={"fen": fen, "san": "Nfd4"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True

