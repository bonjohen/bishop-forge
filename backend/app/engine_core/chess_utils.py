"""
Chess utility functions for coordinate conversion and move generation.
All functions are JIT-compiled with Numba for performance.
"""

import numpy as np
from numba import njit

# Piece type constants
PIECE_NONE = 0
PIECE_PAWN = 1
PIECE_KNIGHT = 2
PIECE_BISHOP = 3
PIECE_ROOK = 4
PIECE_QUEEN = 5
PIECE_KING = 6

# Color constants
COLOR_EMPTY = -1
COLOR_WHITE = 0
COLOR_BLACK = 1


@njit(cache=True, inline='always')
def is_valid_square(sq):
    """Check if square index is valid (0-63)."""
    return 0 <= sq < 64


@njit(cache=True, inline='always')
def get_rank(sq):
    """Get rank (0-7) from square index. 0=rank 1, 7=rank 8."""
    return sq // 8


@njit(cache=True, inline='always')
def get_file(sq):
    """Get file (0-7) from square index. 0=file a, 7=file h."""
    return sq % 8


@njit(cache=True, inline='always')
def make_square(rank, file):
    """Create square index from rank and file."""
    return rank * 8 + file


@njit(cache=True, inline='always')
def abs_diff(a, b):
    """Absolute difference between two integers."""
    return a - b if a > b else b - a


@njit(cache=True)
def get_knight_attacks(sq):
    """
    Get all possible knight attack squares from a given square.
    
    Args:
        sq: Source square (0-63)
    
    Returns:
        Array of valid target squares
    """
    offsets = np.array([-17, -15, -10, -6, 6, 10, 15, 17], dtype=np.int8)
    attacks = []
    
    sq_rank = get_rank(sq)
    sq_file = get_file(sq)
    
    for offset in offsets:
        target = sq + offset
        if is_valid_square(target):
            target_rank = get_rank(target)
            target_file = get_file(target)
            # Check if move is valid (not wrapping around board)
            rank_diff = abs_diff(target_rank, sq_rank)
            file_diff = abs_diff(target_file, sq_file)
            if (rank_diff == 2 and file_diff == 1) or (rank_diff == 1 and file_diff == 2):
                attacks.append(target)
    
    return np.array(attacks, dtype=np.int8)


@njit(cache=True)
def get_king_attacks(sq):
    """
    Get all possible king attack squares from a given square.
    
    Args:
        sq: Source square (0-63)
    
    Returns:
        Array of valid target squares
    """
    offsets = np.array([-9, -8, -7, -1, 1, 7, 8, 9], dtype=np.int8)
    attacks = []
    
    sq_file = get_file(sq)
    
    for offset in offsets:
        target = sq + offset
        if is_valid_square(target):
            target_file = get_file(target)
            # Check for board wrap (file difference should be at most 1)
            if abs_diff(target_file, sq_file) <= 1:
                attacks.append(target)
    
    return np.array(attacks, dtype=np.int8)


@njit(cache=True)
def get_pawn_attacks(sq, color):
    """
    Get pawn attack squares (diagonal captures only, not forward moves).
    
    Args:
        sq: Source square (0-63)
        color: 0 for white, 1 for black
    
    Returns:
        Array of valid attack squares
    """
    attacks = []
    sq_file = get_file(sq)
    
    if color == COLOR_WHITE:
        # White pawns attack diagonally upward
        if sq_file > 0:  # Can attack left
            target = sq + 7
            if is_valid_square(target):
                attacks.append(target)
        if sq_file < 7:  # Can attack right
            target = sq + 9
            if is_valid_square(target):
                attacks.append(target)
    else:  # BLACK
        # Black pawns attack diagonally downward
        if sq_file > 0:  # Can attack left
            target = sq - 9
            if is_valid_square(target):
                attacks.append(target)
        if sq_file < 7:  # Can attack right
            target = sq - 7
            if is_valid_square(target):
                attacks.append(target)
    
    return np.array(attacks, dtype=np.int8)


@njit(cache=True)
def get_ray_attacks(sq, direction, piece_arr):
    """
    Generate ray attacks in a direction until blocked.

    Args:
        sq: Starting square (0-63)
        direction: Offset (-9, -8, -7, -1, 1, 7, 8, 9)
        piece_arr: Piece array (64,)

    Returns:
        Array of attacked squares in this direction
    """
    attacks = []
    sq_file = get_file(sq)
    current = sq + direction

    while is_valid_square(current):
        current_file = get_file(current)

        # Check for board wrap on horizontal/diagonal moves
        if direction in (-9, -1, 7):  # Moving left
            if current_file >= sq_file:  # Wrapped around
                break
        elif direction in (-7, 1, 9):  # Moving right
            if current_file <= sq_file:  # Wrapped around
                break

        attacks.append(current)

        # Stop if square is occupied
        if piece_arr[current] != PIECE_NONE:
            break

        sq_file = current_file
        current += direction

    return np.array(attacks, dtype=np.int8)


@njit(cache=True)
def get_bishop_attacks(sq, piece_arr):
    """Get all bishop attack squares (diagonal rays)."""
    attacks = []

    # Four diagonal directions
    for direction in (-9, -7, 7, 9):
        ray = get_ray_attacks(sq, direction, piece_arr)
        for target in ray:
            attacks.append(target)

    return np.array(attacks, dtype=np.int8)


@njit(cache=True)
def get_rook_attacks(sq, piece_arr):
    """Get all rook attack squares (horizontal/vertical rays)."""
    attacks = []

    # Four orthogonal directions
    for direction in (-8, -1, 1, 8):
        ray = get_ray_attacks(sq, direction, piece_arr)
        for target in ray:
            attacks.append(target)

    return np.array(attacks, dtype=np.int8)


@njit(cache=True)
def get_queen_attacks(sq, piece_arr):
    """Get all queen attack squares (bishop + rook)."""
    attacks = []

    # All eight directions
    for direction in (-9, -8, -7, -1, 1, 7, 8, 9):
        ray = get_ray_attacks(sq, direction, piece_arr)
        for target in ray:
            attacks.append(target)

    return np.array(attacks, dtype=np.int8)

