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
