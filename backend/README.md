# BishopForge Backend API

FastAPI-based chess analysis and helper API for Project BishopForge.

## Features

- **Chess Analysis**: Get best move suggestions using Stockfish or lightweight Python evaluation
- **Move Generation**: List all legal moves for any position
- **Study Mode**: Validate SAN moves for training/study purposes
- **PGN Support**: Import and export games in PGN format
- **Session Management**: Maintain ephemeral game sessions with move history

## Quick Start

### Prerequisites

- Python 3.12+
- Stockfish binary for production-quality analysis

### Installation

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
# For development, the defaults work fine (uses lightweight Python mode)
```

### Running the Server

```bash
# Development server with auto-reload
uvicorn app.main:app --reload --port 8000

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_analysis.py

# Run with coverage
pytest --cov=app tests/
```

## Engine Modes

The backend supports three engine modes:

### 1. Python Mode (Default)
- **Use case**: Development, testing, lightweight deployments
- **Pros**: No external dependencies, fast startup
- **Cons**: Weak evaluation (material count only)
- **Config**: `BF_ENGINE_MODE=python`

### 2. SimpleEngine Mode (Recommended for Production)
- **Use case**: Production deployments requiring strong analysis
- **Pros**: Stockfish-powered, strong evaluation
- **Cons**: Requires Stockfish binary
- **Config**:
  ```
  BF_ENGINE_MODE=simpleengine
  BF_STOCKFISH_PATH=/usr/games/stockfish
  BF_ENGINE_POOL_SIZE=4
  ```

### 3. External Mode
- **Use case**: Delegate to remote engine service
- **Pros**: Offload computation, scalable
- **Cons**: Network latency, requires external service
- **Config**:
  ```
  BF_ENGINE_MODE=external
  BF_EXTERNAL_ENGINE_URL=https://your-engine-service.com/analyze
  ```

## API Endpoints

### Health Check
```
GET /health
```

### Analysis
```
POST /analysis/
Body: { "fen": "...", "max_depth": 12 }
Response: { "best_move": { "uci": "e2e4", "san": "e4", "score_cp": 23, "mate": null } }
```

### Legal Moves
```
POST /moves/
Body: { "fen": "...", "square": "e2" }  # square is optional
Response: { "moves_san": ["e4", "e3"], "moves_uci": ["e2e4", "e2e3"] }
```

### Study - Check Move
```
POST /study/check
Body: { "fen": "...", "san": "e4" }
Response: { "valid": true, "reason": null }
```

### PGN - Load
```
POST /pgn/load
Body: { "pgn": "1. e4 e5 2. Nf3..." }
Response: { "moves_san": ["e4", "e5", "Nf3"], "final_fen": "..." }
```

### PGN - Save
```
POST /pgn/save
Body: { "starting_fen": null, "moves_uci": ["e2e4", "e7e5"] }
Response: { "pgn": "1. e4 e5\n" }
```

### Sessions
```
POST /session/new
GET /session/{id}
POST /session/{id}/move
POST /session/{id}/undo
```

## Project Structure

```
backend/
├── app/
│   ├── main.py           # FastAPI app initialization
│   ├── config.py         # Configuration management
│   ├── models.py         # Pydantic models
│   ├── engine.py         # Chess engine abstraction
│   ├── cache.py          # In-memory caching
│   └── routers/
│       ├── analysis.py   # Analysis endpoint
│       ├── moves.py      # Move generation
│       ├── study.py      # SAN validation
│       ├── pgn.py        # PGN import/export
│       └── sessions.py   # Session management
├── tests/                # Test suite
├── requirements.txt      # Python dependencies
└── .env.example          # Environment configuration template
```

## Deployment

See `docs/backend_plan.md` for detailed deployment instructions for Fly.io or Railway.

## License

Part of Project BishopForge

