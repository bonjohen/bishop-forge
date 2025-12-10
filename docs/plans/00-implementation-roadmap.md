# BishopForge Engine Implementation Roadmap

## Overview
This roadmap outlines the implementation of a high-performance chess engine with CPU (Numba) and GPU (CuPy) acceleration for the BishopForge project.

## Current Status
✅ **Complete**:
- Project structure and architecture
- Public API wrapper (`app/engine.py`)
- Backend auto-detection (`engine_core/backend.py`)
- Batch processing infrastructure (`engine_core/engine_batch.py`)
- FastAPI routers and endpoints

🚧 **In Progress**:
- Chess logic implementation (placeholder methods exist)

❌ **Not Started**:
- Numba JIT optimization
- CuPy GPU kernels
- Full integration with routers

## Implementation Plans

### Plan 1: Chess Logic Implementation
**File**: `docs/plans/01-chess-logic-implementation.md`

**Objective**: Replace placeholder methods with actual chess logic

**Key Deliverables**:
- Attack map computation (all piece types)
- Position evaluation (material, mobility, king safety)
- Pseudo-legal move generation
- Helper functions for coordinate conversion and ray attacks

**Estimated Effort**: 26-38 hours

**Dependencies**: None

**Priority**: 🔴 **CRITICAL** - Must be completed first

---

### Plan 2: Numba JIT Optimization
**File**: `docs/plans/02-numba-jit-optimization.md`

**Objective**: Optimize CPU performance using Numba JIT compilation

**Key Deliverables**:
- JIT-compiled helper functions
- Optimized attack map computation
- Optimized move generation with pre-allocated buffers
- Performance benchmark suite
- 50-200x speedup vs pure Python

**Estimated Effort**: 16-24 hours

**Dependencies**: Plan 1 (Chess Logic)

**Priority**: 🟡 **HIGH** - Needed for production performance

---

### Plan 3: CuPy GPU Acceleration
**File**: `docs/plans/03-cupy-gpu-acceleration.md`

**Objective**: Implement GPU-accelerated batch operations

**Key Deliverables**:
- CuPy kernels for batch attack maps
- Vectorized batch evaluation
- GPU batch move generation
- Memory management optimization
- 10-100x speedup for large batches

**Estimated Effort**: 24-32 hours

**Dependencies**: Plan 1 (Chess Logic), Plan 2 (Numba - for reference implementation)

**Priority**: 🟢 **MEDIUM** - Optional but valuable for batch workloads

---

### Plan 4: Engine Integration
**File**: `docs/plans/04-engine-integration.md`

**Objective**: Integrate custom engine with FastAPI routers

**Key Deliverables**:
- FEN conversion utilities
- New engine info endpoints
- Feature flag for engine selection
- Integration tests
- Updated documentation

**Estimated Effort**: 12-16 hours

**Dependencies**: Plan 1 (Chess Logic)

**Priority**: 🟡 **HIGH** - Needed for end-to-end functionality

---

## Implementation Sequence

### Phase 1: Core Chess Logic (Week 1-2)
1. Implement Plan 1: Chess Logic Implementation
   - Start with attack maps (simplest)
   - Then move generation (most complex)
   - Finally evaluation (uses attack maps and moves)
2. Write comprehensive unit tests
3. Verify correctness against known positions

**Milestone**: All chess logic tests pass

---

### Phase 2: CPU Optimization (Week 3)
1. Implement Plan 2: Numba JIT Optimization
   - Add JIT decorators to helper functions
   - Optimize hot paths
   - Create benchmark suite
2. Profile and iterate on performance
3. Verify no regression in correctness

**Milestone**: <10μs per position for all operations

---

### Phase 3: Integration (Week 4)
1. Implement Plan 4: Engine Integration
   - Create FEN utilities
   - Add new endpoints
   - Write integration tests
2. Update documentation
3. End-to-end testing

**Milestone**: Custom engine accessible via API

---

### Phase 4: GPU Acceleration (Week 5-6) [Optional]
1. Implement Plan 3: CuPy GPU Acceleration
   - Start with simple vectorized operations
   - Add custom kernels for complex operations
   - Optimize memory transfers
2. Benchmark GPU vs CPU
3. Verify GPU/CPU equivalence

**Milestone**: >10x speedup for batch size 100+

---

## Testing Strategy

### Unit Tests
- **Location**: `backend/app/engine_core/test_*.py`
- **Coverage**: Each chess logic function
- **Approach**: Known positions with expected outputs

### Integration Tests
- **Location**: `backend/tests/test_integration.py`
- **Coverage**: End-to-end API calls
- **Approach**: FEN → evaluation → response

### Performance Tests
- **Location**: `backend/app/engine_core/benchmark.py`
- **Coverage**: All core operations
- **Metrics**: Time per operation, throughput

### Regression Tests
- **Approach**: Save results from reference implementation
- **Verify**: New optimizations produce identical results

---

## Success Metrics

### Correctness
- [ ] All unit tests pass (100% pass rate)
- [ ] Integration tests pass
- [ ] Known positions evaluated correctly
- [ ] Move generation matches chess.py for test positions

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

## Risk Mitigation

### Risk 1: Chess Logic Bugs
**Mitigation**: Extensive testing against python-chess library

### Risk 2: Performance Not Meeting Targets
**Mitigation**: Profile early, optimize hot paths, consider alternative algorithms

### Risk 3: GPU Memory Limitations
**Mitigation**: Implement batch size limits, add memory monitoring

### Risk 4: Integration Complexity
**Mitigation**: Incremental integration, feature flags for rollback

---

## Resources

### Documentation
- Numba documentation: https://numba.pydata.org/
- CuPy documentation: https://docs.cupy.dev/
- Chess programming wiki: https://www.chessprogramming.org/

### Tools
- Profiling: `cProfile`, `line_profiler`, `py-spy`
- GPU profiling: `nvprof`, `nsys`
- Testing: `pytest`, `hypothesis`

### Reference Implementations
- python-chess: For correctness verification
- Stockfish: For algorithm reference (C++)

---

## Next Steps

1. **Review plans** with team
2. **Set up development environment** (install Numba, optionally CuPy)
3. **Create feature branch** for implementation
4. **Start with Plan 1** (Chess Logic Implementation)
5. **Iterate** based on test results and performance metrics

---

## Estimated Total Effort
- **Minimum** (Plans 1, 2, 4): 54-78 hours (~2-3 weeks full-time)
- **Maximum** (All plans): 78-110 hours (~3-4 weeks full-time)

---

## Questions for Consideration

1. **GPU Priority**: Is GPU acceleration needed for MVP, or can it be deferred?
2. **Performance Targets**: Are the stated targets (<10μs CPU, >10x GPU) acceptable?
3. **Testing Coverage**: What level of test coverage is required (80%? 90%?)?
4. **Integration Approach**: Should we fully replace python-chess, or keep it as fallback?
5. **Deployment**: Will GPU be available in production environment?

