from __future__ import annotations

from typing import Optional, List

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    fen: str = Field(..., description="FEN position to analyze")
    max_depth: int = Field(8, ge=1, le=40, description="Search depth (1–40)")


class MoveSuggestion(BaseModel):
    uci: Optional[str] = Field(None, description="UCI move, e.g. e2e4")
    san: Optional[str] = Field(None, description="SAN move, e.g. e4, Nf3")
    score_cp: Optional[int] = Field(None, description="Score in centipawns from White's perspective")
    mate: Optional[int] = Field(None, description="Mate in N (positive for White, negative for Black)")


class AnalyzeResponse(BaseModel):
    best_move: MoveSuggestion


class MovesRequest(BaseModel):
    fen: str = Field(..., description="FEN position")
    square: Optional[str] = Field(None, description="Optional from-square (e.g. e2) to filter moves")


class MovesResponse(BaseModel):
    moves_san: List[str]
    moves_uci: List[str]


class StudyCheckRequest(BaseModel):
    fen: str
    san: str


class StudyCheckResponse(BaseModel):
    valid: bool
    reason: Optional[str] = None


class PGNLoadRequest(BaseModel):
    pgn: str


class PGNLoadResponse(BaseModel):
    moves_san: List[str]
    final_fen: str


class PGNSaveRequest(BaseModel):
    starting_fen: Optional[str] = None
    moves_uci: List[str]


class PGNSaveResponse(BaseModel):
    pgn: str


class NewSessionResponse(BaseModel):
    session_id: str
    fen: str


class SessionMoveRequest(BaseModel):
    move_uci: str


class SessionStateResponse(BaseModel):
    session_id: str
    fen: str
    moves_uci: List[str]
