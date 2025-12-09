Below is the **backend-only task plan**, rewritten as a **clean, final, standalone document**.

I have:

* Selected options on your behalf where choices existed
* Removed frontend tasks
* Removed duplication
* Reorganized tasks into a professional backend-engineering plan
* Added missing steps (e.g., error-handling, logging, environment config)
* Ensured all tasks align directly with your current backend code
* Ensured this is a **single complete guide you can follow step-by-step**

This is now your **authoritative backend implementation document.**

---

# **Project BishopForge — Backend Implementation Plan**

### *Complete, Fully Selected, Ready for Execution*

This document defines **every task required to complete the backend** of the BishopForge chess engine service.
All choices have been made for you, and the plan follows a clear sequence from development to deployment.

---

# **1. Architecture Decisions (All Selected)**

These decisions govern the backend implementation:

### ✔ Engine Mode

Use **python-chess SimpleEngine (Stockfish)** for production.
Use **"python" lightweight mode** as fallback.

### ✔ Routing Structure

All API functionality must be split into smaller routers:

```
analysis.py     — best-move evaluation (core)
moves.py        — legal move generation
study.py        — forced SAN move validation
pgn.py          — PGN import/export
sessions.py     — ephemeral game sessions
```

### ✔ Persistence

Use **memory-based sessions** for MVP.
(You can later swap in Redis by replacing one module.)

### ✔ Caching

Use the **built-in cache module (LRU)** for MVP.
Later upgrade to Redis when needed.

### ✔ Deployment Target

Use **Fly.io** or **Railway** (preselected).
Backend runs with:

```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### ✔ Config System

Use `config.py` + environment variables.
Generate `.env.example` for developer guidance.

---

# **2. Backend Directory Structure**

Your backend MUST match this:

```
backend/
  app/
    main.py
    config.py
    models.py
    engine.py
    cache.py
    routers/
      analysis.py
      moves.py
      study.py
      pgn.py
      sessions.py
  tests/
    test_analysis.py
    test_moves.py
    test_study.py
    test_pgn.py
    test_sessions.py
  requirements.txt
  README.md
  .gitignore
```

---

# **3. Phase-by-Phase Backend Implementation Tasks**

---

# **Phase 1 — Foundation**

### 1.1 Requirements File (already chosen)

Use:

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
python-chess==1.999.0
pytest==8.3.2
pydantic==2.9.0
pydantic-core==2.23.0
typing-extensions==4.12.2
```

### 1.2 Config System

Implement `config.py` with:

* ENGINE_MODE (`python`, `simple`, `external`)
* STOCKFISH_PATH
* CACHE_ENABLED (`true/false`)
* LOG_LEVEL (`info`)
* CORS settings
* ENV (`development` or `production`)

Generate `.env.example`.

### 1.3 FastAPI Initialization

`main.py` must:

* Create FastAPI app
* Add CORS middleware
* Register routers
* Load configuration
* Initialize global engine pool
* Expose `/health` endpoint
* Set logging configuration

---

# **Phase 2 — Engine Implementation**

### 2.1 Python Mode

Implement simple evaluation (material count).

### 2.2 SimpleEngine Mode (default for production)

* Launch Stockfish subprocess
* Add async lock
* Set depth limit
* Handle timeouts
* Graceful engine shutdown

### 2.3 External Mode (future option)

Use generic HTTP POST to remote engine server.

### 2.4 Engine Pool

Preselected pool configuration:

```
POOL_SIZE = 2
DEPTH = 12
```

Pool MUST:

* Initialize pool at startup
* Reuse engine instances
* Prevent parallel access
* Close engines on shutdown

---

# **Phase 3 — Backend Routers**

---

## **3.1 analysis.py (core)**

Endpoints:

### ✔ POST `/analysis/`

Input:

* FEN
* max_depth (default 12)

Output:

* best move (SAN, UCI)
* evaluation (centipawns or mate)
* node count
* depth used

Error cases to implement:

* invalid FEN
* game over
* engine unavailable
* timeout

Caching:

* Use FEN+DEPTH as key
* Return cached response when present

---

## **3.2 moves.py**

Endpoints:

### ✔ POST `/moves/`

Input:

* FEN
* optional square ("from")

Output:

