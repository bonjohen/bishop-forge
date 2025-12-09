````markdown
# Project BishopForge – Technical Design

Chess web application hosted under **chess.johnboen.com**, with an optional analysis API under **api-chess.johnboen.com**.

Audience: software developers who will implement, extend, and test the system.

---

## 1. Goals and Scope

### 1.1 Primary Goals

- Provide a **minimal chess-playing web UI**:
  - Users can play a full legal game of chess in the browser.
  - Board renders from FEN.
  - Click-to-select, click-to-move interaction.
  - Highlight valid moves (optional).
  - Take back moves (optional).
  - Apply “forced” SAN moves for study (optional).

- Keep **cost low**:
  - Frontend: static hosting (GitHub Pages for `chess.johnboen.com`).
  - Backend: optional FastAPI microservice which can be deployed separately.

- Provide a **clean architecture**:
  - Rules and game state encapsulated in testable core modules.
  - UI modules are “dumb” views that subscribe to events and call core APIs.
  - Backend is optional and can be added without changing the core gameplay.

### 1.2 Non-Goals (MVP)

- No user accounts or authentication.
- No persistent game storage (database).
- No full-strength chess engine integration (initially).
- No real-time multiplayer.
- No sophisticated UX (animations, drag-and-drop, etc.) beyond what’s needed for MVP.

---

## 2. System Context

### 2.1 High-Level Components

- **Web Browser**
  - Renders HTML/CSS/JS.
  - Executes the Vite-bundled frontend.
  - Handles all core game logic via `chess.js`.

- **Static Hosting (GitHub Pages)**
  - Serves `index.html`, JS bundles, and static assets.
  - Domain: `chess.johnboen.com`.

- **Optional Backend (FastAPI)**
  - HTTP JSON API.
  - Provides:
    - `GET /health` – health check.
    - `POST /analysis/` – given FEN, returns a suggested move.
  - Domain: `api-chess.johnboen.com`.

### 2.2 Data Flow (High-Level)

- User interacts with chessboard in the browser.
- UI calls **core game state** module.
- Core game state delegates to **engine client** (wrapper around `chess.js`).
- Engine client validates/executes moves and returns status.
- Game state updates and emits events via **event bus**.
- UI subscribes to events and re-renders.

Optional backend flow:

- Frontend captures current FEN.
- Sends FEN to `POST /analysis/`.
- Backend validates FEN, computes or selects a move.
- Returns JSON with `best_move` info.
- Frontend displays result as additional hint (does not override game state automatically in MVP).

---

## 3. Technology Choices

### 3.1 Frontend

- **Build tool**: Vite
- **Language**: Vanilla JavaScript (ES modules)
- **Rules engine**: `chess.js`
- **Testing**: Vitest

Rationale:

- Vite is fast and simple for small apps.
- Vanilla JS keeps dependencies light; no framework required for this scale.
- `chess.js` is a well-known chess rules engine.
- Vitest integrates cleanly with Vite and supports ES modules.

### 3.2 Backend (Optional)

- **Framework**: FastAPI
- **Language**: Python 3.x
- **Models**: Pydantic
- **Chess library**: `python-chess`
- **Testing**: Pytest + FastAPI TestClient

Rationale:

- FastAPI provides quick, type-annotated, well-documented endpoints.
- `python-chess` can validate FEN and generate moves reliably.
- Easy to later integrate a real chess engine (e.g., Stockfish).

---

## 4. Directory Structure

