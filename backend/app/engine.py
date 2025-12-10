"""
engine.py — Public chess engine API used by FastAPI routers.

This module wraps the internal accelerated engine_core (NumPy+Numba / CuPy)
and exposes type-stable, backend-agnostic interfaces for:
    - single-position evaluation
    - batched evaluation
    - single-position move generation
    - batched move generation
    - batched attack maps

All public return types are Python scalars or NumPy ndarrays,
regardless of whether the underlying backend uses CPU or GPU.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Tuple, List

import numpy as np

try:
    import cupy as cp  # type: ignore
except Exception:
    cp = None

# Internal core engine
from .engine_core.backend import xp, GPU  # noqa: F401  (GPU info may be useful elsewhere)
from .engine_core.engine_batch import (
    compute_attack_maps_batch as _core_compute_attack_maps_batch,
    evaluate_batch as _core_evaluate_batch,
    generate_moves_batch as _core_generate_moves_batch,
)
from .engine_core.moves import (
    MOVE_IDX,
    MOVE_FROM,
    MOVE_TO,
    MOVE_PROMO,
    MOVE_FLAGS,
)


# =====================================================================
# Data structures
# =====================================================================

@dataclass(frozen=True)
class Evaluation:
    """Single-position evaluation scores."""
    white_off: int
    white_def: int
    black_off: int
    black_def: int


@dataclass(frozen=True)
class BatchedEvaluation:
    """Batched evaluation scores; arrays are shape (N,)."""
    white_off: np.ndarray
    white_def: np.ndarray
    black_off: np.ndarray
    black_def: np.ndarray


@dataclass(frozen=True)
class Move:
    """Single move in a batch (board_idx may be 0 for single-position)."""
    board_idx: int
    from_sq: int
    to_sq: int
    promo: int
    flags: int


@dataclass(frozen=True)
class SingleMove:
    """Single-position move (no board index)."""
    from_sq: int
    to_sq: int
    promo: int
    flags: int


# =====================================================================
# Internal helpers
# =====================================================================

def _to_numpy(arr) -> np.ndarray:
    """Convert xp/NumPy/CuPy array to a NumPy ndarray."""
    if isinstance(arr, np.ndarray):
        return arr
    if cp is not None and isinstance(arr, cp.ndarray):  # type: ignore[attr-defined]
        return cp.asnumpy(arr)  # type: ignore[call-arg]
    # Fallback
    return np.asarray(arr)


def _normalize_board_batch(
    piece: Sequence[Sequence[int]] | np.ndarray,
    color: Sequence[Sequence[int]] | np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Ensure we have NumPy arrays of shape (N, 64), dtype=int8.

    Accepts:
        - (64,)      → treated as single position (N=1)
        - (N,64)     → batch
        - any Sequence-of-Sequences convertible to np.ndarray
    """
    piece_np = np.asarray(piece, dtype=np.int8)
    color_np = np.asarray(color, dtype=np.int8)

    if piece_np.ndim == 1:
        if piece_np.shape[0] != 64:
            raise ValueError(f"Expected piece array of length 64, got {piece_np.shape}")
        piece_np = piece_np.reshape(1, 64)
    if color_np.ndim == 1:
        if color_np.shape[0] != 64:
            raise ValueError(f"Expected color array of length 64, got {color_np.shape}")
        color_np = color_np.reshape(1, 64)

    if piece_np.shape != color_np.shape:
        raise ValueError(
            f"piece and color shapes must match; got {piece_np.shape} vs {color_np.shape}"
        )

    if piece_np.shape[1] != 64:
        raise ValueError(
            f"Expected shape (N,64) for boards; got {piece_np.shape}"
        )

    return piece_np, color_np


def _normalize_stm_batch(
    stm: Sequence[int] | np.ndarray,
    N: int,
) -> np.ndarray:
    """
    Normalize side-to-move batch.

    Accepts:
        - scalar-like (0 or 1) → broadcast to (N,)
        - (N,) array/list of 0/1
    """
    stm_arr = np.asarray(stm, dtype=np.int8)

    if stm_arr.ndim == 0:
        # broadcast scalar
        stm_arr = np.full(N, int(stm_arr), dtype=np.int8)
    elif stm_arr.ndim == 1:
        if stm_arr.shape[0] != N:
            raise ValueError(
                f"stm_batch length must be {N}, got {stm_arr.shape[0]}"
            )
    else:
        raise ValueError(
            f"stm must be scalar or 1D array; got shape {stm_arr.shape}"
        )

    return stm_arr


# =====================================================================
# Public API — Evaluation
# =====================================================================

def evaluate_position_single(
    piece: Sequence[Sequence[int]] | np.ndarray,
    color: Sequence[Sequence[int]] | np.ndarray,
) -> Evaluation:
    """
    Evaluate a single board (length-64 arrays).

    Returns:
        Evaluation(white_off, white_def, black_off, black_def)
        All fields are Python ints.
    """
    piece_batch, color_batch = _normalize_board_batch(piece, color)  # → (1,64)
    # Move to backend array type
    piece_xp = xp.asarray(piece_batch, dtype=xp.int8)
    color_xp = xp.asarray(color_batch, dtype=xp.int8)

    wo_xp, wd_xp, bo_xp, bd_xp = _core_evaluate_batch(piece_xp, color_xp)
    wo = int(_to_numpy(wo_xp)[0])
    wd = int(_to_numpy(wd_xp)[0])
    bo = int(_to_numpy(bo_xp)[0])
    bd = int(_to_numpy(bd_xp)[0])

    return Evaluation(white_off=wo, white_def=wd, black_off=bo, black_def=bd)


