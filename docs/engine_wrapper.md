# **Project BishopForge: Chess Engine Architecture (Short Overview)**

### **1. API Backend (FastAPI)**

FastAPI backend remains the “public interface.”
It exposes POST/GET endpoints for:

* position analysis
* move generation
* PGN handling
* SAN validation
* session management

These endpoints call a *thin wrapper* in `app/engine.py`.

---

# **2. Engine Wrapper (`app/engine.py`)**

This module defines **stable, backend-agnostic interfaces** for:

* single-position evaluation
* batched evaluation
* single-position move generation
* batched move generation
* batched attack maps

It always returns **NumPy arrays + Python primitives** so the API layer never sees GPU objects.

---

# **3. Accelerated Compute Core (`app/engine_core/`)**

This directory contains the **real chess compute engine**, fully isolated from FastAPI:

```
engine_core/
    backend.py
    engine_cpu.py
    engine_gpu.py
    engine_batch.py
    moves.py
```

### **Key responsibilities:**

### **A. Automatic CPU/GPU Detection (`backend.py`)**

* On import, attempts to load and initialize CuPy.
* If GPU is available → use **CuPy** backend.
* Else → fall back to **NumPy + Numba** backend.

It exports:

* `xp` → either `numpy` or `cupy`
* `GPU` → boolean
* `Engine` → CPU or GPU engine class

---

# **4. Dual Engine Implementations**

### **A. `engine_cpu.py`**

* Uses NumPy arrays and Numba-accelerated JIT kernels.
* Optimized for general CPU performance.
* Reliable everywhere, including Fly.io (GPU not available).

### **B. `engine_gpu.py`**

* Uses CuPy arrays on NVIDIA/AMD GPUs.
* Batched kernels allow parallel processing of hundreds of boards.
* Provides the same API as the CPU engine.

---

# **5. Batch Processing Layer (`engine_batch.py`)**

This module builds **batch-first** versions of all compute functions:

* `evaluate_batch`
* `compute_attack_maps_batch`
* `generate_moves_batch`

Boards are shaped `(N,64)` and operations return:

* attack maps `(N,64)`
* evaluation arrays `(N,)`
* move lists with a `board_idx` column

This design enables:

* GPU parallelization
* synchronous batch processing
* search frontier expansion
* ML-friendly pipelines

---

# **6. Move Representation (`moves.py`)**

Defines stable integer constants for move columns:

```
IDX, FROM, TO, PROMO, FLAGS
```

Used in both CPU and GPU pipelines.

---

# **7. Docker Deployment**

Your FastAPI backend is containerized normally:

* Python
* FastAPI
* Uvicorn
* NumPy, Numba
* (optionally) CuPy installed only when you want GPU support

### **Fly.io Deployment**

* Fly.io instances do **not** expose GPUs.
* Therefore the engine automatically runs in **CPU mode** using Numba.

### **Local / On-Prem / GPU Machines**

* CuPy is available → engine runs in **GPU mode**
* No code changes required

---

# **8. Key Strengths**

### **A. Fully Decoupled**

API code never touches GPU logic.
Chess logic never touches FastAPI.

### **B. Portable**

Runs on:

* Docker
* local desktops
* GPU-enabled servers
* Fly.io (CPU only)
* CI environments

### **C. Extensible**

You can replace internal kernels (attack maps, movegen, evaluation) without affecting:

* API routers
* tests
* Docker deployment
* frontend

### **D. Batch-First Architecture**

Everything uses the same `(N,64)` representation:

* drivable by GPU vectorization
* perfect for machine learning
* great for search with multi-node frontier expansion

---

If you want, I can now produce a **diagram (ASCII or image)** showing the architecture, or a **10-line “executive summary”** you can put at the top of the repo.