```text
project-bishopforge/
  README.md

  docs/
    architecture.md             # System-level overview (this doc’s contents distilled)
    design_core_functions.md    # API-level function contracts
    test_plan.md                # What to test and how
    project_plan.md             # Phased implementation roadmap
    project_structure.md        # Directory layout and rationale
    steps_for_john.md           # DNS, GitHub, and deployment steps

  frontend/
    package.json
    vite.config.js
    index.html
    README.md
    src/
      main.js
      ui/
        boardView.js
        controlsView.js
        statusView.js
      core/
        engineClient.js
        gameState.js
        rulesConfig.js
        fenUtils.js
      utils/
        eventBus.js
      api/
        backendClient.js
    tests/
      engineClient.test.js
      gameState.test.js

  backend/
    requirements.txt
    app/
      __init__.py
      main.py
      models.py
      routers/
        __init__.py
        analysis.py
    tests/
      test_analysis.py
````

---

## 5. Frontend Design

### 5.1 Core Concepts

* **Engine Client (`engineClient`)**: Encapsulates `chess.js`.

* **Game State (`gameState`)**: App-level logic that:

  * Applies config rules (e.g., allow/deny takeback).
  * Delegates to engine client.
  * Emits events on state change.

* **Rules Config (`rulesConfig`)**:

  * Default config.
  * Simple merging.

* **UI Views**:

  * `boardView`: board rendering + move interaction.
  * `statusView`: game status & move list.
  * `controlsView`: toggles, new game, undo, forced SAN.

* **Event Bus (`eventBus`)**: Local pub/sub for frontend modules.

### 5.2 Core Types (informal)

```ts
type Color = 'w' | 'b';

type Status = {
  isCheck: boolean;
  isCheckmate: boolean;
  isStalemate: boolean;
  isDraw: boolean;
  turn: Color;
};

type VerboseMove = {
  color: Color;
  from: string; // 'e2'
  to: string;   // 'e4'
  san: string;  // 'e4', 'Nf3', etc.
  lan: string;  // long algebraic notation
  flags: string;
  piece: string;
  captured?: string;
  promotion?: string;
};

type RulesConfig = {
  highlight_valid_moves: boolean;
  allow_takeback: boolean;
};
```

---

### 5.3 `engineClient.js`

**Responsibility**: Provide a stable API over `chess.js`.

**Main methods**:

```ts
initGame(initialFen?: string): void
getFen(): string
getLegalMoves(fromSquare?: string): VerboseMove[]
makeMove(from: string, to: string, promotion?: string): MoveResult
undoMove(): UndoResult
forceMove(san: string): MoveResult
getStatus(): Status
getHistory(): VerboseMove[]
```

**Result types:**

```ts
type MoveResult = {
  success: boolean;
  reason?: 'illegal' | 'game_over';
  move?: VerboseMove;
  status?: Status;
};

type UndoResult = {
  success: boolean;
  reason?: 'no_move';
  previousFen?: string;
  move?: VerboseMove;
  status?: Status;
};
```

**Key behaviors**:

* `initGame(initialFen?)`

  * Create new `Chess` instance.
  * If `initialFen` provided:

    * Try to `load()` it.
    * If invalid: throw `Error('Invalid FEN for initGame')`.

* `getLegalMoves(fromSquare?)`

  * If `fromSquare` omitted:

    * Return `chess.moves({ verbose: true })`.
  * Else:

    * Filter list by `m.from === fromSquare`.

* `makeMove(from, to, promotion?)`

  * Attempts `chess.move({ from, to, promotion })`.
  * If `null`:

    * `success = false`, `reason = 'illegal'`.
  * On success:

    * Returns `move` (verbose), `status = getStatus()`.

* `undoMove()`

  * Calls `chess.undo()`.
  * If `null`:

    * `success = false`, `reason = 'no_move'`.
  * Else:

    * `success = true`, `previousFen = chess.fen()`, `move`, `status`.

* `forceMove(san)`

  * Uses `chess.move(san)`.
  * If `null`:

    * `success = false`, `reason = 'illegal'`.
  * Else:

    * `success = true`, `move`, `status`.

* `getStatus()`

  * Uses `inCheck`, `inCheckmate`, `inStalemate`, `inDraw`, `turn`.
  * Abstracts over potential API naming differences between versions.

**Usage Example:**

```js
import { createEngineClient } from './engineClient.js';

