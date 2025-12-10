# main_test.py

from .backend import xp, GPU
from .engine_batch import (
    compute_attack_maps_batch,
    evaluate_batch,
    generate_moves_batch,
)

print("Backend:", "GPU" if GPU else "CPU")

# Example: batch of 3 empty boards
N = 3
piece_arr_batch = xp.zeros((N, 64), dtype=xp.int8)
color_arr_batch = xp.full((N, 64), -1, dtype=xp.int8)
stm_batch = xp.zeros(N, dtype=xp.int8)

white, black = compute_attack_maps_batch(piece_arr_batch, color_arr_batch)
print("Attack maps OK:", white.shape, black.shape)

wo, wd, bo, bd = evaluate_batch(piece_arr_batch, color_arr_batch)
print("Eval OK:", wo, wd, bo, bd)

moves = generate_moves_batch(piece_arr_batch, color_arr_batch, stm_batch)
print("Moves OK:", moves.shape)

print("All good.")
