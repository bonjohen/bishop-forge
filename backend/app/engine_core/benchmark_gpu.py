"""
GPU Benchmark Suite - Measure GPU speedup vs CPU.
"""

import time
import numpy as np

# Try to import CuPy
try:
    import cupy as cp
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    print("CuPy not available, GPU benchmarks will be skipped")

from .engine_cpu import EngineCPU
from .fen_utils import fen_to_arrays, STARTING_FEN

if GPU_AVAILABLE:
    from .engine_gpu import EngineGPU


def benchmark_batch_evaluation(batch_sizes=[1, 10, 100, 1000]):
    """Benchmark batch evaluation on CPU vs GPU."""
    if not GPU_AVAILABLE:
        print("GPU not available, skipping GPU benchmarks")
        return
    
    print("\n" + "="*70)
    print("BENCHMARK: Batch Evaluation")
    print("="*70)
    print(f"{'Batch Size':<12} {'CPU Time':<15} {'GPU Time':<15} {'Speedup':<10}")
    print("-"*70)
    
    # Prepare test position
    piece_np, color_np, _ = fen_to_arrays(STARTING_FEN)
    
    for N in batch_sizes:
        # Create batch
        piece_batch_np = np.stack([piece_np] * N)
        color_batch_np = np.stack([color_np] * N)
        
        # CPU benchmark
        start = time.perf_counter()
        for i in range(N):
            EngineCPU.evaluate(piece_batch_np[i], color_batch_np[i])
        cpu_time = time.perf_counter() - start
        
        # GPU benchmark
        piece_batch_gpu = cp.asarray(piece_batch_np)
        color_batch_gpu = cp.asarray(color_batch_np)
        
        # Warmup
        EngineGPU.evaluate_batch(piece_batch_gpu, color_batch_gpu)
        cp.cuda.Stream.null.synchronize()
        
        # Timed run
        start = time.perf_counter()
        EngineGPU.evaluate_batch(piece_batch_gpu, color_batch_gpu)
        cp.cuda.Stream.null.synchronize()
        gpu_time = time.perf_counter() - start
        
        speedup = cpu_time / gpu_time if gpu_time > 0 else 0
        
        print(f"{N:<12} {cpu_time*1000:>12.2f} ms {gpu_time*1000:>12.2f} ms {speedup:>8.1f}x")


def benchmark_batch_attack_maps(batch_sizes=[1, 10, 100, 1000]):
    """Benchmark batch attack maps on CPU vs GPU."""
    if not GPU_AVAILABLE:
        print("GPU not available, skipping GPU benchmarks")
        return
    
    print("\n" + "="*70)
    print("BENCHMARK: Batch Attack Maps")
    print("="*70)
    print(f"{'Batch Size':<12} {'CPU Time':<15} {'GPU Time':<15} {'Speedup':<10}")
    print("-"*70)
    
    # Prepare test position
    piece_np, color_np, _ = fen_to_arrays(STARTING_FEN)
    
    for N in batch_sizes:
        # Create batch
        piece_batch_np = np.stack([piece_np] * N)
        color_batch_np = np.stack([color_np] * N)
        
        # CPU benchmark
        start = time.perf_counter()
        for i in range(N):
            EngineCPU.compute_attack_maps(piece_batch_np[i], color_batch_np[i])
        cpu_time = time.perf_counter() - start
        
        # GPU benchmark
        piece_batch_gpu = cp.asarray(piece_batch_np)
        color_batch_gpu = cp.asarray(color_batch_np)
        
        # Warmup
        EngineGPU.compute_attack_maps_batch(piece_batch_gpu, color_batch_gpu)
        cp.cuda.Stream.null.synchronize()
        
        # Timed run
        start = time.perf_counter()
        EngineGPU.compute_attack_maps_batch(piece_batch_gpu, color_batch_gpu)
        cp.cuda.Stream.null.synchronize()
        gpu_time = time.perf_counter() - start
        
        speedup = cpu_time / gpu_time if gpu_time > 0 else 0
        
        print(f"{N:<12} {cpu_time*1000:>12.2f} ms {gpu_time*1000:>12.2f} ms {speedup:>8.1f}x")


def benchmark_batch_move_generation(batch_sizes=[1, 10, 100]):
    """Benchmark batch move generation on CPU vs GPU."""
    if not GPU_AVAILABLE:
        print("GPU not available, skipping GPU benchmarks")
        return
    
    print("\n" + "="*70)
    print("BENCHMARK: Batch Move Generation")
    print("="*70)
    print(f"{'Batch Size':<12} {'CPU Time':<15} {'GPU Time':<15} {'Speedup':<10}")
    print("-"*70)
    
    # Prepare test position
    piece_np, color_np, stm = fen_to_arrays(STARTING_FEN)
    
    for N in batch_sizes:
        # Create batch
        piece_batch_np = np.stack([piece_np] * N)
        color_batch_np = np.stack([color_np] * N)
        stm_batch_np = np.array([stm] * N, dtype=np.int8)
        
        # CPU benchmark
        start = time.perf_counter()
        for i in range(N):
            EngineCPU.generate_pseudo_legal_moves(
                piece_batch_np[i], color_batch_np[i], stm_batch_np[i]
            )
        cpu_time = time.perf_counter() - start
        
        # GPU benchmark
        piece_batch_gpu = cp.asarray(piece_batch_np)
        color_batch_gpu = cp.asarray(color_batch_np)
        stm_batch_gpu = cp.asarray(stm_batch_np)
        
        # Warmup
        EngineGPU.generate_moves_batch(piece_batch_gpu, color_batch_gpu, stm_batch_gpu)
        cp.cuda.Stream.null.synchronize()
        
        # Timed run
        start = time.perf_counter()
        EngineGPU.generate_moves_batch(piece_batch_gpu, color_batch_gpu, stm_batch_gpu)
        cp.cuda.Stream.null.synchronize()
        gpu_time = time.perf_counter() - start
        
        speedup = cpu_time / gpu_time if gpu_time > 0 else 0
        
        print(f"{N:<12} {cpu_time*1000:>12.2f} ms {gpu_time*1000:>12.2f} ms {speedup:>8.1f}x")


if __name__ == "__main__":
    print("\n🚀 BishopForge GPU Benchmark Suite")
    print("="*70)
    
    if not GPU_AVAILABLE:
        print("\n❌ CuPy not available. Install with: pip install cupy-cuda12x")
        exit(1)
    
    # Run benchmarks
    benchmark_batch_evaluation()
    benchmark_batch_attack_maps()
    benchmark_batch_move_generation()
    
    print("\n" + "="*70)
    print("✅ Benchmarks complete!")
    print("="*70)

