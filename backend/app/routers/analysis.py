from __future__ import annotations

import chess
from fastapi import APIRouter, HTTPException

from ..models import AnalyzeRequest, AnalyzeResponse, MoveSuggestion
from ..cache import cache

# Import engine_manager only if it exists
try:
    from ..engine import engine_manager
except (ImportError, AttributeError):
    engine_manager = None

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/", response_model=AnalyzeResponse)
async def analyze_position(req: AnalyzeRequest) -> AnalyzeResponse:
    try:
        board = chess.Board(fen=req.fen)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid FEN: {exc}") from exc

    # Check cache
    cached = cache.get(board.fen(), req.max_depth)
    if cached is not None:
        return AnalyzeResponse(best_move=MoveSuggestion(**cached))

    if board.is_game_over():
        raise HTTPException(status_code=400, detail="Game is already over in this position")

    if engine_manager is None:
        raise HTTPException(status_code=503, detail="Engine manager not available")

    result = await engine_manager.analyze(board, max_depth=req.max_depth)

    suggestion = MoveSuggestion(**result)

    cache.set(board.fen(), req.max_depth, result)

    return AnalyzeResponse(best_move=suggestion)