const engine = createEngineClient();
engine.initGame(); // starting position

const movesFromE2 = engine.getLegalMoves('e2');  // e3, e4
const result = engine.makeMove('e2', 'e4');
if (result.success) {
  console.log(result.status);
}
```

---

### 5.4 `rulesConfig.js`

**Responsibility**: Provide default rules and a pure merge helper.

```js
export function getDefaultConfig() {
  return {
    highlight_valid_moves: true,
    allow_takeback: true,
  };
}

export function mergeConfig(base, patch) {
  return { ...base, ...patch };
}
```

Usage:

```js
import { getDefaultConfig, mergeConfig } from './rulesConfig.js';

let config = getDefaultConfig();
config = mergeConfig(config, { highlight_valid_moves: false });
```

---

### 5.5 `gameState.js`

**Responsibility**: Encapsulate:

* Current FEN.
* Current status.
* Rules config.
* Higher-level operations for gameplay, respecting config.
* Emitting events on changes.

**Public API:**

```ts
newGame(): void
getFen(): string
getStatus(): Status
getMoveHistory(): VerboseMove[]
getConfig(): RulesConfig
updateConfig(patch: Partial<RulesConfig>): void
getLegalMovesFrom(square: string): VerboseMove[]
applyMove(from: string, to: string, promotion?: string): MoveResult
requestUndo(): UndoResult & { reason?: 'not_allowed' }
```

**Events**:

* `gameStateChanged` – emitted whenever the board position changes.
* `configChanged` – emitted whenever config is updated.

**Key logic**:

* `newGame()`

  * Calls `engine.initGame()`.
  * Refreshes status from `engine.getStatus()`.
  * Emits `gameStateChanged`.

* `updateConfig(patch)`

  * Uses `mergeConfig`.
  * Emits `configChanged`.

* `applyMove(from, to, promotion?)`

  * Calls `engine.makeMove(...)`.
  * If `success`:

    * Updates cached status.
    * Emits `gameStateChanged`.

* `requestUndo()`

  * If `config.allow_takeback === false`:

    * Return `{ success: false, reason: 'not_allowed' }`.
  * Else:

    * Delegates to `engine.undoMove()`, updates status, emits on success.

**Usage Example:**

```js
import { createGameState } from './core/gameState.js';
import { getDefaultConfig } from './core/rulesConfig.js';
import { createEventBus } from './utils/eventBus.js';

const eventBus = createEventBus();
const gameState = createGameState(eventBus, getDefaultConfig());

gameState.newGame();

eventBus.on('gameStateChanged', () => {
  console.log('FEN changed to', gameState.getFen());
});

