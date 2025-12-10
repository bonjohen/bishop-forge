# engine_cpu.py

import numpy as np
from numba import njit

class EngineCPU:
    """
    CPU backend using NumPy + Numba.
    Evaluates single boards (not batch).
    """

    @staticmethod
    @njit(cache=True)
    def compute_attack_maps(piece_arr, color_arr):
        # Placeholder correct shape
        white_att = np.zeros(64, dtype=np.bool_)
        black_att = np.zeros(64, dtype=np.bool_)
        return white_att, black_att

    @staticmethod
    @njit(cache=True)
    def evaluate(piece_arr, color_arr):
        # Offensive/defensive values (placeholder)
        return 0, 0, 0, 0

    @staticmethod
    @njit(cache=True)
    def generate_pseudo_legal_moves(piece_arr, color_arr, stm):
        # Return empty move list: shape (0,4)
        return np.empty((0,4), dtype=np.int16)
