from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .engine import engine_manager
from .routers import analysis, moves, study, pgn, sessions


app = FastAPI(
    title="Project BishopForge API",
    version="1.0.0",
    description="Chess analysis and helper API for Project BishopForge.",
)


# CORS configuration
if settings.ALLOW_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # tighten later if needed
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.on_event("startup")
async def on_startup() -> None:
    await engine_manager.startup()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await engine_manager.shutdown()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


# Routers
app.include_router(analysis.router)
app.include_router(moves.router)
app.include_router(study.router)
app.include_router(pgn.router)
app.include_router(sessions.router)