def evaluate_position_batch(
    piece_batch: Sequence[Sequence[int]] | np.ndarray,
    color_batch: Sequence[Sequence[int]] | np.ndarray,
) -> BatchedEvaluation:
    """
    Evaluate a batch of boards.

    Inputs:
        piece_batch: (N,64) or (64,)
        color_batch: (N,64) or (64,)

    Returns:
        BatchedEvaluation with NumPy arrays white_off, white_def, black_off, black_def
        of shape (N,) each.
    """
    piece_np, color_np = _normalize_board_batch(piece_batch, color_batch)
    piece_xp = xp.asarray(piece_np, dtype=xp.int8)
    color_xp = xp.asarray(color_np, dtype=xp.int8)

    wo_xp, wd_xp, bo_xp, bd_xp = _core_evaluate_batch(piece_xp, color_xp)

    return BatchedEvaluation(
        white_off=_to_numpy(wo_xp),
        white_def=_to_numpy(wd_xp),
        black_off=_to_numpy(bo_xp),
        black_def=_to_numpy(bd_xp),
    )


# =====================================================================
# Public API — Attack Maps
# =====================================================================

def attack_maps_batch(
    piece_batch: Sequence[Sequence[int]] | np.ndarray,
    color_batch: Sequence[Sequence[int]] | np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute attack maps for a batch of boards.

    Returns:
        (white_att, black_att) each as NumPy bool array of shape (N,64).
    """
    piece_np, color_np = _normalize_board_batch(piece_batch, color_batch)
    piece_xp = xp.asarray(piece_np, dtype=xp.int8)
    color_xp = xp.asarray(color_np, dtype=xp.int8)

    w_xp, b_xp = _core_compute_attack_maps_batch(piece_xp, color_xp)
    return _to_numpy(w_xp), _to_numpy(b_xp)


def attack_maps_single(
    piece: Sequence[Sequence[int]] | np.ndarray,
    color: Sequence[Sequence[int]] | np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Attack maps for a single board.

    Returns:
        (white_att[64], black_att[64]) as NumPy bool arrays.
    """
    w_batch, b_batch = attack_maps_batch(piece, color)
    return w_batch[0], b_batch[0]


# =====================================================================
# Public API — Move Generation
# =====================================================================

def generate_moves_single(
    piece: Sequence[Sequence[int]] | np.ndarray,
    color: Sequence[Sequence[int]] | np.ndarray,
    stm: Sequence[int],
) -> List[SingleMove]:
    """
    Generate pseudo-legal moves for a single board.

    Args:
        piece: length-64 array of piece codes (int)
        color: length-64 array of color codes (-1 empty, 0 white, 1 black)
        stm:   side to move (0=white, 1=black)

    Returns:
        List[SingleMove] for this single board.
    """
    piece_np, color_np = _normalize_board_batch(piece, color)  # (1,64)
    stm_batch = _normalize_stm_batch(stm, N=1)

    piece_xp = xp.asarray(piece_np, dtype=xp.int8)
    color_xp = xp.asarray(color_np, dtype=xp.int8)
    stm_xp = xp.asarray(stm_batch, dtype=xp.int8)

    moves_xp = _core_generate_moves_batch(piece_xp, color_xp, stm_xp)
    moves_np = _to_numpy(moves_xp)  # shape (M,5)

    out: List[SingleMove] = []
    for row in moves_np:
        # row[B_MOVE_IDX] is always 0 in single-position use
        from_sq = int(row[MOVE_FROM])
        to_sq = int(row[MOVE_TO])
        promo = int(row[MOVE_PROMO])
        flags = int(row[MOVE_FLAGS])
        out.append(SingleMove(from_sq=from_sq, to_sq=to_sq, promo=promo, flags=flags))
    return out


def generate_moves_batch(
    piece_batch: Sequence[Sequence[int]] | np.ndarray,
    color_batch: Sequence[Sequence[int]] | np.ndarray,
    stm_batch: Sequence[int] | np.ndarray,
) -> List[Move]:
    """
    Generate pseudo-legal moves for a batch of boards.

    Args:
        piece_batch: (N,64) or (64,)
        color_batch: (N,64) or (64,)
        stm_batch:   scalar 0/1 or (N,) array of 0/1 (synchronous batches recommended)

    Returns:
        List[Move] where each Move has board_idx, from_sq, to_sq, promo, flags.
    """
    piece_np, color_np = _normalize_board_batch(piece_batch, color_batch)
    N = piece_np.shape[0]
    stm_np = _normalize_stm_batch(stm_batch, N=N)

    piece_xp = xp.asarray(piece_np, dtype=xp.int8)
    color_xp = xp.asarray(color_np, dtype=xp.int8)
    stm_xp = xp.asarray(stm_np, dtype=xp.int8)

    moves_xp = _core_generate_moves_batch(piece_xp, color_xp, stm_xp)
    moves_np = _to_numpy(moves_xp)

    out: List[Move] = []
    for row in moves_np:
        idx = int(row[MOVE_IDX])
        from_sq = int(row[MOVE_FROM])
        to_sq = int(row[MOVE_TO])
        promo = int(row[MOVE_PROMO])
        flags = int(row[MOVE_FLAGS])
        out.append(
            Move(
                board_idx=idx,
                from_sq=from_sq,
                to_sq=to_sq,
                promo=promo,
                flags=flags,
            )
        )
    return out


# =====================================================================
# Convenience — backend info
# =====================================================================

def backend_name() -> str:
    """Human-readable backend description for logging/diagnostics."""
    if GPU:
        return "GPU (CuPy)"
    return "CPU (NumPy + Numba)"