gameState.applyMove('e2', 'e4');
```

---

### 5.6 `eventBus.js`

A minimal pub/sub mechanism:

```ts
on(event: string, handler: (payload: any) => void): void
off(event: string, handler: (payload: any) => void): void
emit(event: string, payload?: any): void
```

Implementation sketch:

```js
export function createEventBus() {
  const handlers = new Map();

  function on(event, handler) {
    if (!handlers.has(event)) handlers.set(event, new Set());
    handlers.get(event).add(handler);
  }

  function off(event, handler) {
    if (handlers.has(event)) handlers.get(event).delete(handler);
  }

  function emit(event, payload) {
    if (!handlers.has(event)) return;
    for (const fn of handlers.get(event)) {
      try { fn(payload); }
      catch (err) { console.error('Event handler error', event, err); }
    }
  }

  return { on, off, emit };
}
```

---

### 5.7 `fenUtils.js`

**Responsibility**: Convert FEN into a 2D array for board rendering.

```js
export function fenToBoard(fen) {
  const [position] = fen.split(' ');
  const rows = position.split('/');
  const board = [];

  for (let r = 0; r < 8; r++) {
    const row = rows[r];
    const outRow = [];
    for (const ch of row) {
      if (/[1-8]/.test(ch)) {
        const empty = parseInt(ch, 10);
        for (let i = 0; i < empty; i++) outRow.push(null);
      } else {
        outRow.push(ch); // FEN piece char
      }
    }
    board.push(outRow);
  }

  return board;
}
```

---

### 5.8 `boardView.js`

**Responsibility**: Render the board, handle selection, highlight, and move application.

Key behaviors:

* Layout:

  * 8×8 CSS grid (fixed 60px square size for MVP).
* Renders pieces using Unicode (e.g., `♙`, `♟`).
* Click behavior:

  1. First click:

     * Mark square as `selected`.
     * If `highlight_valid_moves`:

       * Call `gameState.getLegalMovesFrom(square)`.
       * Add `.highlight` class to all destinations.
  2. Second click:

     * Attempt `gameState.applyMove(from, to)`.
     * Clear selection and highlights.
     * If move fails: silent for now (future TODO: error UI).

**Coordinate mapping**:

* Files: `['a','b','c','d','e','f','g','h']`
* Ranks: `['8','7','6','5','4','3','2','1']`
* Each `board[r][f]` maps to square `files[f] + ranks[r]`.

**CSS hooks**:

* `.highlight` – for legal destination squares.
* `.selected` – for currently selected square.

---

### 5.9 `statusView.js`

**Responsibility**: Display:

* Current turn (White/Black).
* Check / Checkmate / Stalemate / Draw flags.
* Move history (SAN).

Behavior:

* Subscribes to `gameStateChanged`.
* On event:

  * Calls `gameState.getStatus()` and `gameState.getMoveHistory()`.
  * Builds display string:

    * `Turn: White` or `Turn: Black`.
    * Adds suffix:

      * `– Checkmate`
      * `– Stalemate`
      * `– Draw`
      * `– Check`
  * Renders ordered list of moves (using `move.san` where possible).

---

### 5.10 `controlsView.js`

**Responsibility**:

* Provide top-level controls:

  * `New Game` button.
  * Checkboxes for:

    * Highlight valid moves.
    * Allow take-backs.
  * `Undo move` button.

Behavior:

* On “New Game”:

  * Calls `gameState.newGame()`.

* On config toggles:

  * Calls `gameState.updateConfig(...)`.
  * `gameState` emits `configChanged`, which the view listens to keep checkboxes in sync if config changes programmatically.

* On “Undo Move”:

  * Calls `gameState.requestUndo()`.
  * If result `success === false`:

    * For now: ignore or log (future: show error message).

* On “Apply Forced Move”:

  * Reads SAN from input.
  * Calls `gameState.applyForcedMove(san)`.
  * If success: clears the input.
  * If failure: no UI change (future: display error).

---

### 5.11 `backendClient.js`

**Responsibility**: Thin wrapper around `fetch` to call the optional backend.

Contract:

```ts
async function analyzePosition(fen: string, maxDepth?: number): Promise<AnalyzeResponse>
```

`AnalyzeResponse` shape:

```ts
type MoveSuggestion = { san: string; uci: string; score_cp: number };
type AnalyzeResponse = { best_move: MoveSuggestion };
```

Implementation outline:

```js
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function analyzePosition(fen, maxDepth = 8) {
  const res = await fetch(`${API_BASE}/analysis/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ fen, max_depth: maxDepth })
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Analysis API error: ${res.status} ${text}`);
  }

  return res.json();
}
```

---

## 6. Backend Design (Optional)

### 6.1 Endpoints

* `GET /health`

  * Returns `{"status": "ok"}`.
  * Used for health checks and monitoring.

* `POST /analysis/`

  * Input: FEN + `max_depth` (currently unused).
  * Output: JSON with `best_move`.

### 6.2 Models

```python
from pydantic import BaseModel

class AnalyzeRequest(BaseModel):
    fen: str
    max_depth: int = 8

class MoveSuggestion(BaseModel):
    san: str
    uci: str
    score_cp: int

class AnalyzeResponse(BaseModel):
    best_move: MoveSuggestion
