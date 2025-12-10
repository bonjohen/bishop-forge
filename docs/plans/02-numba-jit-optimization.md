# Plan 2: Add Numba JIT Compilation for CPU Kernels

## Overview
Optimize CPU chess engine performance using Numba's JIT compilation features to achieve near-C performance for compute-intensive operations.

## Current State
- `engine_cpu.py` already has `@njit(cache=True)` decorators on main methods
- Placeholder implementations don't exercise Numba's capabilities
- No performance benchmarking infrastructure

## Numba Optimization Strategy

### 2.1 JIT Compilation Modes

**Current Usage**: `@njit(cache=True)`
- `njit` = "no-python" mode (fastest, pure machine code)
- `cache=True` = Cache compiled code to disk for faster subsequent runs

**Additional Options to Consider**:
```python
@njit(cache=True, fastmath=True, parallel=False)
```
- `fastmath=True`: Relaxed floating-point semantics (faster but less precise)
- `parallel=False`: Initially disable auto-parallelization (add later if needed)

### 2.2 Helper Functions to JIT-Compile

Create `backend/app/engine_core/chess_utils.py`:

```python
from numba import njit
import numpy as np

@njit(cache=True, inline='always')
def is_valid_square(sq):
    """Check if square index is valid (0-63)."""
    return 0 <= sq < 64

@njit(cache=True, inline='always')
def get_rank(sq):
    """Get rank (0-7) from square index."""
    return sq // 8

@njit(cache=True, inline='always')
def get_file(sq):
    """Get file (0-7) from square index."""
    return sq % 8

@njit(cache=True, inline='always')
def make_square(rank, file):
    """Create square index from rank and file."""
    return rank * 8 + file

@njit(cache=True)
def ray_attacks(sq, direction, piece_arr, color_arr):
    """
    Generate ray attacks in a direction until blocked.
    
    Args:
        sq: Starting square (0-63)
        direction: Offset (-9, -8, -7, -1, 1, 7, 8, 9)
        piece_arr: Piece array (64,)
        color_arr: Color array (64,)
    
    Returns:
        List of attacked squares
    """
    attacks = []
    current = sq + direction
    
    while is_valid_square(current):
        # Check if we've wrapped around the board
        if abs(get_file(current) - get_file(current - direction)) > 2:
            break
            
        attacks.append(current)
        
        # Stop if square is occupied
        if piece_arr[current] != 0:
            break
            
        current += direction
    
    return attacks
```

### 2.3 Optimizing Attack Map Computation

**Key Optimizations**:
1. **Inline small functions**: Use `inline='always'` for coordinate helpers
2. **Pre-allocate arrays**: Avoid dynamic resizing
3. **Use typed lists**: `numba.typed.List` for better performance
4. **Avoid Python objects**: Use only NumPy arrays and primitives

**Example Pattern**:
```python
@njit(cache=True)
def compute_attack_maps(piece_arr, color_arr):
    white_att = np.zeros(64, dtype=np.bool_)
    black_att = np.zeros(64, dtype=np.bool_)
    
    # Pre-compute knight offsets (constant)
    knight_offsets = np.array([-17, -15, -10, -6, 6, 10, 15, 17], dtype=np.int8)
    
    for sq in range(64):
        if piece_arr[sq] == 0:  # Empty square
            continue
            
        piece = piece_arr[sq]
        color = color_arr[sq]
        
        # Use if-elif chain (faster than dict lookup in Numba)
        if piece == 2:  # Knight
            for offset in knight_offsets:
                target = sq + offset
                if is_valid_square(target):
                    # Check for board wrap
                    if abs(get_file(target) - get_file(sq)) <= 2:
                        if color == 0:
                            white_att[target] = True
                        else:
                            black_att[target] = True
        # ... other pieces
    
    return white_att, black_att
```

### 2.4 Optimizing Move Generation

**Key Optimizations**:
1. **Pre-allocate move buffer**: Estimate max moves (~218 in chess)
2. **Use counter instead of list append**: Faster in Numba
3. **Unroll common patterns**: Separate loops for different piece types

