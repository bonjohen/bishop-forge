# GPU Setup Guide for BishopForge

## Issue: RTX 4070 Not Detected

Your RTX 4070 is installed correctly, but CuPy is looking for the wrong CUDA version.

### Problem
- **Installed**: CuPy 13.4.1 (built for CUDA 11.2)
- **Error**: `Could not find module 'nvrtc64_112_0.dll'`
- **Cause**: RTX 4070 requires CUDA 12.x, but you have CuPy built for CUDA 11.2

---

## Solution: Install Correct CuPy Version

### Step 1: Check Your CUDA Version

```powershell
nvidia-smi
```

Look for "CUDA Version" in the output (e.g., 12.3, 12.4, etc.)

**Example output**:
```
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 546.33                 Driver Version: 546.33         CUDA Version: 12.3     |
|-----------------------------------------------------------------------------------------+
```

### Step 2: Uninstall ALL CuPy Packages

```powershell
pip uninstall cupy cupy-cuda11x cupy-cuda12x -y
```

### Step 3: Install Correct CuPy Version

**For CUDA 12.x** (most likely for RTX 4070):
```powershell
pip install cupy-cuda12x
```

**For CUDA 11.x** (if nvidia-smi shows 11.x):
```powershell
pip install cupy-cuda11x
```

**IMPORTANT**: Make sure you install `cupy-cuda12x` (with the `-cuda12x` suffix), NOT just `cupy`!

### Step 4: Verify Installation

```powershell
python -c "import cupy as cp; print('CuPy version:', cp.__version__); dev = cp.cuda.runtime.getDevice(); props = cp.cuda.runtime.getDeviceProperties(dev); print('GPU:', props['name'].decode())"
```

**Expected output**:
```
CuPy version: 13.4.1
GPU: NVIDIA GeForce RTX 4070
```

### Step 5: Test GPU Backend

```powershell
cd backend
python -c "from app.engine_core.backend import GPU, backend_info; print('GPU detected:', GPU); print(backend_info())"
```

**Expected output**:
```
Backend: GPU (CuPy) - NVIDIA GeForce RTX 4070
GPU detected: True
Backend: GPU (CuPy) - NVIDIA GeForce RTX 4070
```

### Step 6: Run GPU Tests

```powershell
python -m pytest app/engine_core/test_gpu.py -v
```

**Expected**: All 5 tests should pass!

---

## Alternative: Install CUDA Toolkit

If you don't have CUDA installed at all:

1. Download CUDA Toolkit 12.x from: https://developer.nvidia.com/cuda-downloads
2. Install CUDA Toolkit
3. Install CuPy: `pip install cupy-cuda12x`

---

## Troubleshooting

### Issue: "CUDA driver version is insufficient"
- Update your NVIDIA drivers: https://www.nvidia.com/Download/index.aspx
- RTX 4070 requires driver version 525.60 or newer

### Issue: "No CUDA-capable device is detected"
- Check Device Manager → Display adapters
- Ensure RTX 4070 is enabled
- Restart computer

### Issue: Still getting DLL errors
- Ensure CUDA bin directory is in PATH:
  - `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.x\bin`
- Restart terminal after installing CUDA

---

## Performance Expectations

Once GPU is working, you should see:

### Batch Size 100
- Evaluation: 10-30x speedup
- Attack Maps: 10-20x speedup
- Move Generation: 5-15x speedup

### Batch Size 1000
- Evaluation: 30-100x speedup
- Attack Maps: 20-50x speedup
- Move Generation: 10-30x speedup

---

## Quick Reference

| CUDA Version | CuPy Package |
|--------------|--------------|
| 12.x | `pip install cupy-cuda12x` |
| 11.x | `pip install cupy-cuda11x` |
| No CUDA | Uses CPU (NumPy) automatically |

---

## Next Steps After GPU Setup

1. Run GPU tests: `pytest app/engine_core/test_gpu.py -v`
2. Run GPU benchmarks: `python -m app.engine_core.benchmark_gpu`
3. Enjoy 10-100x speedup! 🚀

