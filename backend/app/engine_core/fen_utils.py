"""
FEN (Forsyth-Edwards Notation) conversion utilities.
Convert between FEN strings and engine's internal board representation.
"""

import numpy as np
from .chess_utils import (
    PIECE_NONE, PIECE_PAWN, PIECE_KNIGHT, PIECE_BISHOP,
    PIECE_ROOK, PIECE_QUEEN, PIECE_KING,
    COLOR_EMPTY, COLOR_WHITE, COLOR_BLACK
)


def fen_to_arrays(fen: str) -> tuple[np.ndarray, np.ndarray, int]:
    """
    Convert FEN to engine arrays.
    
    Args:
        fen: FEN string (e.g., "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    
    Returns:
        piece_arr: (64,) array of piece types
        color_arr: (64,) array of colors
        stm: side to move (0=white, 1=black)
    """
    parts = fen.split()
    position = parts[0]
    stm_char = parts[1] if len(parts) > 1 else 'w'
    
    piece_arr = np.zeros(64, dtype=np.int8)
    color_arr = np.full(64, COLOR_EMPTY, dtype=np.int8)
    
    # Piece character to type mapping
    piece_map = {
        'p': PIECE_PAWN, 'n': PIECE_KNIGHT, 'b': PIECE_BISHOP,
        'r': PIECE_ROOK, 'q': PIECE_QUEEN, 'k': PIECE_KING
    }
    
    # Parse position (FEN starts from rank 8, we start from rank 0)
    sq = 56  # Start at a8 (rank 7, file 0)
    for ch in position:
        if ch == '/':
            sq -= 16  # Move to next rank (down 2 ranks because we already moved forward)
        elif ch.isdigit():
            sq += int(ch)  # Skip empty squares
        else:
            # Determine piece type and color
            piece_type = piece_map[ch.lower()]
            color = COLOR_WHITE if ch.isupper() else COLOR_BLACK
            
            piece_arr[sq] = piece_type
            color_arr[sq] = color
            sq += 1
    
    stm = COLOR_WHITE if stm_char == 'w' else COLOR_BLACK
    
    return piece_arr, color_arr, stm


def arrays_to_fen(piece_arr: np.ndarray, color_arr: np.ndarray, stm: int) -> str:
    """
    Convert engine arrays to FEN.
    
    Args:
        piece_arr: (64,) array of piece types
        color_arr: (64,) array of colors
        stm: side to move (0=white, 1=black)
    
    Returns:
        FEN string (simplified, without castling/en passant/clocks)
    """
    piece_chars = {
        PIECE_PAWN: 'p', PIECE_KNIGHT: 'n', PIECE_BISHOP: 'b',
        PIECE_ROOK: 'r', PIECE_QUEEN: 'q', PIECE_KING: 'k'
    }
    
    fen_parts = []
    for rank in range(7, -1, -1):  # 8 to 1 (FEN starts from rank 8)
        empty_count = 0
        rank_str = ""
        
        for file in range(8):  # a to h
            sq = rank * 8 + file
            
            if piece_arr[sq] == PIECE_NONE:
                empty_count += 1
            else:
                if empty_count > 0:
                    rank_str += str(empty_count)
                    empty_count = 0
                
                ch = piece_chars[piece_arr[sq]]
                if color_arr[sq] == COLOR_WHITE:
                    ch = ch.upper()
                rank_str += ch
        
        if empty_count > 0:
            rank_str += str(empty_count)
        
        fen_parts.append(rank_str)
    
    position = '/'.join(fen_parts)
    stm_char = 'w' if stm == COLOR_WHITE else 'b'
    
    # Simplified FEN (no castling rights, en passant, or move counters)
    return f"{position} {stm_char} - - 0 1"


def fen_to_board_2d(fen: str) -> list[list[str | None]]:
    """
    Convert FEN to 2D board representation for display.
    
    Args:
        fen: FEN string
    
    Returns:
        8x8 list where board[rank][file] is piece character or None
        rank 0 = rank 8, rank 7 = rank 1 (display order)
    """
    parts = fen.split()
    position = parts[0]
    rows = position.split('/')
    
    board = []
    for row in rows:
        out_row = []
        for ch in row:
            if ch.isdigit():
                # Add empty squares
                for _ in range(int(ch)):
                    out_row.append(None)
            else:
                out_row.append(ch)
        board.append(out_row)
    
    return board


# Standard starting position FEN
STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

