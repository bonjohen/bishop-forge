from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Optional

import chess
import chess.engine
import httpx

from .config import settings


class EngineError(Exception):
    pass


class EngineManager:
    """
    Unified engine abstraction with three modes:
    - 'python'      : lightweight eval (material only)
    - 'simpleengine': Stockfish via python-chess SimpleEngine
    - 'external'    : delegate to remote HTTP engine
    """

    def __init__(self) -> None:
        self.mode = settings.ENGINE_MODE
        self._pool: asyncio.Queue[chess.engine.SimpleEngine] | None = None
        self._pool_initialized = False

    async def startup(self) -> None:
        if self.mode == "simpleengine":
            if not settings.STOCKFISH_PATH:
                raise EngineError("STOCKFISH_PATH must be set for simpleengine mode")
            self._pool = asyncio.Queue()
            for _ in range(settings.ENGINE_POOL_SIZE):
                engine = chess.engine.SimpleEngine.popen_uci(settings.STOCKFISH_PATH)
                await self._pool.put(engine)
            self._pool_initialized = True

    async def shutdown(self) -> None:
        if self.mode == "simpleengine" and self._pool:
            while not self._pool.empty():
                engine = await self._pool.get()
                engine.close()
            self._pool_initialized = False

    @asynccontextmanager
    async def _get_engine(self) -> chess.engine.SimpleEngine:
        if not self._pool or not self._pool_initialized:
            raise EngineError("Engine pool not initialized")
        engine = await self._pool.get()
        try:
            yield engine
        finally:
            await self._pool.put(engine)

    async def analyze(self, board: chess.Board, max_depth: int = 8) -> dict:
        """
        Return dict:
        {
          "uci": "e2e4",
          "san": "e4",
          "score_cp": 23,   # centipawns (None if not applicable)
          "mate": None|int  # mate in N (sign indicates side to move)
        }
        """
        if self.mode == "python":
            return self._analyze_python(board)

        if self.mode == "simpleengine":
            return await self._analyze_simpleengine(board, max_depth)

        if self.mode == "external":
            return await self._analyze_external(board, max_depth)

        raise EngineError(f"Unknown engine mode: {self.mode}")

    def _analyze_python(self, board: chess.Board) -> dict:
        # Very simple material evaluation as a fallback
        piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
        }
        score = 0
        for piece_type, value in piece_values.items():
            score += len(board.pieces(piece_type, chess.WHITE)) * value
            score -= len(board.pieces(piece_type, chess.BLACK)) * value

        legal = list(board.legal_moves)
        if not legal:
            # no legal moves: checkmate or stalemate
            return {
                "uci": None,
                "san": None,
                "score_cp": score,
                "mate": 0,
            }

        # naive: choose first legal move
        move = legal[0]
        san = board.san(move)
        return {
            "uci": move.uci(),
            "san": san,
            "score_cp": score,
            "mate": None,
        }

    async def _analyze_simpleengine(self, board: chess.Board, max_depth: int) -> dict:
        async with self._get_engine() as engine:
            info = await engine.analyse(board, chess.engine.Limit(depth=max_depth))
            move = info.get("pv", [None])[0] or next(iter(board.legal_moves))
            san = board.san(move)

            score = info.get("score")
            score_cp: Optional[int] = None
            mate: Optional[int] = None
            if score is not None:
                if score.is_mate():
                    mate = score.white().mate()
                else:
                    score_cp = score.white().score()

            return {
                "uci": move.uci(),
                "san": san,
                "score_cp": score_cp,
                "mate": mate,
            }

    async def _analyze_external(self, board: chess.Board, max_depth: int) -> dict:
        if not settings.EXTERNAL_ENGINE_URL:
            raise EngineError("EXTERNAL_ENGINE_URL must be set for external mode")

        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(
                settings.EXTERNAL_ENGINE_URL,
                json={"fen": board.fen(), "max_depth": max_depth},
            )
            res.raise_for_status()
            data = res.json()
            # Expect compatible schema; otherwise normalize here
            return {
                "uci": data.get("uci"),
                "san": data.get("san"),
                "score_cp": data.get("score_cp"),
                "mate": data.get("mate"),
            }


engine_manager = EngineManager()
