from __future__ import annotations

import uuid
from typing import Dict, List

import chess
from fastapi import APIRouter, HTTPException

from ..models import NewSessionResponse, SessionMoveRequest, SessionStateResponse

router = APIRouter(prefix="/session", tags=["session"])

# In-memory session store (good enough for dev; replace with Redis later)
_sessions: Dict[str, chess.Board] = {}
_session_moves: Dict[str, List[str]] = {}


@router.post("/new", response_model=NewSessionResponse)
async def new_session() -> NewSessionResponse:
    session_id = str(uuid.uuid4())
    board = chess.Board()
    _sessions[session_id] = board
    _session_moves[session_id] = []
    return NewSessionResponse(session_id=session_id, fen=board.fen())


def _get_session(session_id: str) -> chess.Board:
    board = _sessions.get(session_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return board


@router.get("/{session_id}", response_model=SessionStateResponse)
async def get_session_state(session_id: str) -> SessionStateResponse:
    board = _get_session(session_id)
    moves = _session_moves.get(session_id, [])
    return SessionStateResponse(session_id=session_id, fen=board.fen(), moves_uci=moves)


@router.post("/{session_id}/move", response_model=SessionStateResponse)
async def apply_session_move(session_id: str, req: SessionMoveRequest) -> SessionStateResponse:
    board = _get_session(session_id)

    try:
        move = board.parse_uci(req.move_uci)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UCI move")

    if move not in board.legal_moves:
        raise HTTPException(status_code=400, detail="Illegal move in this position")

    board.push(move)
    _session_moves.setdefault(session_id, []).append(req.move_uci)

    return SessionStateResponse(session_id=session_id, fen=board.fen(), moves_uci=_session_moves[session_id])


@router.post("/{session_id}/undo", response_model=SessionStateResponse)
async def undo_session_move(session_id: str) -> SessionStateResponse:
    board = _get_session(session_id)
    moves = _session_moves.get(session_id, [])

    if not moves:
        raise HTTPException(status_code=400, detail="No moves to undo")

    board.pop()
    moves.pop()

    return SessionStateResponse(session_id=session_id, fen=board.fen(), moves_uci=moves)
