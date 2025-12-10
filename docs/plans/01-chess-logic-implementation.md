# Plan 1: Implement Actual Chess Logic in Placeholder Methods

## Overview
Replace placeholder implementations in `engine_cpu.py` and `engine_gpu.py` with actual chess logic for move generation, attack map computation, and position evaluation.

## Current State
- `engine_cpu.py`: Contains placeholder methods with `@njit` decorators returning empty/zero values
- `engine_gpu.py`: Contains placeholder methods returning empty/zero values
- Both implement: `compute_attack_maps()`, `evaluate()`, `generate_pseudo_legal_moves()`

## Board Representation
- **Piece Array** (64 elements, int8): Square indices 0-63 (a1=0, h1=7, a8=56, h8=63)
  - 0 = Empty, 1 = Pawn, 2 = Knight, 3 = Bishop, 4 = Rook, 5 = Queen, 6 = King
- **Color Array** (64 elements, int8): -1 = Empty, 0 = White, 1 = Black
- **Side to Move** (stm): 0 = White, 1 = Black

## Implementation Tasks

### 1.1 Attack Map Computation
**File**: `backend/app/engine_core/engine_cpu.py` (method: `compute_attack_maps`)

**Requirements**:
- Input: `piece_arr[64]`, `color_arr[64]`
- Output: `(white_att[64], black_att[64])` as bool arrays
- Mark squares attacked by each side (not occupied, but attacked)

**Algorithm**:
1. Initialize two bool arrays (64 elements) to False
2. For each square (0-63):
   - If empty, skip
   - Get piece type and color
   - Generate attack squares based on piece type:
     - **Pawn**: Diagonal attacks (different for white/black)
     - **Knight**: L-shaped moves (8 possible)
     - **Bishop**: Diagonal rays until blocked
     - **Rook**: Horizontal/vertical rays until blocked
     - **Queen**: Combination of bishop + rook
     - **King**: One square in all 8 directions
3. Mark attacked squares in appropriate color array

**Helper Functions Needed**:
- `is_valid_square(sq)`: Check if square index is 0-63
- `get_rank(sq)`, `get_file(sq)`: Extract rank/file from square index
- `make_square(rank, file)`: Create square index from rank/file
- `ray_attacks(sq, directions, piece_arr)`: Generate sliding piece attacks

### 1.2 Position Evaluation
**File**: `backend/app/engine_core/engine_cpu.py` (method: `evaluate`)

**Requirements**:
- Input: `piece_arr[64]`, `color_arr[64]`
- Output: `(white_off, white_def, black_off, black_def)` as integers
- Offensive = material + mobility, Defensive = king safety + pawn structure

**Algorithm**:
1. **Material Counting**:
   - Pawn = 100, Knight = 320, Bishop = 330, Rook = 500, Queen = 900
   - Sum for each color
2. **Mobility** (offensive):
   - Count pseudo-legal moves for each piece
   - Weight: 1 point per legal move
3. **King Safety** (defensive):
   - Pawn shield: +10 per pawn in front of king
   - Open files near king: -20 per open file
4. **Pawn Structure** (defensive):
   - Doubled pawns: -10 per doubled pawn
   - Isolated pawns: -15 per isolated pawn
   - Passed pawns: +20 per passed pawn

**Return**: `(white_off, white_def, black_off, black_def)`

### 1.3 Move Generation
**File**: `backend/app/engine_core/engine_cpu.py` (method: `generate_pseudo_legal_moves`)

**Requirements**:
- Input: `piece_arr[64]`, `color_arr[64]`, `stm` (0=white, 1=black)
- Output: NumPy array shape `(M, 4)` where M = number of moves
  - Column 0: from_square (0-63)
  - Column 1: to_square (0-63)
  - Column 2: promotion piece (0=none, 2=N, 3=B, 4=R, 5=Q)
  - Column 3: flags (0=normal, 1=capture, 2=en passant, 4=castling, 8=double pawn push)

**Algorithm**:
1. Create empty list to accumulate moves
2. For each square (0-63):
   - If color doesn't match stm, skip
   - Generate moves based on piece type:
     - **Pawn**: Forward 1/2, captures, promotions, en passant
     - **Knight**: 8 L-shaped moves
     - **Bishop**: Diagonal rays
     - **Rook**: Horizontal/vertical rays
     - **Queen**: Bishop + Rook moves
     - **King**: 8 adjacent squares + castling
3. For each target square:
   - Check if valid (on board)
   - Check if not occupied by same color
   - Add move to list with appropriate flags
4. Convert list to NumPy array `(M, 4)`

**Note**: This generates pseudo-legal moves (doesn't check if king is in check after move)

### 1.4 GPU Implementation
**File**: `backend/app/engine_core/engine_gpu.py`

**Strategy**:
- Implement same logic using CuPy arrays
- Use CuPy kernels for parallel computation where beneficial
- For initial implementation, can use same algorithms as CPU (CuPy will handle GPU execution)
- Later optimization: Write custom CUDA kernels for hot paths

**Key Differences**:
- Use `cp.zeros`, `cp.empty` instead of `np.zeros`, `np.empty`
- Use `cp.asnumpy()` only when returning to CPU
- Batch operations where possible (GPU excels at parallel work)

## Testing Strategy

### Unit Tests
Create `backend/app/engine_core/test_chess_logic.py`:
1. **Test Attack Maps**:
   - Empty board → all False
   - Single knight on e4 → 8 attacked squares
   - Rook on a1 → 14 attacked squares (7 horizontal + 7 vertical)
   - Blocked rook → fewer attacked squares
2. **Test Evaluation**:
   - Starting position → balanced scores
   - Material advantage → higher offensive score
   - Exposed king → lower defensive score
3. **Test Move Generation**:
   - Starting position → 20 legal moves for white
   - Knight on e4 → 8 possible moves (if unblocked)
   - Pawn on 7th rank → 4 promotion moves per capture/push

### Integration Tests
Use existing `main_test.py` to verify batch operations work correctly.

## Dependencies
- NumPy (already installed)
- Numba (already installed)
- CuPy (optional, for GPU)

## Estimated Effort
- Attack maps: 4-6 hours
- Evaluation: 6-8 hours
- Move generation: 8-12 hours
- GPU port: 4-6 hours
- Testing: 4-6 hours
- **Total**: 26-38 hours

## Success Criteria
- [ ] All three methods return non-placeholder values
- [ ] Attack maps correctly identify attacked squares
- [ ] Evaluation returns reasonable scores for test positions
- [ ] Move generation produces correct number of moves for known positions
- [ ] All unit tests pass
- [ ] GPU implementation produces same results as CPU

