from __future__ import annotations

import chess
from fastapi import APIRouter, HTTPException

from ..models import StudyCheckRequest, StudyCheckResponse

router = APIRouter(prefix="/study", tags=["study"])


@router.post("/check", response_model=StudyCheckResponse)
async def check_forced_move(req: StudyCheckRequest) -> StudyCheckResponse:
    try:
        board = chess.Board(fen=req.fen)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid FEN: {exc}") from exc

    try:
        # If san is illegal, python-chess will raise
        move = board.parse_san(req.san)
    except ValueError:
        return StudyCheckResponse(valid=False, reason="SAN is not legal in this position")

    if move not in board.legal_moves:
        return StudyCheckResponse(valid=False, reason="Move not legal in this position")

    return StudyCheckResponse(valid=True, reason=None)
