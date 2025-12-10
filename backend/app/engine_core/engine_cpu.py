# engine_cpu.py

import numpy as np
from numba import njit
from .chess_utils import (
    PIECE_NONE, PIECE_PAWN, PIECE_KNIGHT, PIECE_BISHOP,
    PIECE_ROOK, PIECE_QUEEN, PIECE_KING,
    COLOR_WHITE, COLOR_BLACK,
    get_knight_attacks, get_king_attacks, get_pawn_attacks,
    get_bishop_attacks, get_rook_attacks, get_queen_attacks,
    get_rank, get_file
)


@njit(cache=True)
def _evaluate_king_safety(king_sq, color, piece_arr, color_arr):
    """
    Evaluate king safety.

    Args:
        king_sq: King square (0-63)
        color: King color (0=white, 1=black)
        piece_arr: Piece array
        color_arr: Color array

    Returns:
        King safety score (higher is safer)
    """
    safety = 100  # Base safety

    king_rank = get_rank(king_sq)
    king_file = get_file(king_sq)

    # Pawn shield bonus
    if color == COLOR_WHITE:
        # Check for pawns in front of king
        for file_offset in (-1, 0, 1):
            check_file = king_file + file_offset
            if 0 <= check_file < 8:
                # Check rank in front of king
                if king_rank < 7:
                    check_sq = (king_rank + 1) * 8 + check_file
                    if piece_arr[check_sq] == PIECE_PAWN and color_arr[check_sq] == COLOR_WHITE:
                        safety += 10
    else:  # BLACK
        # Check for pawns in front of king
        for file_offset in (-1, 0, 1):
            check_file = king_file + file_offset
            if 0 <= check_file < 8:
                # Check rank in front of king
                if king_rank > 0:
                    check_sq = (king_rank - 1) * 8 + check_file
                    if piece_arr[check_sq] == PIECE_PAWN and color_arr[check_sq] == COLOR_BLACK:
                        safety += 10

    return safety

