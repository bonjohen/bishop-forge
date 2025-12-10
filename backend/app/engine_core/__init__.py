"""
BishopForge Engine Core - Accelerated Chess Compute

This package provides CPU/GPU-accelerated chess computation with automatic
backend detection and batch processing capabilities.

Public API:
    - xp: NumPy or CuPy (depending on GPU availability)
    - GPU: Boolean indicating if GPU is available
    - Engine: Single-board engine class (CPU or GPU)
    - compute_attack_maps_batch: Batch attack map computation
    - evaluate_batch: Batch position evaluation
    - generate_moves_batch: Batch move generation
"""

from .backend import xp, GPU, Engine
from .engine_batch import (
    compute_attack_maps_batch,
    evaluate_batch,
    generate_moves_batch,
)
from .moves import (
    MOVE_IDX,
    MOVE_FROM,
    MOVE_TO,
    MOVE_PROMO,
    MOVE_FLAGS,
)

__all__ = [
    "xp",
    "GPU",
    "Engine",
    "compute_attack_maps_batch",
    "evaluate_batch",
    "generate_moves_batch",
    "MOVE_IDX",
    "MOVE_FROM",
    "MOVE_TO",
    "MOVE_PROMO",
    "MOVE_FLAGS",
]

