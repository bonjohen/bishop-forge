# engine_batch.py
"""
Batch operations for chess engine.
Uses native GPU batch methods when available, falls back to CPU loop otherwise.
"""

from .backend import xp, GPU, Engine as SingleEngine
from .moves import (
    MOVE_IDX, MOVE_FROM, MOVE_TO, MOVE_PROMO, MOVE_FLAGS
)

###########################################################################
# Batch Attack Maps
###########################################################################

def compute_attack_maps_batch(piece_arr_batch, color_arr_batch):
    """
    Compute attack maps for batch of positions.
    Uses native GPU batch method if available, otherwise loops over CPU.
    """
    # Use native GPU batch method if available
    if GPU and hasattr(SingleEngine, 'compute_attack_maps_batch'):
        return SingleEngine.compute_attack_maps_batch(piece_arr_batch, color_arr_batch)

    # Fall back to CPU loop
    N = piece_arr_batch.shape[0]
    white = xp.zeros((N, 64), dtype=xp.bool_)
    black = xp.zeros((N, 64), dtype=xp.bool_)

    for i in range(N):
        w, b = SingleEngine.compute_attack_maps(piece_arr_batch[i], color_arr_batch[i])
        white[i] = w
        black[i] = b

    return white, black


###########################################################################
# Batch Evaluation
###########################################################################

def evaluate_batch(piece_arr_batch, color_arr_batch):
    """
    Evaluate batch of positions.
    Uses native GPU batch method if available, otherwise loops over CPU.
    """
    # Use native GPU batch method if available
    if GPU and hasattr(SingleEngine, 'evaluate_batch'):
        return SingleEngine.evaluate_batch(piece_arr_batch, color_arr_batch)

    # Fall back to CPU loop
    N = piece_arr_batch.shape[0]
    white_off = xp.zeros(N, dtype=xp.int32)
    white_def = xp.zeros(N, dtype=xp.int32)
    black_off = xp.zeros(N, dtype=xp.int32)
    black_def = xp.zeros(N, dtype=xp.int32)

    for i in range(N):
        wo, wd, bo, bd = SingleEngine.evaluate(
            piece_arr_batch[i], color_arr_batch[i]
        )
        white_off[i] = int(wo)
        white_def[i] = int(wd)
        black_off[i] = int(bo)
        black_def[i] = int(bd)

    return white_off, white_def, black_off, black_def


###########################################################################
# Batch Move Generation
###########################################################################

def generate_moves_batch(piece_arr_batch, color_arr_batch, stm_batch):
    """
    Generate moves for batch of positions.
    Uses native GPU batch method if available, otherwise loops over CPU.
    """
    # Use native GPU batch method if available
    if GPU and hasattr(SingleEngine, 'generate_moves_batch'):
        return SingleEngine.generate_moves_batch(piece_arr_batch, color_arr_batch, stm_batch)

    # Fall back to CPU loop
    xp_local = xp
    moves_accum = []

    for i in range(piece_arr_batch.shape[0]):
        moves_single = SingleEngine.generate_pseudo_legal_moves(
            piece_arr_batch[i],
            color_arr_batch[i],
            int(stm_batch[i])
        )

        if moves_single.shape[0] == 0:
            continue

        out = xp_local.empty((moves_single.shape[0], 5), dtype=xp_local.int16)
        out[:, MOVE_IDX]   = i
        out[:, MOVE_FROM]  = moves_single[:, 0]
        out[:, MOVE_TO]    = moves_single[:, 1]
        out[:, MOVE_PROMO] = moves_single[:, 2]
        out[:, MOVE_FLAGS] = moves_single[:, 3]

        moves_accum.append(out)

    if not moves_accum:
        return xp_local.zeros((0,5), dtype=xp_local.int16)

    return xp_local.concatenate(moves_accum, axis=0)
