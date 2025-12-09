from __future__ import annotations

import io

import chess
import chess.pgn
from fastapi import APIRouter, HTTPException

from ..models import PGNLoadRequest, PGNLoadResponse, PGNSaveRequest, PGNSaveResponse

router = APIRouter(prefix="/pgn", tags=["pgn"])


@router.post("/load", response_model=PGNLoadResponse)
async def load_pgn(req: PGNLoadRequest) -> PGNLoadResponse:
    try:
        game = chess.pgn.read_game(io.StringIO(req.pgn))
    except Exception as exc:  # python-chess can raise generic error
        raise HTTPException(status_code=400, detail=f"Invalid PGN: {exc}") from exc

    if game is None:
        raise HTTPException(status_code=400, detail="No game found in PGN")

    board = game.board()
    moves_san: list[str] = []
    for move in game.mainline_moves():
        moves_san.append(board.san(move))
        board.push(move)

    return PGNLoadResponse(moves_san=moves_san, final_fen=board.fen())


@router.post("/save", response_model=PGNSaveResponse)
async def save_pgn(req: PGNSaveRequest) -> PGNSaveResponse:
    if req.starting_fen:
        try:
            board = chess.Board(fen=req.starting_fen)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=f"Invalid starting FEN: {exc}") from exc
    else:
        board = chess.Board()

    game = chess.pgn.Game()
    game.setup(board)
    node = game

    for uci in req.moves_uci:
        try:
            move = board.parse_uci(uci)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid UCI move: {uci}")
        node = node.add_variation(move)
        board.push(move)

    out = io.StringIO()
    print(game, file=out, end="\n")

    return PGNSaveResponse(pgn=out.getvalue())