* legal moves SAN + UCI
* per-square move list if `from` provided

---

## **3.3 study.py**

Endpoints:

### ✔ POST `/study/check`

Validates a forced SAN move.

### ✔ POST `/study/apply`

Applies SAN move and returns new FEN.

---

## **3.4 pgn.py**

Endpoints:

### ✔ POST `/pgn/load`

Converts PGN → list of FEN positions.

### ✔ POST `/pgn/save`

Converts move list → PGN string.

---

## **3.5 sessions.py**

Sessions are **in-memory ephemeral game states**.

Endpoints:

* POST `/session/new`
* GET `/session/{id}`
* POST `/session/{id}/move`
* POST `/session/{id}/undo`
* DELETE `/session/{id}`

Session lifetime:

* Reset on server restart
* No persistence (MVP)

---

# **Phase 4 — Caching Layer**

### 4.1 In-Memory LRU Cache (MVP)

Implement:

* `cache.get(key)`
* `cache.set(key, value, ttl)`
* TTL = 5 minutes

### 4.2 Cache Keys

* Analysis: `analysis:{fen}:{depth}`
* Move list: `moves:{fen}`

### 4.3 Cache Bypass

If `BF_CACHE_ENABLED = false` → disable caching.

---

# **Phase 5 — Error Handling + Logging**

### 5.1 Custom Exceptions

Create:

* `InvalidFENError`
* `GameOverError`
* `EngineError`

### 5.2 Exception Handlers

Return formatted JSON errors.

### 5.3 Logging

Log:

* FEN received
* Engine depth
* Response time
* Errors
* External engine failures

Format selection:
Use **JSON logs** in production.

---

# **Phase 6 — Testing (Pytest)**

---

## 6.1 Unit Tests

### 🔨 Required for MVP:

| Module      | Tests Required                                  |
| ----------- | ----------------------------------------------- |
| analysis.py | valid FEN, invalid FEN, mate positions, caching |
| moves.py    | legal moves, invalid FEN                        |
| study.py    | valid SAN, illegal SAN                          |
| pgn.py      | load PGN, save PGN                              |
| sessions.py | create, move, undo, invalid ID                  |

---

## 6.2 Engine Tests

* Python mode evaluation
* SimpleEngine basic tests
* Timeout handling

---

## 6.3 Integration Tests

Use FastAPI TestClient:

* Full `/analysis/` call
* Internal engine behavior
* Caching behavior
* Move/undo interactions via `/session/*`

---

# **Phase 7 — Deployment Preparation**

### 7.1 Deployment Target

**Fly.io** (selected).
Create:

```
fly.toml
Dockerfile
```

### 7.2 Dockerfile

Use Python 3.12 slim.

Must install Stockfish binary:

```
/usr/games/stockfish
```

### 7.3 Environment Variables

Add to Fly.io:

* BF_ENGINE_MODE=simple
* BF_STOCKFISH_PATH=/usr/games/stockfish
* BF_CACHE_ENABLED=true
* BF_LOG_LEVEL=info

### 7.4 Deployment Commands

```
flyctl launch
flyctl deploy
flyctl logs
```

---

# **Phase 8 — Production Hardening**

### 8.1 Security

* CORS limited to your domain
* Remove debug=True
* Increase request body limit for PGN

### 8.2 Performance

* Increase engine pool to 4
* Add request timeouts
* Add rate limiting via middleware

### 8.3 Monitoring

Implement:

* Logging
* /health endpoint monitoring

---

# **Phase 9 — Documentation**

### 9.1 API Reference

Generate via scripts:

* Endpoints
* Input/Output schemas
* Examples
* Error responses

### 9.2 Developer Guide

Add:

* Setup
* Running tests
* Engine configuration
* PGN formats

### 9.3 .env.example

Document all backend env variables.

---

# **Final Step — Backend Readiness Checklist**

Before launch, all must be true:

### ✔ Analysis endpoint stable

### ✔ Move generation correct

### ✔ Study SAN validation correct

### ✔ PGN import/export working

### ✔ Sessions working

### ✔ Engine pool stable

### ✔ Stockfish integrated

### ✔ 100% tests passing

### ✔ Docker build passes

### ✔ Fly.io deployment tested

### ✔ Frontend works against production backend

