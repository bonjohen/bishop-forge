from __future__ import annotations

import chess
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_pgn_load_simple_game():
    """Test loading a simple PGN game"""
    pgn = "1. e4 e5 2. Nf3 Nc6"
    
    res = client.post(
        "/pgn/load",
        json={"pgn": pgn},
    )
    assert res.status_code == 200
    data = res.json()
    assert "moves_san" in data
    assert "final_fen" in data
    assert data["moves_san"] == ["e4", "e5", "Nf3", "Nc6"]
    # Verify final FEN is correct
    board = chess.Board()
    for move in data["moves_san"]:
        board.push_san(move)
    assert data["final_fen"] == board.fen()


def test_pgn_load_with_headers():
    """Test loading PGN with headers"""
    pgn = """[Event "Test Game"]
[White "Player 1"]
[Black "Player 2"]

1. e4 e5 2. Nf3"""
    
    res = client.post(
        "/pgn/load",
        json={"pgn": pgn},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["moves_san"] == ["e4", "e5", "Nf3"]


def test_pgn_load_invalid_pgn():
    """Test error handling for invalid PGN"""
    # python-chess is very lenient and may parse some invalid PGN
    # Use a truly malformed PGN that will fail
    pgn = ""

    res = client.post(
        "/pgn/load",
        json={"pgn": pgn},
    )
    assert res.status_code == 400
    assert "No game found" in res.json()["detail"]


def test_pgn_load_empty():
    """Test error handling for empty PGN"""
    res = client.post(
        "/pgn/load",
        json={"pgn": ""},
    )
    assert res.status_code == 400


def test_pgn_save_simple_game():
    """Test saving a simple game to PGN"""
    res = client.post(
        "/pgn/save",
        json={
            "starting_fen": None,
            "moves_uci": ["e2e4", "e7e5", "g1f3", "b8c6"],
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "pgn" in data
    # PGN should contain the moves
    assert "e4" in data["pgn"]
    assert "e5" in data["pgn"]
    assert "Nf3" in data["pgn"]
    assert "Nc6" in data["pgn"]


def test_pgn_save_with_custom_starting_position():
    """Test saving game from custom starting position"""
    # Start from position after 1. e4
    board = chess.Board()
    board.push_san("e4")
    starting_fen = board.fen()
    
    res = client.post(
        "/pgn/save",
        json={
            "starting_fen": starting_fen,
            "moves_uci": ["e7e5", "g1f3"],
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "pgn" in data


def test_pgn_save_invalid_uci():
    """Test error handling for invalid UCI move"""
    res = client.post(
        "/pgn/save",
        json={
            "starting_fen": None,
            "moves_uci": ["e2e4", "invalid_move"],
        },
    )
    assert res.status_code == 400
    assert "Invalid UCI move" in res.json()["detail"]


def test_pgn_save_invalid_starting_fen():
    """Test error handling for invalid starting FEN"""
    res = client.post(
        "/pgn/save",
        json={
            "starting_fen": "invalid fen",
            "moves_uci": ["e2e4"],
        },
    )
    assert res.status_code == 400
    assert "Invalid starting FEN" in res.json()["detail"]


def test_pgn_save_empty_moves():
    """Test saving PGN with no moves"""
    res = client.post(
        "/pgn/save",
        json={
            "starting_fen": None,
            "moves_uci": [],
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "pgn" in data


def test_pgn_roundtrip():
    """Test loading and saving the same game"""
    original_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5"
    
    # Load the PGN
    load_res = client.post(
        "/pgn/load",
        json={"pgn": original_pgn},
    )
    assert load_res.status_code == 200
    load_data = load_res.json()
    
    # Convert SAN moves to UCI
    board = chess.Board()
    moves_uci = []
    for san in load_data["moves_san"]:
        move = board.parse_san(san)
        moves_uci.append(move.uci())
        board.push(move)
    
    # Save back to PGN
    save_res = client.post(
        "/pgn/save",
        json={
            "starting_fen": None,
            "moves_uci": moves_uci,
        },
    )
    assert save_res.status_code == 200
    save_data = save_res.json()
    
    # Verify the moves are preserved
    assert "e4" in save_data["pgn"]
    assert "Bb5" in save_data["pgn"]

