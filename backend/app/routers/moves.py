from __future__ import annotations

import chess
from fastapi import APIRouter, HTTPException

from ..models import MovesRequest, MovesResponse

router = APIRouter(prefix="/moves", tags=["moves"])


@router.post("/", response_model=MovesResponse)
async def list_moves(req: MovesRequest) -> MovesResponse:
    try:
        board = chess.Board(fen=req.fen)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid FEN: {exc}") from exc

    if board.is_game_over():
        return MovesResponse(moves_san=[], moves_uci=[])

    moves = list(board.legal_moves)

    if req.square:
        # Filter by from-square if provided
        moves = [m for m in moves if chess.square_name(m.from_square) == req.square]

    moves_san: list[str] = []
    moves_uci: list[str] = []
    for mv in moves:
        moves_uci.append(mv.uci())
        moves_san.append(board.san(mv))

    return MovesResponse(moves_san=moves_san, moves_uci=moves_uci)
