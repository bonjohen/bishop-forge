"""
opponent.py - AI opponent move generation with different playing styles.
"""
from __future__ import annotations

import random
import chess
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from ..engine_core.backend import GPU as GPU_AVAILABLE
from ..engine_core.fen_utils import fen_to_arrays
from ..engine_core.engine_cpu import EngineCPU

router = APIRouter(prefix="/opponent", tags=["opponent"])

# Global flag to force CPU mode (can be toggled by frontend)
_force_cpu_mode = False


class OpponentMoveRequest(BaseModel):
    fen: str = Field(..., description="Current position FEN")
    profile: str = Field("random", description="Opponent profile: random, aggressive, defensive, moderate, defensive_passive")


class OpponentMoveResponse(BaseModel):
    move_uci: str = Field(..., description="Selected move in UCI format")
    move_san: Optional[str] = Field(None, description="Selected move in SAN format")
    evaluation: Optional[dict] = Field(None, description="Position evaluation details")


class GPUStatusResponse(BaseModel):
    gpu_available: bool = Field(..., description="Whether GPU is available")
    gpu_enabled: bool = Field(..., description="Whether GPU is currently enabled")
    backend_info: str = Field(..., description="Backend information string")


@router.get("/gpu-status", response_model=GPUStatusResponse)
async def get_gpu_status() -> GPUStatusResponse:
    """Get current GPU status and backend information."""
    from ..engine_core.backend import backend_info
    
    return GPUStatusResponse(
        gpu_available=GPU_AVAILABLE,
        gpu_enabled=GPU_AVAILABLE and not _force_cpu_mode,
        backend_info=backend_info()
    )


@router.post("/gpu-toggle")
async def toggle_gpu(enable: bool) -> dict:
    """Toggle GPU usage (force CPU mode on/off)."""
    global _force_cpu_mode
    _force_cpu_mode = not enable
    
    return {
        "gpu_enabled": enable and GPU_AVAILABLE,
        "message": f"GPU {'enabled' if enable and GPU_AVAILABLE else 'disabled (using CPU)'}"
    }


@router.post("/move", response_model=OpponentMoveResponse)
async def get_opponent_move(req: OpponentMoveRequest) -> OpponentMoveResponse:
    """
    Get opponent move based on selected profile.
    
    Profiles:
    - random: Random valid move
    - aggressive: Maximize own offense, minimize opponent offense
    - defensive: Maximize own defense, minimize opponent offense
    - moderate: Maximize own offense and defense
    - defensive_passive: Maximize own defense, minimize opponent defense
    """
    try:
        board = chess.Board(fen=req.fen)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid FEN: {exc}") from exc
    
    if board.is_game_over():
        raise HTTPException(status_code=400, detail="Game is already over")
    
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        raise HTTPException(status_code=400, detail="No legal moves available")
    
    # Select move based on profile
    if req.profile == "random":
        selected_move = random.choice(legal_moves)
        evaluation = None
    else:
        selected_move, evaluation = _select_strategic_move(board, legal_moves, req.profile)
    
    move_san = board.san(selected_move)
    move_uci = selected_move.uci()
    
    return OpponentMoveResponse(
        move_uci=move_uci,
        move_san=move_san,
        evaluation=evaluation
    )


def _select_strategic_move(board: chess.Board, legal_moves: list, profile: str) -> tuple:
    """Select move based on strategic profile using single-level evaluation."""
    best_move = None
    best_score = float('-inf')
    evaluation_details = {}
    
    # Get current position evaluation
    piece_arr, color_arr, stm = fen_to_arrays(board.fen())
    current_eval = EngineCPU.evaluate(piece_arr, color_arr)
    current_wo, current_wd, current_bo, current_bd = current_eval
    
    # Evaluate each legal move
    for move in legal_moves:
        board.push(move)
        piece_arr_after, color_arr_after, stm_after = fen_to_arrays(board.fen())
        after_eval = EngineCPU.evaluate(piece_arr_after, color_arr_after)
        wo_after, wd_after, bo_after, bd_after = after_eval
        board.pop()
        
        # Calculate score based on profile
        # Note: If black to move, we flip the perspective
        is_white = board.turn == chess.WHITE
        
        if is_white:
            my_off, my_def, opp_off, opp_def = wo_after, wd_after, bo_after, bd_after
            my_off_delta = wo_after - current_wo
            my_def_delta = wd_after - current_wd
            opp_off_delta = bo_after - current_bo
            opp_def_delta = bd_after - current_bd
        else:
            my_off, my_def, opp_off, opp_def = bo_after, bd_after, wo_after, wd_after
            my_off_delta = bo_after - current_bo
            my_def_delta = bd_after - current_bd
            opp_off_delta = wo_after - current_wo
            opp_def_delta = wd_after - current_wd
        
        # Score based on profile
        if profile == "aggressive":
            score = my_off_delta - opp_off_delta
        elif profile == "defensive":
            score = my_def_delta - opp_off_delta
        elif profile == "moderate":
            score = my_off_delta + my_def_delta
        elif profile == "defensive_passive":
            score = my_def_delta - opp_def_delta
        else:
            score = my_off_delta  # Default to offensive
        
        if score > best_score:
            best_score = score
            best_move = move
            evaluation_details = {
                "score": int(best_score),
                "my_offense": int(my_off),
                "my_defense": int(my_def),
                "opponent_offense": int(opp_off),
                "opponent_defense": int(opp_def)
            }
    
    return best_move, evaluation_details