```

### 6.3 Implementation Outline

```python
# app/routers/analysis.py
from fastapi import APIRouter, HTTPException
import chess
from ..models import AnalyzeRequest, AnalyzeResponse, MoveSuggestion

router = APIRouter()

@router.post("/", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    board = chess.Board()
    try:
        board.set_fen(req.fen)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    legal_moves = list(board.legal_moves)
    if not legal_moves:
        raise HTTPException(status_code=400, detail="No legal moves in this position")

    # MVP: first legal move
    move = legal_moves[0]
    san = board.san(move)
    uci = move.uci()

    best = MoveSuggestion(san=san, uci=uci, score_cp=0)
    return AnalyzeResponse(best_move=best)
```

Main application:

```python
# app/main.py
from fastapi import FastAPI
from .routers import analysis

app = FastAPI(title="Project BishopForge API")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
```

---

## 7. Testing Strategy

### 7.1 Frontend (Vitest)

**engineClient tests**:

* Initial FEN after `initGame()` includes expected structure.
* Legal move `e2 -> e4`:

  * `success === true`
  * Turn flips to black.
* Illegal move (e.g., `e2 -> e5`):

  * `success === false`, `reason === 'illegal'`.
* Undo with no history:

  * `success === false`, `reason === 'no_move'`.
* Undo after one move:

  * FEN returns to initial.
* `forceMove('e4')` is accepted from start.
* `forceMove('Qh9')` is rejected (`reason === 'illegal'`).

**gameState tests** (with fake event bus):

* `newGame()` sets starting position and white to move.
* `applyMove('e2','e4')`:

  * `success === true`
  * Status.turn is `'b'`
  * Emits `gameStateChanged`.
* `requestUndo()` when `allow_takeback = false`:

  * `success === false`, `reason === 'not_allowed'`.
* `requestUndo()` when allowed and at least one move:

  * Undo works and FEN returns to initial.
* `applyForcedMove()` when `allow_forced_moves = false`:

  * `success === false`, `reason === 'not_allowed'`.
* `applyForcedMove()` when `allow_forced_moves = true` and SAN valid:

  * `success === true`, status updates.

### 7.2 Backend (Pytest)

Using `TestClient(app)`:

* `GET /health`:

  * `status_code == 200`, body `{"status": "ok"}`.

* Valid FEN to `/analysis/`:

  * `status_code == 200`.
  * JSON includes `best_move.san` and `best_move.uci`.

* Invalid FEN:

  * `status_code == 400`.

* FEN with no legal moves:

  * `status_code == 400`, `detail` indicates no legal moves.

---

## 8. Deployment Considerations

### 8.1 Frontend (GitHub Pages)

* Build: `npm run build` → `dist/`.
* Deploy `dist/` to `gh-pages` branch.
* DNS:

  * `chess.johnboen.com CNAME bonjohen.github.io`.
* GitHub Pages settings:

  * Source: `gh-pages` branch.
  * Custom domain: `chess.johnboen.com`.
  * Enforce HTTPS.

### 8.2 Backend

* Run `uvicorn app.main:app` behind:

  * Reverse proxy (nginx) or
  * Platform provider (Render, Fly.io, etc.).
* DNS:

  * `api-chess.johnboen.com` → backend host.
* TLS:

  * Let’s Encrypt or provider’s certificate.

---

## 9. Future Extensions

* Replace dummy analysis with real engine (Stockfish) and expose:

  * Score in centipawns.
  * Depth, PV line.
* Add puzzle mode:

  * Preloaded FENs + solution sequences.
* Add simple persistence:

  * Store game snapshots or PGNs per browser (localStorage) or per user (backend).
* Add multi-board or training features:

  * Force opponent moves.
  * Annotated study mode with variations.

---

This design document consolidates the architecture, contracts, and behaviors needed for a developer to implement, test, and extend **Project BishopForge** with minimal ambiguity.

```
```
