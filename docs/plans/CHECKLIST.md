# BishopForge Engine Implementation Checklist

## 📋 Plan 1: Chess Logic Implementation

### Attack Map Computation
- [ ] Implement `is_valid_square(sq)` helper
- [ ] Implement `get_rank(sq)` and `get_file(sq)` helpers
- [ ] Implement `make_square(rank, file)` helper
- [ ] Implement `ray_attacks()` for sliding pieces
- [ ] Implement pawn attack generation
- [ ] Implement knight attack generation
- [ ] Implement bishop attack generation (diagonal rays)
- [ ] Implement rook attack generation (horizontal/vertical rays)
- [ ] Implement queen attack generation (bishop + rook)
- [ ] Implement king attack generation
- [ ] Test: Empty board → all False
- [ ] Test: Single knight → 8 attacked squares
- [ ] Test: Rook on a1 → 14 attacked squares
- [ ] Test: Blocked rook → fewer attacked squares

### Position Evaluation
- [ ] Implement material counting (P=100, N=320, B=330, R=500, Q=900)
- [ ] Implement mobility calculation
- [ ] Implement king safety evaluation
  - [ ] Pawn shield bonus
  - [ ] Open file penalty
- [ ] Implement pawn structure evaluation
  - [ ] Doubled pawns penalty
  - [ ] Isolated pawns penalty
  - [ ] Passed pawns bonus
- [ ] Test: Starting position → balanced scores
- [ ] Test: Material advantage → higher offensive score
- [ ] Test: Exposed king → lower defensive score

### Move Generation
- [ ] Implement pawn move generation
  - [ ] Forward 1 square
  - [ ] Forward 2 squares (from starting rank)
  - [ ] Diagonal captures
  - [ ] Promotions (4 piece types)
  - [ ] En passant (placeholder for now)
- [ ] Implement knight move generation (8 L-shaped moves)
- [ ] Implement bishop move generation (diagonal rays)
- [ ] Implement rook move generation (horizontal/vertical rays)
- [ ] Implement queen move generation (bishop + rook)
- [ ] Implement king move generation
  - [ ] 8 adjacent squares
  - [ ] Castling (placeholder for now)
- [ ] Implement move flags (normal, capture, en passant, castling, double push)
- [ ] Test: Starting position → 20 legal moves
- [ ] Test: Knight on e4 → 8 possible moves
- [ ] Test: Pawn on 7th rank → 4 promotion moves

### GPU Implementation
- [ ] Port attack map computation to CuPy
- [ ] Port evaluation to CuPy
- [ ] Port move generation to CuPy
- [ ] Test: GPU results match CPU results

---

## 📋 Plan 2: Numba JIT Optimization

### Helper Functions
- [ ] Create `chess_utils.py` file
- [ ] Add `@njit(cache=True, inline='always')` to coordinate helpers
- [ ] Add `@njit(cache=True)` to `ray_attacks()`
- [ ] Verify all helpers are JIT-compiled

### Attack Map Optimization
- [ ] Pre-allocate attack arrays
- [ ] Use typed lists for better performance
- [ ] Pre-compute knight offsets as constant array
- [ ] Avoid Python objects in hot paths
- [ ] Benchmark: <5μs per position

### Move Generation Optimization
- [ ] Pre-allocate move buffer (256 moves max)
- [ ] Use counter instead of list append
- [ ] Separate functions for each piece type
- [ ] Unroll common patterns
- [ ] Benchmark: <10μs per position

### Evaluation Optimization
- [ ] Vectorize material counting
- [ ] Cache piece lists
- [ ] Avoid redundant computations
- [ ] Single pass through board
- [ ] Benchmark: <3μs per position

### Benchmark Suite
- [ ] Create `benchmark.py` file
- [ ] Implement `benchmark_attack_maps()`
- [ ] Implement `benchmark_move_generation()`
- [ ] Implement `benchmark_evaluation()`
- [ ] Add warmup phase for JIT compilation
- [ ] Report results in microseconds

### Testing
- [ ] Verify JIT-compiled code produces same results
- [ ] Measure speedup vs pure Python (target: 50-200x)
- [ ] Run regression tests

---

