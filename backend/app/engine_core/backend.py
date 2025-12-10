"""
backend.py — CPU/GPU backend abstraction.

Exposes:
    xp      → NumPy or CuPy
    GPU     → True/False
    Engine  → EngineCPU or EngineGPU class
"""

# ================================================================
# 1. Try GPU (CuPy)
# ================================================================

GPU = False
xp = None
Engine = None

try:
    import cupy as cp

    # Try allocating and performing a simple operation to confirm working GPU
    try:
        test_arr = cp.zeros((4,), dtype=cp.float32)
        test_arr = test_arr + 1  # This triggers compilation
        _ = test_arr.get()  # Transfer to CPU to verify full pipeline
        xp = cp
        GPU = True
    except Exception as e:
        # GPU detected but not fully functional (missing CUDA libs, etc.)
        # Fall back to CPU
        raise ImportError(f"GPU detected but not functional: {e}")

except Exception:
    pass

# ================================================================
# 2. Fall back to CPU
# ================================================================
if not GPU:
    import numpy as np
    xp = np
    GPU = False

# ================================================================
# 3. Load the appropriate engine implementation
# ================================================================
if GPU:
    from .engine_gpu import EngineGPU as Engine
else:
    from .engine_cpu import EngineCPU as Engine

# ================================================================
# 4. Developer-friendly printout
# ================================================================
def backend_info():
    if GPU:
        try:
            import cupy as cp
            dev = cp.cuda.runtime.getDevice()
            props = cp.cuda.runtime.getDeviceProperties(dev)
            name = props["name"].decode()
            return f"Backend: GPU (CuPy) - {name}"
        except Exception:
            return "Backend: GPU (CuPy) - Unknown GPU"
    else:
        return "Backend: CPU (NumPy + Numba)"

print(backend_info())
