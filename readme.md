```markdown
# Project BishopForge  
A minimal, testable chess web application with optional FastAPI analysis backend.

**Live target (planned):**  
- Frontend: `https://chess.johnboen.com`  
- Backend (optional): `https://api-chess.johnboen.com`

This project provides a clean, modular chess client built entirely from first principles using **vanilla JavaScript**, **chess.js**, and an optional **Python FastAPI backend** for position analysis.  
All game logic runs client-side for speed, simplicity, and zero hosting cost.

---

## 🚀 Features

### ✔ Complete In-Browser Chess Logic  
- Powered by **chess.js** wrapped in a clean `engineClient` interface  
- Valid move generation  
- SAN history  
- Legal/illegal move validation  

### ✔ UI That Mirrors Real Chess Tools  
- Click-to-select, click-to-move  
- Optional highlighting of legal moves  
- Optional undo/takeback  
- Optional “forced SAN move” mode (study mode / puzzle exploration)  
- Status panel with:
  - Turn indicator  
  - Check / Checkmate / Stalemate / Draw  
  - Full move list  

### ✔ Optional Backend (FastAPI)  
Provides one endpoint:

```

POST /analysis/
{
"fen": "<current position>",
"max_depth": 8
}

```

MVP backend returns the **first legal move** for validation/testing.  
It can be extended to call Stockfish or another engine.

---

# 📁 Project Structure

```

project-bishopforge/
README.md
docs/...
frontend/
package.json
vite.config.js
index.html
src/
main.js
ui/
core/
utils/
api/
tests/
backend/
requirements.txt
app/
main.py
models.py
routers/
tests/

````

---

# 🖥 Frontend Setup (Vite + JS)

## 1. Install dependencies

```bash
cd frontend
npm install
````

## 2. Run development server

```bash
npm run dev
```

Vite will print a localhost URL such as:

```
http://localhost:5173
```

Open it in your browser.

## 3. Build for production

```bash
npm run build
```

Output appears in:

```
frontend/dist/
```

You will push this folder to the **gh-pages** branch for deployment at `chess.johnboen.com`.

---

# 🌐 Deploying to GitHub Pages

1. Enable GitHub Pages

   * Repository → Settings → Pages
   * Select `gh-pages` branch as the publishing source

2. Add CNAME:

   * `chess.johnboen.com → bonjohen.github.io`

3. Push build:

```bash
npm run build
git subtree push --prefix frontend/dist origin gh-pages
```

or automate later with GitHub Actions.

---

# 🐍 Backend Setup (FastAPI)

Backend is optional for MVP.

## 1. Create virtual environment

```bash
cd backend
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Run server locally

```bash
uvicorn app.main:app --reload --port 8000
```

You can now test:

```
GET  http://localhost:8000/health
POST http://localhost:8000/analysis/
```

---

# 🧪 Testing

## Frontend (Vitest)

```bash
cd frontend
npm run test
```

Covers:

* engineClient
* gameState

## Backend (pytest)

```bash
cd backend
pytest
```

Covers:

* `/health`
* `/analysis/` validation logic

---

# 🔧 Development Philosophy

* **Pure modular design**
  Core logic is independent of UI.

* **Event-driven architecture**
  Views subscribe to `gameStateChanged` and `configChanged`.
  No tight coupling.

* **Testable from top to bottom**
  All logic is in plain ES modules or Python modules with complete unit test capabilities.

* **Zero-cost hosting**
  Frontend runs on GitHub Pages.
  Backend is optional and deployable to any cheap host.

---

# 🧭 Roadmap

* Integrate real engine (Stockfish or API)
* Add puzzles + study mode improvements
* Add theme customization
* Add drag-and-drop piece movement
* Add engine evaluation overlay
