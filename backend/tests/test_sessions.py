from __future__ import annotations

import chess
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_session_create():
    """Test creating a new session"""
    res = client.post("/session/new")
    assert res.status_code == 200
    data = res.json()
    assert "session_id" in data
    assert "fen" in data
    # Should start with standard starting position
    assert data["fen"] == chess.Board().fen()


def test_session_get_state():
    """Test retrieving session state"""
    # Create session
    create_res = client.post("/session/new")
    session_id = create_res.json()["session_id"]
    
    # Get state
    res = client.get(f"/session/{session_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["session_id"] == session_id
    assert data["fen"] == chess.Board().fen()
    assert data["moves_uci"] == []


def test_session_get_invalid_id():
    """Test error handling for invalid session ID"""
    res = client.get("/session/nonexistent-id")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_session_make_move():
    """Test making a move in a session"""
    # Create session
    create_res = client.post("/session/new")
    session_id = create_res.json()["session_id"]
    
    # Make move
    res = client.post(
        f"/session/{session_id}/move",
        json={"move_uci": "e2e4"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["session_id"] == session_id
    assert len(data["moves_uci"]) == 1
    assert data["moves_uci"][0] == "e2e4"
    
    # Verify FEN changed
    board = chess.Board()
    board.push_san("e4")
    assert data["fen"] == board.fen()


def test_session_make_multiple_moves():
    """Test making multiple moves in a session"""
    # Create session
    create_res = client.post("/session/new")
    session_id = create_res.json()["session_id"]
    
    # Make first move
    client.post(
        f"/session/{session_id}/move",
        json={"move_uci": "e2e4"},
    )
    
    # Make second move
    res = client.post(
        f"/session/{session_id}/move",
        json={"move_uci": "e7e5"},
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["moves_uci"]) == 2
    assert data["moves_uci"] == ["e2e4", "e7e5"]


def test_session_illegal_move():
    """Test error handling for illegal move"""
    # Create session
    create_res = client.post("/session/new")
    session_id = create_res.json()["session_id"]

    # Try illegal move (e5 for White in starting position)
    res = client.post(
        f"/session/{session_id}/move",
        json={"move_uci": "e2e5"},
    )
    assert res.status_code == 400
    # The error message could be "Invalid UCI move" or "Illegal move"
    detail = res.json()["detail"].lower()
    assert "illegal" in detail or "invalid" in detail


def test_session_invalid_uci():
    """Test error handling for invalid UCI notation"""
    # Create session
    create_res = client.post("/session/new")
    session_id = create_res.json()["session_id"]
    
    # Try invalid UCI
    res = client.post(
        f"/session/{session_id}/move",
        json={"move_uci": "invalid"},
    )
    assert res.status_code == 400
    assert "invalid" in res.json()["detail"].lower()


def test_session_undo():
    """Test undoing a move"""
    # Create session and make moves
    create_res = client.post("/session/new")
    session_id = create_res.json()["session_id"]
    
    client.post(
        f"/session/{session_id}/move",
        json={"move_uci": "e2e4"},
    )
    client.post(
        f"/session/{session_id}/move",
        json={"move_uci": "e7e5"},
    )
    
    # Undo last move
    res = client.post(f"/session/{session_id}/undo")
    assert res.status_code == 200
    data = res.json()
    assert len(data["moves_uci"]) == 1
    assert data["moves_uci"] == ["e2e4"]
    
    # Verify FEN is correct
    board = chess.Board()
    board.push_san("e4")
    assert data["fen"] == board.fen()


def test_session_undo_empty():
    """Test error handling when undoing with no moves"""
    # Create session
    create_res = client.post("/session/new")
    session_id = create_res.json()["session_id"]
    
    # Try to undo with no moves
    res = client.post(f"/session/{session_id}/undo")
    assert res.status_code == 400
    assert "no moves" in res.json()["detail"].lower()


def test_session_undo_multiple():
    """Test undoing multiple moves"""
    # Create session and make moves
    create_res = client.post("/session/new")
    session_id = create_res.json()["session_id"]
    
    client.post(f"/session/{session_id}/move", json={"move_uci": "e2e4"})
    client.post(f"/session/{session_id}/move", json={"move_uci": "e7e5"})
    client.post(f"/session/{session_id}/move", json={"move_uci": "g1f3"})
    
    # Undo twice
    client.post(f"/session/{session_id}/undo")
    res = client.post(f"/session/{session_id}/undo")
    
    assert res.status_code == 200
    data = res.json()
    assert len(data["moves_uci"]) == 1
    assert data["moves_uci"] == ["e2e4"]


def test_session_move_after_undo():
    """Test making a move after undo"""
    # Create session and make moves
    create_res = client.post("/session/new")
    session_id = create_res.json()["session_id"]
    
    client.post(f"/session/{session_id}/move", json={"move_uci": "e2e4"})
    client.post(f"/session/{session_id}/move", json={"move_uci": "e7e5"})
    
    # Undo
    client.post(f"/session/{session_id}/undo")
    
    # Make different move
    res = client.post(
        f"/session/{session_id}/move",
        json={"move_uci": "c7c5"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["moves_uci"] == ["e2e4", "c7c5"]