## 📋 Plan 3: CuPy GPU Acceleration

### Batch Attack Maps
- [ ] Implement `compute_attack_maps_batch()` in `engine_gpu.py`
- [ ] Create knight attacks kernel
- [ ] Create sliding attacks kernel (bishop, rook, queen)
- [ ] Create pawn attacks kernel
- [ ] Create king attacks kernel
- [ ] Configure kernel launch (grid/block sizes)
- [ ] Test: GPU batch matches CPU batch

### Batch Evaluation
- [ ] Implement `evaluate_batch()` in `engine_gpu.py`
- [ ] Vectorize material counting
- [ ] Implement mobility counting kernel
- [ ] Implement king safety kernel
- [ ] Test: GPU batch matches CPU batch

### Batch Move Generation
- [ ] Choose approach (pre-allocated buffer vs two-pass)
- [ ] Implement move counting kernel
- [ ] Implement move generation kernel
- [ ] Implement compaction kernel
- [ ] Test: GPU batch matches CPU batch

### Memory Management
- [ ] Minimize CPU↔GPU transfers
- [ ] Use memory pools for allocation reuse
- [ ] Batch transfers when possible
- [ ] Monitor memory usage

### Optimization
- [ ] Implement coalesced memory access
- [ ] Use shared memory for frequently accessed data
- [ ] Optimize occupancy (threads per block)
- [ ] Minimize branch divergence

### Testing
- [ ] Create `test_gpu.py` file
- [ ] Test GPU/CPU equivalence for all operations
- [ ] Benchmark batch size 100: >10x speedup
- [ ] Benchmark batch size 1000: >50x speedup

---

## 📋 Plan 4: Engine Integration

### FEN Conversion
- [ ] Create `fen_utils.py` file
- [ ] Implement `fen_to_arrays()` function
  - [ ] Parse position string
  - [ ] Parse side to move
  - [ ] Handle empty squares
  - [ ] Handle piece placement
- [ ] Implement `arrays_to_fen()` function
  - [ ] Convert piece array to FEN
  - [ ] Convert color array to FEN
  - [ ] Add side to move
- [ ] Test: Round-trip conversion (FEN → arrays → FEN)
- [ ] Test: Starting position FEN

### API Endpoints
- [ ] Create `routers/engine_info.py` file
- [ ] Implement `GET /api/engine/backend` endpoint
- [ ] Implement `POST /api/engine/evaluate` endpoint
- [ ] Register routes in `main.py`
- [ ] Test endpoints with curl/Postman

### Router Integration
- [ ] Add `USE_CUSTOM_ENGINE` environment variable
- [ ] Update `routers/analysis.py` to use custom engine
- [ ] Add feature flag logic
- [ ] Test: Custom engine path
- [ ] Test: Stockfish fallback path

### Integration Tests
- [ ] Create `tests/test_integration.py` file
- [ ] Test: Starting position evaluation
- [ ] Test: Move generation (20 moves)
- [ ] Test: Attack maps
- [ ] Test: Batch operations
- [ ] Test: End-to-end API call

### Documentation
- [ ] Update `docs/API.md` with new endpoints
- [ ] Document FEN conversion utilities
- [ ] Document feature flag usage
- [ ] Add examples for custom engine usage

---

## 🎯 Overall Success Criteria

### Correctness
- [ ] All unit tests pass (100% pass rate)
- [ ] All integration tests pass
- [ ] Known positions evaluated correctly
- [ ] Move generation matches python-chess

### Performance (CPU)
- [ ] Attack maps: <5μs per position
- [ ] Move generation: <10μs per position
- [ ] Evaluation: <3μs per position
- [ ] Total: <20μs per position

### Performance (GPU, batch size 100)
- [ ] Attack maps: >10x speedup vs CPU
- [ ] Move generation: >10x speedup vs CPU
- [ ] Evaluation: >10x speedup vs CPU

### Integration
- [ ] Custom engine accessible via API
- [ ] FEN conversion works correctly
- [ ] Feature flag allows engine switching
- [ ] Documentation complete

---

## 📝 Notes

- Check off items as you complete them
- Add notes for any deviations from the plan
- Update estimated effort if needed
- Document any blockers or issues

