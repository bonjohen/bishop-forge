# engine_gpu.py

import cupy as cp

class EngineGPU:
    """
    GPU backend using CuPy.
    Evaluates single boards (not batch).
    """

    @staticmethod
    def compute_attack_maps(piece_arr, color_arr):
        white = cp.zeros(64, dtype=cp.bool_)
        black = cp.zeros(64, dtype=cp.bool_)
        return white, black

    @staticmethod
    def evaluate(piece_arr, color_arr):
        # Four values (placeholder) - return Python ints for compatibility
        return (0, 0, 0, 0)

    @staticmethod
    def generate_pseudo_legal_moves(piece_arr, color_arr, stm):
        # Return empty move list: shape (0,4)
        return cp.zeros((0,4), dtype=cp.int16)
