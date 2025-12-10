# Computer Opponent & GPU Toggle Implementation

## 🎯 Overview

This document describes the implementation of two major features:
1. **GPU Status Display & Toggle** - Shows GPU status and allows forcing CPU mode
2. **Computer Opponent System** - Play against AI with 5 different difficulty profiles

---

## ✅ Features Implemented

### 1. GPU Status & Toggle

**Backend API** (`backend/app/routers/opponent.py`):
- `GET /opponent/gpu-status` - Returns GPU availability and current backend info
- `POST /opponent/gpu-toggle?enable=true/false` - Toggle GPU usage

**Frontend** (`frontend/src/ui/controlsView.js`):
- GPU status checkbox (only visible when GPU is available)
- Shows backend info (e.g., "Use GPU (Backend: GPU (CuPy) - NVIDIA GeForce RTX 4070)")
- Checkbox toggles between GPU and CPU mode

### 2. Computer Opponent Profiles

**Five AI Profiles** (all use single-level evaluation):

| Profile | Strategy | Description |
|---------|----------|-------------|
| **Random** | Random move selection | Selects any legal move randomly |
| **High Aggressive** | Maximize offense | Increases own offense, decreases opponent offense |
| **High Defensive** | Maximize defense | Increases own defense, decreases opponent offense |
| **Moderate** | Balanced | Increases both own offense and defense |
| **Defensive Passive** | Passive defense | Increases own defense, decreases opponent defense |

**Backend API** (`backend/app/routers/opponent.py`):
- `POST /opponent/move` - Get opponent move for current position
  - Request: `{ "fen": "...", "profile": "aggressive" }`
  - Response: `{ "move_uci": "e2e4", "move_san": "e4", "evaluation": {...} }`

**Frontend** (`frontend/src/ui/controlsView.js`):
- Opponent dropdown selector at top of controls
- Options: "Human (No Computer)", "Random Mover", "High Aggressive", "High Defensive", "Moderate", "Defensive Passive"

**Auto-Play Logic** (`frontend/src/ui/boardView.js`):
- After human move, automatically requests opponent move
- 500ms delay for better UX
- Displays "Opponent is thinking..." message
- Shows opponent's move in status

---

## 📁 Files Modified

### Backend
- `backend/app/routers/opponent.py` - **NEW** - Opponent AI logic and GPU toggle
- `backend/app/main.py` - Added opponent router, fixed engine_manager import
- `backend/app/routers/analysis.py` - Fixed engine_manager import

### Frontend
- `frontend/src/api/backendClient.js` - Added `getGPUStatus()`, `toggleGPU()`, `getOpponentMove()`
- `frontend/src/core/gameState.js` - Added opponent state management
- `frontend/src/ui/controlsView.js` - Added GPU toggle and opponent selector
- `frontend/src/ui/boardView.js` - Added auto-play logic for opponent moves

### Tests
- `backend/test_opponent_direct.py` - **NEW** - Direct test of opponent AI logic

---

## 🧪 Testing

### Backend Tests

**Test Opponent AI Logic** (without server):
```powershell
cd backend
python test_opponent_direct.py
```

Expected output:
```
Testing Opponent AI Profiles
============================================================

AGGRESSIVE:
  Selected move: e3 (e2e3)
  Evaluation: {'score': 7, 'my_offense': 4053, ...}

DEFENSIVE:
  Selected move: Nh3 (g1h3)
  Evaluation: {'score': 0, 'my_offense': 4047, ...}

MODERATE:
  Selected move: Nf3 (g1f3)
  Evaluation: {'score': 5, 'my_offense': 4051, ...}

DEFENSIVE_PASSIVE:
  Selected move: Nh3 (g1h3)
  Evaluation: {'score': 0, 'my_offense': 4047, ...}

✅ All profiles tested successfully!
```

**Test API Endpoints** (requires running server):
```powershell
cd backend
python test_opponent_api.py
```

### Frontend Testing

1. **Start Backend**:
```powershell
cd backend
uvicorn app.main:app --reload
```

2. **Start Frontend**:
```powershell
cd frontend
npm run dev
```

3. **Test GPU Toggle**:
   - Look for GPU checkbox at top of controls
   - Should show "Use GPU (Backend: GPU (CuPy) - NVIDIA GeForce RTX 4070)" if GPU available
   - Toggle checkbox to switch between GPU and CPU

4. **Test Opponent AI**:
   - Select opponent from dropdown (e.g., "High Aggressive")
   - Make a move as white
   - Computer should automatically respond after 500ms
   - Try different opponent profiles to see different playing styles

---

## 🎮 How to Play Against Computer

1. Start both backend and frontend servers
2. Open browser to `http://localhost:5173`
3. Select opponent from dropdown at top of controls:
   - "Random Mover" - Good for testing
   - "High Aggressive" - Attacks aggressively
   - "High Defensive" - Plays defensively
   - "Moderate" - Balanced play
   - "Defensive Passive" - Very defensive
4. Make your move (you play white)
5. Computer will automatically respond (plays black)
6. Continue playing!

---

## 🔧 Technical Details

### Opponent AI Algorithm

Each profile evaluates all legal moves and selects the best one based on:

```python
# Get current position evaluation
current_eval = EngineCPU.evaluate(piece_arr, color_arr)
current_wo, current_wd, current_bo, current_bd = current_eval

# For each legal move:
#   1. Apply move
#   2. Evaluate new position
#   3. Calculate deltas
#   4. Score based on profile

# Aggressive: score = my_off_delta - opp_off_delta
# Defensive: score = my_def_delta - opp_off_delta
# Moderate: score = my_off_delta + my_def_delta
# Defensive Passive: score = my_def_delta - opp_def_delta
```

### GPU Toggle Implementation

- Global flag `_force_cpu_mode` in `opponent.py`
- When enabled, forces CPU evaluation even if GPU is available
- Frontend checkbox calls `/opponent/gpu-toggle` endpoint
- Status endpoint returns current GPU state

---

## ✅ Success Criteria

- [x] GPU status displayed in frontend
- [x] GPU toggle checkbox functional
- [x] Opponent dropdown with 5 profiles
- [x] Auto-play after human move
- [x] Different profiles select different moves
- [x] Smooth UX with "thinking" message
- [x] Backend API tested and working
- [x] Frontend integration complete

---

## 🚀 Next Steps (Optional)

1. Add difficulty levels (search depth)
2. Add opening book for better early game
3. Add endgame tablebase support
4. Add time controls
5. Add move history display
6. Add game save/load functionality