class EngineCPU:
    """
    CPU backend using NumPy + Numba.
    Evaluates single boards (not batch).
    """

    @staticmethod
    @njit(cache=True)
    def compute_attack_maps(piece_arr, color_arr):
        """
        Compute attack maps for both sides.

        Args:
            piece_arr: (64,) array of piece types
            color_arr: (64,) array of colors

        Returns:
            (white_att, black_att): Both (64,) bool arrays
        """
        white_att = np.zeros(64, dtype=np.bool_)
        black_att = np.zeros(64, dtype=np.bool_)

        for sq in range(64):
            if piece_arr[sq] == PIECE_NONE:
                continue

            piece = piece_arr[sq]
            color = color_arr[sq]

            # Get attacked squares based on piece type
            if piece == PIECE_PAWN:
                attacks = get_pawn_attacks(sq, color)
            elif piece == PIECE_KNIGHT:
                attacks = get_knight_attacks(sq)
            elif piece == PIECE_BISHOP:
                attacks = get_bishop_attacks(sq, piece_arr)
            elif piece == PIECE_ROOK:
                attacks = get_rook_attacks(sq, piece_arr)
            elif piece == PIECE_QUEEN:
                attacks = get_queen_attacks(sq, piece_arr)
            elif piece == PIECE_KING:
                attacks = get_king_attacks(sq)
            else:
                continue

            # Mark attacked squares
            for target in attacks:
                if color == COLOR_WHITE:
                    white_att[target] = True
                else:
                    black_att[target] = True

        return white_att, black_att

    @staticmethod
    @njit(cache=True)
    def evaluate(piece_arr, color_arr):
        """
        Evaluate a position.

        Args:
            piece_arr: (64,) array of piece types
            color_arr: (64,) array of colors

        Returns:
            (white_off, white_def, black_off, black_def): Offensive and defensive scores
        """
        # Material values
        piece_values = np.array([0, 100, 320, 330, 500, 900, 0], dtype=np.int32)

        white_material = 0
        black_material = 0
        white_mobility = 0
        black_mobility = 0
        white_king_sq = -1
        black_king_sq = -1

        # Single pass: count material and find kings
        for sq in range(64):
            if piece_arr[sq] == PIECE_NONE:
                continue

            piece = piece_arr[sq]
            color = color_arr[sq]
            value = piece_values[piece]

            if color == COLOR_WHITE:
                white_material += value
                if piece == PIECE_KING:
                    white_king_sq = sq
            else:
                black_material += value
                if piece == PIECE_KING:
                    black_king_sq = sq

        # Mobility: count pseudo-legal moves
        for sq in range(64):
            if piece_arr[sq] == PIECE_NONE:
                continue

            piece = piece_arr[sq]
            color = color_arr[sq]

            # Count moves for this piece
            move_count = 0

            if piece == PIECE_PAWN:
                attacks = get_pawn_attacks(sq, color)
                move_count = len(attacks)
                # Add forward moves
                if color == COLOR_WHITE:
                    if sq + 8 < 64 and piece_arr[sq + 8] == PIECE_NONE:
                        move_count += 1
                else:
                    if sq - 8 >= 0 and piece_arr[sq - 8] == PIECE_NONE:
                        move_count += 1
            elif piece == PIECE_KNIGHT:
                attacks = get_knight_attacks(sq)
                move_count = len(attacks)
            elif piece == PIECE_BISHOP:
                attacks = get_bishop_attacks(sq, piece_arr)
                move_count = len(attacks)
            elif piece == PIECE_ROOK:
                attacks = get_rook_attacks(sq, piece_arr)
                move_count = len(attacks)
            elif piece == PIECE_QUEEN:
                attacks = get_queen_attacks(sq, piece_arr)
                move_count = len(attacks)
            elif piece == PIECE_KING:
                attacks = get_king_attacks(sq)
                move_count = len(attacks)

            if color == COLOR_WHITE:
                white_mobility += move_count
            else:
                black_mobility += move_count

        # King safety evaluation
        white_king_safety = 0
        black_king_safety = 0

        if white_king_sq >= 0:
            white_king_safety = _evaluate_king_safety(white_king_sq, COLOR_WHITE, piece_arr, color_arr)

        if black_king_sq >= 0:
            black_king_safety = _evaluate_king_safety(black_king_sq, COLOR_BLACK, piece_arr, color_arr)

        # Combine scores
        white_off = white_material + white_mobility
        white_def = white_king_safety
        black_off = black_material + black_mobility
        black_def = black_king_safety

        return white_off, white_def, black_off, black_def

    @staticmethod
    @njit(cache=True)
    def generate_pseudo_legal_moves(piece_arr, color_arr, stm):
        """
        Generate pseudo-legal moves for the side to move.

        Args:
            piece_arr: (64,) array of piece types
            color_arr: (64,) array of colors
            stm: Side to move (0=white, 1=black)

        Returns:
            (M, 4) array where each row is [from_sq, to_sq, promo, flags]
        """
        # Pre-allocate buffer (max ~218 moves in chess, use 256 for safety)
        moves_buffer = np.empty((256, 4), dtype=np.int16)
        move_count = 0

        for sq in range(64):
            if color_arr[sq] != stm:
                continue

            piece = piece_arr[sq]

            if piece == PIECE_PAWN:
                move_count = _add_pawn_moves(
                    sq, stm, piece_arr, color_arr, moves_buffer, move_count
                )
            elif piece == PIECE_KNIGHT:
                move_count = _add_knight_moves(
                    sq, stm, piece_arr, color_arr, moves_buffer, move_count
                )
            elif piece == PIECE_BISHOP:
                move_count = _add_bishop_moves(
                    sq, stm, piece_arr, color_arr, moves_buffer, move_count
                )
            elif piece == PIECE_ROOK:
                move_count = _add_rook_moves(
                    sq, stm, piece_arr, color_arr, moves_buffer, move_count
                )
            elif piece == PIECE_QUEEN:
                move_count = _add_queen_moves(
                    sq, stm, piece_arr, color_arr, moves_buffer, move_count
                )
            elif piece == PIECE_KING:
                move_count = _add_king_moves(
                    sq, stm, piece_arr, color_arr, moves_buffer, move_count
                )

        # Return only filled portion
        return moves_buffer[:move_count]


# Move generation helper functions

# Move flags
FLAG_NORMAL = 0
FLAG_CAPTURE = 1
FLAG_EN_PASSANT = 2
FLAG_CASTLING = 4
FLAG_DOUBLE_PUSH = 8


