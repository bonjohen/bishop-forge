# BishopForge Engine Implementation Plans

## 📋 Overview

This document provides a comprehensive guide to implementing the BishopForge chess engine with CPU and GPU acceleration. The implementation is divided into four detailed plans that build upon each other.

## 📁 Plan Documents

All detailed plans are located in `docs/plans/`:

### 🗺️ [00-implementation-roadmap.md](plans/00-implementation-roadmap.md)
**Master roadmap** covering the entire implementation sequence, timelines, success metrics, and risk mitigation strategies.

**Key Contents**:
- Implementation phases and sequence
- Testing strategy
- Success metrics
- Risk mitigation
- Estimated effort: 54-110 hours total

---

### 🔴 [01-chess-logic-implementation.md](plans/01-chess-logic-implementation.md)
**Priority: CRITICAL** - Must be completed first

**Objective**: Replace placeholder methods with actual chess logic

**Key Deliverables**:
- ✅ Attack map computation for all piece types
- ✅ Position evaluation (material, mobility, king safety, pawn structure)
- ✅ Pseudo-legal move generation
- ✅ Helper functions for coordinate conversion and ray attacks
- ✅ Comprehensive unit tests

**Estimated Effort**: 26-38 hours

**Board Representation**:
- Piece array (64 elements): 0=Empty, 1=Pawn, 2=Knight, 3=Bishop, 4=Rook, 5=Queen, 6=King
- Color array (64 elements): -1=Empty, 0=White, 1=Black
- Square indexing: 0=a1, 7=h1, 56=a8, 63=h8

---

### 🟡 [02-numba-jit-optimization.md](plans/02-numba-jit-optimization.md)
**Priority: HIGH** - Needed for production performance

**Objective**: Optimize CPU performance using Numba JIT compilation

**Key Deliverables**:
- ✅ JIT-compiled helper functions with `@njit` decorators
- ✅ Optimized attack map computation
- ✅ Optimized move generation with pre-allocated buffers
- ✅ Performance benchmark suite
- ✅ 50-200x speedup vs pure Python

**Estimated Effort**: 16-24 hours

**Performance Targets**:
- Attack maps: <5μs per position
- Move generation: <10μs per position
- Evaluation: <3μs per position
- **Total: <20μs per position**

**Dependencies**: Plan 1 (Chess Logic)

---

### 🟢 [03-cupy-gpu-acceleration.md](plans/03-cupy-gpu-acceleration.md)
**Priority: MEDIUM** - Optional but valuable for batch workloads

**Objective**: Implement GPU-accelerated batch operations using CuPy

**Key Deliverables**:
- ✅ CuPy kernels for batch attack maps
- ✅ Vectorized batch evaluation
- ✅ GPU batch move generation
- ✅ Memory management optimization
- ✅ 10-100x speedup for large batches

**Estimated Effort**: 24-32 hours

**Performance Targets**:
- Batch size 100: >10x speedup vs CPU
- Batch size 1000: >50x speedup vs CPU

**Dependencies**: Plan 1 (Chess Logic), Plan 2 (Numba - for reference)

**GPU Strategy**:
- Element-wise kernels for simple operations
- Raw CUDA kernels for complex operations
- Minimize CPU↔GPU memory transfers
- Use memory pools for allocation reuse

---

### 🟡 [04-engine-integration.md](plans/04-engine-integration.md)
**Priority: HIGH** - Needed for end-to-end functionality

**Objective**: Integrate custom engine with FastAPI routers

**Key Deliverables**:
- ✅ FEN conversion utilities (FEN ↔ internal arrays)
- ✅ New engine info endpoints (`/api/engine/backend`, `/api/engine/evaluate`)
- ✅ Feature flag for engine selection (custom vs Stockfish)
- ✅ Integration tests
- ✅ Updated API documentation

**Estimated Effort**: 12-16 hours

**Dependencies**: Plan 1 (Chess Logic)

**New Endpoints**:
```
GET  /api/engine/backend   - Get backend info (CPU/GPU)
POST /api/engine/evaluate  - Evaluate position with custom engine
```

---

## 🎯 Implementation Sequence

### Phase 1: Core Chess Logic (Week 1-2)
1. ✅ Implement attack maps
2. ✅ Implement move generation
3. ✅ Implement position evaluation
4. ✅ Write unit tests
5. ✅ Verify correctness

**Milestone**: All chess logic tests pass

### Phase 2: CPU Optimization (Week 3)
1. ✅ Add Numba JIT decorators
2. ✅ Optimize hot paths
3. ✅ Create benchmark suite
4. ✅ Profile and iterate

**Milestone**: <10μs per position

### Phase 3: Integration (Week 4)
1. ✅ Create FEN utilities
2. ✅ Add API endpoints
3. ✅ Write integration tests
4. ✅ Update documentation

**Milestone**: Custom engine accessible via API

### Phase 4: GPU Acceleration (Week 5-6) [Optional]
1. ✅ Implement vectorized operations
2. ✅ Add CUDA kernels
3. ✅ Optimize memory transfers
4. ✅ Benchmark GPU vs CPU

**Milestone**: >10x speedup for batch size 100+

---

## 🧪 Testing Strategy

### Unit Tests
- **Location**: `backend/app/engine_core/test_*.py`
- **Coverage**: Each chess logic function
- **Examples**: Known positions with expected outputs

### Integration Tests
- **Location**: `backend/tests/test_integration.py`
- **Coverage**: End-to-end API calls
- **Flow**: FEN → evaluation → response

### Performance Tests
- **Location**: `backend/app/engine_core/benchmark.py`
- **Metrics**: Time per operation, throughput
- **Targets**: See individual plans

---

## 📊 Success Criteria

### ✅ Correctness
- [ ] All unit tests pass (100% pass rate)
- [ ] Integration tests pass
- [ ] Known positions evaluated correctly
- [ ] Move generation matches python-chess for test positions

### ⚡ Performance (CPU)
- [ ] Attack maps: <5μs per position
- [ ] Move generation: <10μs per position
- [ ] Evaluation: <3μs per position

### 🚀 Performance (GPU, batch size 100)
- [ ] Attack maps: >10x speedup vs CPU
- [ ] Move generation: >10x speedup vs CPU
- [ ] Evaluation: >10x speedup vs CPU

### 🔌 Integration
- [ ] Custom engine accessible via API
- [ ] FEN conversion works correctly
- [ ] Feature flag allows engine switching
- [ ] Documentation complete

---

## 🛠️ Quick Start

1. **Review the roadmap**: Read `00-implementation-roadmap.md`
2. **Start with Plan 1**: Implement chess logic first
3. **Test thoroughly**: Write tests as you go
4. **Optimize**: Add Numba JIT (Plan 2)
5. **Integrate**: Connect to API (Plan 4)
6. **Optional GPU**: Add CuPy acceleration (Plan 3)

---

## 📚 Resources

- **Numba**: https://numba.pydata.org/
- **CuPy**: https://docs.cupy.dev/
- **Chess Programming Wiki**: https://www.chessprogramming.org/
- **Reference**: python-chess library for correctness verification

---

## 🎨 Architecture Diagrams

Visual diagrams showing implementation flow and system architecture are available in the individual plan documents.

---

## ❓ Questions?

For detailed information on any specific plan, refer to the individual plan documents in `docs/plans/`.

For questions about the overall implementation strategy, see the roadmap in `00-implementation-roadmap.md`.

