# engine_gpu.py
"""
GPU backend using CuPy.
For single-board operations, we convert to NumPy and use CPU implementation.
For batch operations, we use native GPU kernels for maximum performance.
"""

import cupy as cp
import numpy as np

# Import CPU implementation to use for single-board operations
from .engine_cpu import EngineCPU


class EngineGPU:
    """
    GPU backend using CuPy.
    Single-board operations delegate to CPU.
    Batch operations use native GPU kernels for performance.
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

    # ========================================================================
    # BATCH OPERATIONS (Native GPU Implementation)
    # ========================================================================

    @staticmethod
    def evaluate_batch(piece_batch, color_batch):
        """
        Evaluate batch of positions using GPU vectorization.

        Args:
            piece_batch: CuPy array (N, 64) - piece types
            color_batch: CuPy array (N, 64) - piece colors

        Returns:
            (white_off, white_def, black_off, black_def): CuPy arrays (N,)
        """
        N = piece_batch.shape[0]

        # Material counting (vectorized)
        # Piece values: [Empty, Pawn, Knight, Bishop, Rook, Queen, King]
        piece_values = cp.array([0, 100, 320, 330, 500, 900, 0], dtype=cp.int32)

        # Broadcast indexing: piece_batch (N, 64) -> material (N, 64)
        material = piece_values[piece_batch]

        # Create masks for white and black pieces
        white_mask = (color_batch == 0).astype(cp.int32)
        black_mask = (color_batch == 1).astype(cp.int32)

        # Sum material for each side (N,)
        white_material = cp.sum(material * white_mask, axis=1)
        black_material = cp.sum(material * black_mask, axis=1)

        # Mobility counting (simplified: count pieces that can move)
        # For now, use piece count as proxy for mobility
        # TODO: Implement proper move counting on GPU
        white_mobility = cp.sum(white_mask * (piece_batch > 0), axis=1) * 10
        black_mobility = cp.sum(black_mask * (piece_batch > 0), axis=1) * 10

        # King safety (simplified: count pawns near king)
        white_king_safety = _evaluate_king_safety_batch_gpu(piece_batch, color_batch, 0)
        black_king_safety = _evaluate_king_safety_batch_gpu(piece_batch, color_batch, 1)

        # Combine scores
        white_off = white_material + white_mobility
        white_def = white_king_safety
        black_off = black_material + black_mobility
        black_def = black_king_safety

        return white_off, white_def, black_off, black_def

    @staticmethod
    def compute_attack_maps_batch(piece_batch, color_batch):
        """
        Compute attack maps for batch of positions using GPU kernels.

        Args:
            piece_batch: CuPy array (N, 64)
            color_batch: CuPy array (N, 64)

        Returns:
            (white_att, black_att): CuPy bool arrays (N, 64)
        """
        N = piece_batch.shape[0]
        white_att = cp.zeros((N, 64), dtype=cp.bool_)
        black_att = cp.zeros((N, 64), dtype=cp.bool_)

        # Compute attacks for each piece type
        _compute_pawn_attacks_batch_gpu(piece_batch, color_batch, white_att, black_att)
        _compute_knight_attacks_batch_gpu(piece_batch, color_batch, white_att, black_att)
        _compute_king_attacks_batch_gpu(piece_batch, color_batch, white_att, black_att)
        _compute_sliding_attacks_batch_gpu(piece_batch, color_batch, white_att, black_att)

        return white_att, black_att

    @staticmethod
    def generate_moves_batch(piece_batch, color_batch, stm_batch):
        """
        Generate moves for batch of positions using GPU kernels.

        Args:
            piece_batch: CuPy array (N, 64)
            color_batch: CuPy array (N, 64)
            stm_batch: CuPy array (N,) - side to move for each position

        Returns:
            moves: CuPy array (M, 5) where M = total moves across all boards
                   Columns: [board_idx, from_sq, to_sq, promo, flags]
        """
        N = piece_batch.shape[0]

        # Pre-allocate buffer (max 256 moves per position)
        max_moves = N * 256
        moves_buffer = cp.zeros((max_moves, 5), dtype=cp.int16)
        move_counts = cp.zeros(N, dtype=cp.int32)

        # Generate moves using GPU kernel
        _generate_moves_batch_gpu(
            piece_batch, color_batch, stm_batch,
            moves_buffer, move_counts
        )

        # Compact: remove empty slots
        total_moves = int(cp.sum(move_counts))
        if total_moves == 0:
            return cp.zeros((0, 5), dtype=cp.int16)

        # Use prefix sum for compaction
        offsets = cp.cumsum(move_counts) - move_counts
        moves = cp.empty((total_moves, 5), dtype=cp.int16)
        _compact_moves_gpu(moves_buffer, move_counts, offsets, moves, N)

        return moves


# ============================================================================
# GPU Helper Functions and Kernels
# ============================================================================

def _evaluate_king_safety_batch_gpu(piece_batch, color_batch, side):
    """
    Evaluate king safety for a batch of positions (vectorized).

    Args:
        piece_batch: CuPy array (N, 64)
        color_batch: CuPy array (N, 64)
        side: 0 for white, 1 for black

    Returns:
        CuPy array (N,) - king safety scores
    """
    N = piece_batch.shape[0]

    # Find king positions (piece == 6, color == side)
    king_mask = (piece_batch == 6) & (color_batch == side)

    # For simplicity, count pawns of same color (pawn shield)
    pawn_mask = (piece_batch == 1) & (color_batch == side)
    pawn_count = cp.sum(pawn_mask.astype(cp.int32), axis=1)

    # Simple king safety: 15 points per pawn
    return pawn_count * 15


# ============================================================================
# CUDA Kernels for Attack Maps (Lazy-loaded)
# ============================================================================

# Kernel cache (loaded on first use)
_knight_attacks_kernel = None
_king_attacks_kernel = None
_pawn_attacks_kernel = None


def _get_knight_attacks_kernel():
    """Lazy-load knight attacks kernel."""
    global _knight_attacks_kernel
    if _knight_attacks_kernel is None:
        _knight_attacks_kernel = cp.RawKernel(r'''
extern "C" __global__
void knight_attacks(
    const char* piece,
    const char* color,
    bool* white_att,
    bool* black_att,
    int n_boards
) {
    int board_idx = blockIdx.x;
    int sq = threadIdx.x;

    if (board_idx >= n_boards || sq >= 64) return;

    int offset = board_idx * 64;
    if (piece[offset + sq] != 2) return;  // Not a knight

    // Knight move offsets
    const int offsets[8] = {-17, -15, -10, -6, 6, 10, 15, 17};
    const int file_diffs[8] = {-1, 1, -2, 2, 2, -2, 1, -1};

    int sq_file = sq % 8;
    int sq_rank = sq / 8;

    for (int i = 0; i < 8; i++) {
        int target = sq + offsets[i];
        if (target < 0 || target >= 64) continue;

        int target_file = target % 8;
        int target_rank = target / 8;

        // Check file difference matches expected
        if (abs(target_file - sq_file) != abs(file_diffs[i])) continue;

        if (color[offset + sq] == 0) {
            white_att[offset + target] = true;
        } else {
            black_att[offset + target] = true;
        }
    }
}
''', 'knight_attacks')
    return _knight_attacks_kernel


def _get_king_attacks_kernel():
    """Lazy-load king attacks kernel."""
    global _king_attacks_kernel
    if _king_attacks_kernel is None:
        _king_attacks_kernel = cp.RawKernel(r'''
extern "C" __global__
void king_attacks(
    const char* piece,
    const char* color,
    bool* white_att,
    bool* black_att,
    int n_boards
) {
    int board_idx = blockIdx.x;
    int sq = threadIdx.x;

    if (board_idx >= n_boards || sq >= 64) return;

    int offset = board_idx * 64;
    if (piece[offset + sq] != 6) return;  // Not a king

    // King move offsets
    const int offsets[8] = {-9, -8, -7, -1, 1, 7, 8, 9};

    int sq_file = sq % 8;

    for (int i = 0; i < 8; i++) {
        int target = sq + offsets[i];
        if (target < 0 || target >= 64) continue;

        int target_file = target % 8;

        // Check for board wrap
        if (abs(target_file - sq_file) > 1) continue;

        if (color[offset + sq] == 0) {
            white_att[offset + target] = true;
        } else {
            black_att[offset + target] = true;
        }
    }
}
''', 'king_attacks')
    return _king_attacks_kernel


def _get_pawn_attacks_kernel():
    """Lazy-load pawn attacks kernel."""
    global _pawn_attacks_kernel
    if _pawn_attacks_kernel is None:
        _pawn_attacks_kernel = cp.RawKernel(r'''
extern "C" __global__
void pawn_attacks(
    const char* piece,
    const char* color,
    bool* white_att,
    bool* black_att,
    int n_boards
) {
    int board_idx = blockIdx.x;
    int sq = threadIdx.x;

    if (board_idx >= n_boards || sq >= 64) return;

    int offset = board_idx * 64;
    if (piece[offset + sq] != 1) return;  // Not a pawn

    int sq_file = sq % 8;
    int sq_rank = sq / 8;

    if (color[offset + sq] == 0) {  // White pawn
        // Attacks diagonally forward (rank + 1)
        if (sq_rank < 7) {
            if (sq_file > 0) {
                white_att[offset + sq + 7] = true;  // Up-left
            }
            if (sq_file < 7) {
                white_att[offset + sq + 9] = true;  // Up-right
            }
        }
    } else {  // Black pawn
        // Attacks diagonally forward (rank - 1)
        if (sq_rank > 0) {
            if (sq_file > 0) {
                black_att[offset + sq - 9] = true;  // Down-left
            }
            if (sq_file < 7) {
                black_att[offset + sq - 7] = true;  // Down-right
            }
        }
    }
}
''', 'pawn_attacks')
    return _pawn_attacks_kernel


def _compute_knight_attacks_batch_gpu(piece_batch, color_batch, white_att, black_att):
    """Launch knight attacks kernel."""
    N = piece_batch.shape[0]
    kernel = _get_knight_attacks_kernel()
    # RawKernel call: kernel((grid,), (block,), (args,))
    kernel(
        (N,), (64,),  # grid and block dimensions
        (piece_batch, color_batch, white_att, black_att, N)
    )


def _compute_king_attacks_batch_gpu(piece_batch, color_batch, white_att, black_att):
    """Launch king attacks kernel."""
    N = piece_batch.shape[0]
    kernel = _get_king_attacks_kernel()
    kernel(
        (N,), (64,),  # grid and block dimensions
        (piece_batch, color_batch, white_att, black_att, N)
    )


def _compute_pawn_attacks_batch_gpu(piece_batch, color_batch, white_att, black_att):
    """Launch pawn attacks kernel."""
    N = piece_batch.shape[0]
    kernel = _get_pawn_attacks_kernel()
    kernel(
        (N,), (64,),  # grid and block dimensions
        (piece_batch, color_batch, white_att, black_att, N)
    )


def _compute_sliding_attacks_batch_gpu(piece_batch, color_batch, white_att, black_att):
    """
    Compute sliding piece attacks (bishops, rooks, queens).
    For now, use CPU implementation per board (sliding pieces are complex on GPU).
    TODO: Implement proper ray-tracing CUDA kernel.
    """
    N = piece_batch.shape[0]

    # Convert to CPU, compute, convert back
    # This is a temporary solution - proper GPU implementation would use ray-tracing
    for i in range(N):
        piece_np = cp.asnumpy(piece_batch[i])
        color_np = cp.asnumpy(color_batch[i])

        # Compute sliding attacks on CPU
        for sq in range(64):
            piece = piece_np[sq]
            if piece == 0 or color_np[sq] == -1:
                continue

            color = color_np[sq]
            attacks = []

            if piece == 3:  # Bishop
                from .chess_utils import get_bishop_attacks
                attacks = get_bishop_attacks(sq, piece_np)
            elif piece == 4:  # Rook
                from .chess_utils import get_rook_attacks
                attacks = get_rook_attacks(sq, piece_np)
            elif piece == 5:  # Queen
                from .chess_utils import get_queen_attacks
                attacks = get_queen_attacks(sq, piece_np)

            # Mark attacked squares
            for target in attacks:
                if color == 0:
                    white_att[i, target] = True
                else:
                    black_att[i, target] = True


def _generate_moves_batch_gpu(piece_batch, color_batch, stm_batch, moves_buffer, move_counts):
    """
    Generate moves for batch (CPU fallback for now).
    TODO: Implement proper CUDA kernel for move generation.
    """
    N = piece_batch.shape[0]

    # For now, use CPU implementation per board
    offset = 0
    for i in range(N):
        piece_np = cp.asnumpy(piece_batch[i])
        color_np = cp.asnumpy(color_batch[i])
        stm = int(stm_batch[i])

        # Generate moves on CPU
        moves_np = EngineCPU.generate_pseudo_legal_moves(piece_np, color_np, stm)
        count = moves_np.shape[0]

        if count > 0:
            # Copy to buffer
            moves_buffer[offset:offset+count, 0] = i  # board_idx
            moves_buffer[offset:offset+count, 1:5] = cp.asarray(moves_np)
            move_counts[i] = count
            offset += count


def _compact_moves_gpu(moves_buffer, move_counts, offsets, moves, N):
    """
    Compact moves buffer by removing empty slots.
    Uses prefix sum offsets to determine where each board's moves go.
    """
    # Simple implementation: copy non-empty moves
    dest_idx = 0
    for i in range(N):
        count = int(move_counts[i])
        if count > 0:
            src_start = int(offsets[i])
            moves[dest_idx:dest_idx+count] = moves_buffer[src_start:src_start+count]
            dest_idx += count