@njit(cache=True)
def _add_pawn_moves(sq, stm, piece_arr, color_arr, moves_buffer, move_count):
    """Add pawn moves to buffer."""
    sq_rank = get_rank(sq)
    sq_file = get_file(sq)

    if stm == COLOR_WHITE:
        # Forward one square
        target = sq + 8
        if target < 64 and piece_arr[target] == PIECE_NONE:
            # Check for promotion
            if sq_rank == 6:  # 7th rank
                # Add all promotion moves
                for promo in (PIECE_KNIGHT, PIECE_BISHOP, PIECE_ROOK, PIECE_QUEEN):
                    moves_buffer[move_count] = np.array([sq, target, promo, FLAG_NORMAL], dtype=np.int16)
                    move_count += 1
            else:
                moves_buffer[move_count] = np.array([sq, target, 0, FLAG_NORMAL], dtype=np.int16)
                move_count += 1

                # Forward two squares from starting position
                if sq_rank == 1:  # 2nd rank
                    target2 = sq + 16
                    if piece_arr[target2] == PIECE_NONE:
                        moves_buffer[move_count] = np.array([sq, target2, 0, FLAG_DOUBLE_PUSH], dtype=np.int16)
                        move_count += 1

        # Captures
        for file_offset in (-1, 1):
            target_file = sq_file + file_offset
            if 0 <= target_file < 8:
                target = sq + 8 + file_offset
                if target < 64 and color_arr[target] == COLOR_BLACK:
                    # Check for promotion
                    if sq_rank == 6:  # 7th rank
                        for promo in (PIECE_KNIGHT, PIECE_BISHOP, PIECE_ROOK, PIECE_QUEEN):
                            moves_buffer[move_count] = np.array([sq, target, promo, FLAG_CAPTURE], dtype=np.int16)
                            move_count += 1
                    else:
                        moves_buffer[move_count] = np.array([sq, target, 0, FLAG_CAPTURE], dtype=np.int16)
                        move_count += 1

    else:  # BLACK
        # Forward one square
        target = sq - 8
        if target >= 0 and piece_arr[target] == PIECE_NONE:
            # Check for promotion
            if sq_rank == 1:  # 2nd rank
                for promo in (PIECE_KNIGHT, PIECE_BISHOP, PIECE_ROOK, PIECE_QUEEN):
                    moves_buffer[move_count] = np.array([sq, target, promo, FLAG_NORMAL], dtype=np.int16)
                    move_count += 1
            else:
                moves_buffer[move_count] = np.array([sq, target, 0, FLAG_NORMAL], dtype=np.int16)
                move_count += 1

                # Forward two squares from starting position
                if sq_rank == 6:  # 7th rank
                    target2 = sq - 16
                    if piece_arr[target2] == PIECE_NONE:
                        moves_buffer[move_count] = np.array([sq, target2, 0, FLAG_DOUBLE_PUSH], dtype=np.int16)
                        move_count += 1

        # Captures
        for file_offset in (-1, 1):
            target_file = sq_file + file_offset
            if 0 <= target_file < 8:
                target = sq - 8 + file_offset
                if target >= 0 and color_arr[target] == COLOR_WHITE:
                    # Check for promotion
                    if sq_rank == 1:  # 2nd rank
                        for promo in (PIECE_KNIGHT, PIECE_BISHOP, PIECE_ROOK, PIECE_QUEEN):
                            moves_buffer[move_count] = np.array([sq, target, promo, FLAG_CAPTURE], dtype=np.int16)
                            move_count += 1
                    else:
                        moves_buffer[move_count] = np.array([sq, target, 0, FLAG_CAPTURE], dtype=np.int16)
                        move_count += 1

    return move_count


@njit(cache=True)
def _add_knight_moves(sq, stm, piece_arr, color_arr, moves_buffer, move_count):
    """Add knight moves to buffer."""
    attacks = get_knight_attacks(sq)

    for target in attacks:
        if color_arr[target] == stm:
            continue  # Can't capture own piece

        flags = FLAG_CAPTURE if color_arr[target] != -1 else FLAG_NORMAL
        moves_buffer[move_count] = np.array([sq, target, 0, flags], dtype=np.int16)
        move_count += 1

    return move_count


@njit(cache=True)
def _add_bishop_moves(sq, stm, piece_arr, color_arr, moves_buffer, move_count):
    """Add bishop moves to buffer."""
    attacks = get_bishop_attacks(sq, piece_arr)

    for target in attacks:
        if color_arr[target] == stm:
            continue  # Can't capture own piece

        flags = FLAG_CAPTURE if color_arr[target] != -1 else FLAG_NORMAL
        moves_buffer[move_count] = np.array([sq, target, 0, flags], dtype=np.int16)
        move_count += 1

    return move_count


@njit(cache=True)
def _add_rook_moves(sq, stm, piece_arr, color_arr, moves_buffer, move_count):
    """Add rook moves to buffer."""
    attacks = get_rook_attacks(sq, piece_arr)

    for target in attacks:
        if color_arr[target] == stm:
            continue  # Can't capture own piece

        flags = FLAG_CAPTURE if color_arr[target] != -1 else FLAG_NORMAL
        moves_buffer[move_count] = np.array([sq, target, 0, flags], dtype=np.int16)
        move_count += 1

    return move_count


@njit(cache=True)
def _add_queen_moves(sq, stm, piece_arr, color_arr, moves_buffer, move_count):
    """Add queen moves to buffer."""
    attacks = get_queen_attacks(sq, piece_arr)

    for target in attacks:
        if color_arr[target] == stm:
            continue  # Can't capture own piece

        flags = FLAG_CAPTURE if color_arr[target] != -1 else FLAG_NORMAL
        moves_buffer[move_count] = np.array([sq, target, 0, flags], dtype=np.int16)
        move_count += 1

    return move_count


@njit(cache=True)
def _add_king_moves(sq, stm, piece_arr, color_arr, moves_buffer, move_count):
    """Add king moves to buffer."""
    attacks = get_king_attacks(sq)

    for target in attacks:
        if color_arr[target] == stm:
            continue  # Can't capture own piece

        flags = FLAG_CAPTURE if color_arr[target] != -1 else FLAG_NORMAL
        moves_buffer[move_count] = np.array([sq, target, 0, flags], dtype=np.int16)
        move_count += 1

    return move_count
