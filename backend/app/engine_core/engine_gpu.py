# engine_gpu.py
"""
GPU backend using CuPy.
For single-board operations, we convert to NumPy and use CPU implementation.
This file is primarily for future batch GPU operations.
"""

import cupy as cp
import numpy as np

# Import CPU implementation to use for single-board operations
from .engine_cpu import EngineCPU


class EngineGPU:
    """
    GPU backend using CuPy.
    For now, single-board operations delegate to CPU.
    Future: Implement batch operations with CUDA kernels.
    """

    @staticmethod
    def compute_attack_maps(piece_arr, color_arr):
        """
        Compute attack maps (delegates to CPU for single board).

        Args:
            piece_arr: CuPy array (64,)
            color_arr: CuPy array (64,)

        Returns:
            (white_att, black_att): CuPy bool arrays (64,)
        """
        # Convert to NumPy, compute on CPU, convert back
        piece_np = cp.asnumpy(piece_arr)
        color_np = cp.asnumpy(color_arr)

        white_np, black_np = EngineCPU.compute_attack_maps(piece_np, color_np)

        return cp.asarray(white_np), cp.asarray(black_np)

    @staticmethod
    def evaluate(piece_arr, color_arr):
        """
        Evaluate position (delegates to CPU for single board).

        Args:
            piece_arr: CuPy array (64,)
            color_arr: CuPy array (64,)

        Returns:
            (white_off, white_def, black_off, black_def): Python ints
        """
        # Convert to NumPy, compute on CPU
        piece_np = cp.asnumpy(piece_arr)
        color_np = cp.asnumpy(color_arr)

        return EngineCPU.evaluate(piece_np, color_np)

    @staticmethod
    def generate_pseudo_legal_moves(piece_arr, color_arr, stm):
        """
        Generate pseudo-legal moves (delegates to CPU for single board).

        Args:
            piece_arr: CuPy array (64,)
            color_arr: CuPy array (64,)
            stm: Side to move (0=white, 1=black)

        Returns:
            CuPy array (M, 4)
        """
        # Convert to NumPy, compute on CPU, convert back
        piece_np = cp.asnumpy(piece_arr)
        color_np = cp.asnumpy(color_arr)

        moves_np = EngineCPU.generate_pseudo_legal_moves(piece_np, color_np, stm)

        return cp.asarray(moves_np)
