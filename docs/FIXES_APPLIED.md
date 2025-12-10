# Fixes Applied - 2025-12-10

## Issue 1: Move Notation Bug ✅ FIXED

### Problem
Messages showed:
```
[6:01:07 PM] Move played: f6
```

Expected:
```
[6:01:07 PM] Move played: f7 → f6
```

### Root Cause
The code was using `res.move?.san` which returns Standard Algebraic Notation (e.g., "f6") instead of the from/to squares.

### Fix Applied
**File**: `frontend/src/ui/boardView.js` (lines 208-223)

**Before**:
```javascript
const moveStr = res.move?.san || `${fromSquare} → ${square}`;
eventBus.emit("status:info", `Move played: ${moveStr}`);
```

**After**:
```javascript
const moveFrom = res.move?.from || fromSquare;
const moveTo = res.move?.to || square;
eventBus.emit("status:info", `Move played: ${moveFrom} → ${moveTo}`);
```

### Testing
1. Start frontend: `cd frontend && npm run dev`
2. Make a move (e.g., e2 → e4)
3. Verify message shows: `Move played: e2 → e4` ✓

---

## Issue 2: GPU Not Detected (RTX 4070) ⚠️ REQUIRES ACTION

### Problem
Tests fail with:
```
RuntimeError: CuPy failed to load nvrtc64_112_0.dll
```

GPU detection shows:
```
Backend: CPU (NumPy + Numba)
GPU detected: False
```

### Root Cause
**Wrong CuPy version installed**:
- Installed: CuPy built for CUDA 11.2 (`nvrtc64_112_0.dll`)
- Required: CuPy built for CUDA 12.x (for RTX 4070)

### Fix Required

#### Step 1: Check CUDA Version
```powershell
nvidia-smi
```
Look for "CUDA Version" (should be 12.x for RTX 4070)

**Example output**:
```
CUDA Version: 12.3
```

#### Step 2: Uninstall ALL CuPy Packages
```powershell
pip uninstall cupy cupy-cuda11x cupy-cuda12x -y
```

**IMPORTANT**: You currently have the wrong `cupy` package installed. You need `cupy-cuda12x` specifically!

#### Step 3: Install Correct CuPy
```powershell
pip install cupy-cuda12x
```

**Note**: Install `cupy-cuda12x` (with `-cuda12x` suffix), NOT just `cupy`!

#### Step 4: Verify
```powershell
cd backend
python -c "from app.engine_core.backend import GPU, backend_info; print('GPU:', GPU); print(backend_info())"
```

**Expected output**:
```
Backend: GPU (CuPy) - NVIDIA GeForce RTX 4070
GPU: True
Backend: GPU (CuPy) - NVIDIA GeForce RTX 4070
```

#### Step 5: Run Tests
```powershell
python -m pytest app/engine_core/test_gpu.py -v
```

**Expected**: All 5 tests should pass! ✓

### Documentation
See `docs/GPU_SETUP_GUIDE.md` for detailed instructions.

---

## Issue 3: Pytest Warning ✅ FIXED

### Problem
```
PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
```

### Fix Applied
**File**: `backend/pytest.ini` (created)

Added configuration:
```ini
[pytest]
asyncio_default_fixture_loop_scope = function
```

### Testing
```powershell
python -m pytest app/engine_core/test_gpu.py -v
```

Warning should no longer appear ✓

---

## Summary

| Issue | Status | Action Required |
|-------|--------|-----------------|
| Move notation bug | ✅ FIXED | Test frontend |
| GPU not detected | ⚠️ REQUIRES ACTION | Install `cupy-cuda12x` |
| Pytest warning | ✅ FIXED | None |

---

## Next Steps

### 1. Fix GPU Detection
```powershell
pip uninstall cupy
pip install cupy-cuda12x
```

### 2. Verify GPU Works
```powershell
cd backend
python -c "from app.engine_core.backend import GPU, backend_info; print(backend_info())"
```

### 3. Run All Tests
```powershell
python -m pytest app/engine_core/test_gpu.py -v
```

### 4. Run Benchmarks (Optional)
```powershell
python -m app.engine_core.benchmark_gpu
```

This will show you the actual speedup on your RTX 4070! 🚀

### 5. Test Frontend
```powershell
cd frontend
npm run dev
```

Make some moves and verify the notation is correct.

---

## Files Modified

1. `frontend/src/ui/boardView.js` - Fixed move notation
2. `backend/pytest.ini` - Suppressed pytest warning
3. `docs/GPU_SETUP_GUIDE.md` - Created GPU setup guide
4. `docs/FIXES_APPLIED.md` - This file

---

## Expected Performance (After GPU Fix)

With your RTX 4070, you should see:

### Batch Size 100
- Evaluation: 10-30x speedup
- Attack Maps: 10-20x speedup
- Move Generation: 5-15x speedup

### Batch Size 1000
- Evaluation: 30-100x speedup
- Attack Maps: 20-50x speedup
- Move Generation: 10-30x speedup

The RTX 4070 is a powerful GPU - you should see excellent performance! 🎉