**Example Pattern**:
```python
@njit(cache=True)
def generate_pseudo_legal_moves(piece_arr, color_arr, stm):
    # Pre-allocate buffer (max ~218 moves in chess)
    moves_buffer = np.empty((256, 4), dtype=np.int16)
    move_count = 0
    
    for sq in range(64):
        if color_arr[sq] != stm:
            continue
            
        piece = piece_arr[sq]
        
        if piece == 1:  # Pawn
            move_count = _add_pawn_moves(
                sq, stm, piece_arr, color_arr, moves_buffer, move_count
            )
        elif piece == 2:  # Knight
            move_count = _add_knight_moves(
                sq, stm, piece_arr, color_arr, moves_buffer, move_count
            )
        # ... other pieces
    
    # Return only filled portion
    return moves_buffer[:move_count]

@njit(cache=True)
def _add_pawn_moves(sq, stm, piece_arr, color_arr, moves_buffer, move_count):
    """Add pawn moves to buffer, return new move_count."""
    # Implementation...
    return move_count
```

### 2.5 Optimizing Evaluation

**Key Optimizations**:
1. **Vectorize material counting**: Use NumPy operations
2. **Cache piece lists**: Build once, reuse
3. **Avoid redundant computations**: Store intermediate results

**Example Pattern**:
```python
@njit(cache=True)
def evaluate(piece_arr, color_arr):
    # Material values (constant array)
    piece_values = np.array([0, 100, 320, 330, 500, 900, 0], dtype=np.int32)
    
    white_material = 0
    black_material = 0
    white_mobility = 0
    black_mobility = 0
    
    # Single pass through board
    for sq in range(64):
        if piece_arr[sq] == 0:
            continue
            
        piece = piece_arr[sq]
        color = color_arr[sq]
        value = piece_values[piece]
        
        if color == 0:
            white_material += value
            white_mobility += _count_piece_mobility(sq, piece, piece_arr, color_arr)
        else:
            black_material += value
            black_mobility += _count_piece_mobility(sq, piece, piece_arr, color_arr)
    
    # Combine scores
    white_off = white_material + white_mobility
    white_def = _evaluate_king_safety(0, piece_arr, color_arr)
    black_off = black_material + black_mobility
    black_def = _evaluate_king_safety(1, piece_arr, color_arr)
    
    return white_off, white_def, black_off, black_def
```

## Performance Benchmarking

### 2.6 Create Benchmark Suite
**File**: `backend/app/engine_core/benchmark.py`

```python
import time
import numpy as np
from .backend import Engine

def benchmark_attack_maps(n_iterations=10000):
    # Starting position
    piece_arr = create_starting_position()
    color_arr = create_starting_colors()
    
    start = time.perf_counter()
    for _ in range(n_iterations):
        Engine.compute_attack_maps(piece_arr, color_arr)
    end = time.perf_counter()
    
    avg_time = (end - start) / n_iterations * 1e6  # microseconds
    print(f"Attack maps: {avg_time:.2f} μs per call")

def benchmark_move_generation(n_iterations=10000):
    # Similar pattern
    pass

def benchmark_evaluation(n_iterations=10000):
    # Similar pattern
    pass

if __name__ == "__main__":
    print("Warming up JIT...")
    # Run once to trigger compilation
    benchmark_attack_maps(n_iterations=10)
    
    print("\nRunning benchmarks...")
    benchmark_attack_maps()
    benchmark_move_generation()
    benchmark_evaluation()
```

## Numba Best Practices

### Do's:
- ✅ Use NumPy arrays (not lists)
- ✅ Use primitive types (int, float, bool)
- ✅ Pre-allocate arrays when size is known
- ✅ Use `inline='always'` for tiny helper functions
- ✅ Cache compiled functions with `cache=True`
- ✅ Profile before optimizing

### Don'ts:
- ❌ Use Python lists, dicts, or sets
- ❌ Use string operations
- ❌ Call non-JIT Python functions
- ❌ Use exceptions for control flow
- ❌ Allocate arrays in tight loops

## Testing Strategy

1. **Correctness Tests**: Ensure JIT-compiled code produces same results as reference
2. **Performance Tests**: Verify speedup vs. pure Python
3. **Regression Tests**: Ensure optimizations don't break functionality

## Expected Performance Gains

- **Attack Maps**: 50-100x faster than pure Python
- **Move Generation**: 100-200x faster than pure Python
- **Evaluation**: 30-50x faster than pure Python
- **Overall**: Target <10μs per position for all operations combined

## Success Criteria
- [ ] All helper functions are JIT-compiled
- [ ] No Python object usage in hot paths
- [ ] Benchmark suite runs and reports performance
- [ ] Attack maps: <5μs per position
- [ ] Move generation: <10μs per position
- [ ] Evaluation: <3μs per position
- [ ] All tests pass with identical results to non-optimized version

