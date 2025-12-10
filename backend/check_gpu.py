"""
GPU Diagnostic Script for BishopForge
Run this to check if your GPU is properly configured.
"""

import sys

print("="*70)
print("BishopForge GPU Diagnostic")
print("="*70)

# Step 1: Check if CuPy is installed
print("\n1. Checking CuPy installation...")
try:
    import cupy as cp
    print(f"   ✓ CuPy is installed (version {cp.__version__})")
except ImportError as e:
    print(f"   ✗ CuPy is NOT installed")
    print(f"   Error: {e}")
    print("\n   Solution: Install CuPy with:")
    print("   pip install cupy-cuda12x")
    sys.exit(1)

# Step 2: Check if GPU is detected
print("\n2. Checking GPU detection...")
try:
    dev = cp.cuda.runtime.getDevice()
    props = cp.cuda.runtime.getDeviceProperties(dev)
    gpu_name = props["name"].decode()
    print(f"   ✓ GPU detected: {gpu_name}")
except Exception as e:
    print(f"   ✗ GPU not detected")
    print(f"   Error: {e}")
    print("\n   Solution: Check if NVIDIA drivers are installed")
    sys.exit(1)

# Step 3: Check if CuPy can perform operations
print("\n3. Checking CuPy operations...")
try:
    test_arr = cp.zeros((4,), dtype=cp.float32)
    test_arr = test_arr + 1
    result = test_arr.get()
    print(f"   ✓ CuPy operations work (test result: {result})")
except Exception as e:
    print(f"   ✗ CuPy operations FAILED")
    print(f"   Error: {e}")
    print("\n   This usually means you have the wrong CuPy version!")
    print("\n   Solution:")
    print("   1. Check CUDA version: nvidia-smi")
    print("   2. Uninstall all CuPy: pip uninstall cupy cupy-cuda11x cupy-cuda12x -y")
    print("   3. Install correct version: pip install cupy-cuda12x")
    sys.exit(1)

# Step 4: Check if backend detects GPU
print("\n4. Checking BishopForge backend...")
try:
    from app.engine_core.backend import GPU, backend_info
    if GPU:
        print(f"   ✓ Backend detected GPU: {backend_info()}")
    else:
        print(f"   ✗ Backend is using CPU: {backend_info()}")
        print("\n   This means CuPy operations failed during initialization.")
        print("   Check the error above for details.")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ Backend import failed")
    print(f"   Error: {e}")
    sys.exit(1)

# Step 5: Check if GPU tests can run
print("\n5. Checking GPU test imports...")
try:
    from app.engine_core.test_gpu import test_gpu_single_evaluation
    print(f"   ✓ GPU tests can be imported")
except Exception as e:
    print(f"   ✗ GPU test import failed")
    print(f"   Error: {e}")
    sys.exit(1)

# All checks passed!
print("\n" + "="*70)
print("✅ ALL CHECKS PASSED!")
print("="*70)
print("\nYour GPU is properly configured for BishopForge!")
print("\nNext steps:")
print("  1. Run GPU tests: python -m pytest app/engine_core/test_gpu.py -v")
print("  2. Run GPU benchmarks: python -m app.engine_core.benchmark_gpu")
print("\nExpected performance on your RTX 4070:")
print("  - Batch 100: 10-30x speedup")
print("  - Batch 1000: 30-100x speedup")
print("\n" + "="*70)

