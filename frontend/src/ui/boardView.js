import { fenToBoard, indexToSquare } from "../core/fenUtils.js";

let stylesInjected = false;

function ensureStyles() {
  if (stylesInjected) return;
  const style = document.createElement("style");
  style.textContent = `
    .bf-layout {
      display: flex;
      justify-content: center;
      align-items: flex-start;
      gap: 16px;
    }

    .bf-layout > div {
      display: flex;
      flex-direction: column;
      gap: 12px;
      width: 516px; /* Board width: 8*64px + 4px border */
    }

    .bf-board {
      display: grid;
      grid-template-columns: repeat(8, 64px);
      grid-template-rows: repeat(8, 64px);
      border: 2px solid #333;
      background: #333;
      width: fit-content;
      box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }

    .bf-square {
      width: 64px;
      height: 64px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 38px;
      cursor: pointer;
      user-select: none;
      transition: background 0.12s ease;
    }

    .bf-square.light {
      background: #f0d9b5;
    }

    .bf-square.dark {
      background: #b58863;
    }

    .bf-square.selected {
      outline: 3px solid #ffcc00;
      outline-offset: -3px;
    }

    .bf-square.highlight {
      box-shadow: inset 0 0 0 3px rgba(0, 255, 0, 0.7);
    }

    .bf-sidepanel {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .bf-card {
      background: #ffffff;
      border: 1px solid #ddd;
      border-radius: 4px;
      padding: 8px 10px;
      font-size: 14px;
      width: 100%;
      box-sizing: border-box;
    }

    .bf-card h3 {
      margin: 0 0 4px 0;
      font-size: 14px;
      font-weight: 600;
    }

    .bf-controls-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 8px;
    }

    .bf-controls-row button {
      padding: 4px 8px;
      border-radius: 4px;
      border: 1px solid #aaa;
      background: #f8f8f8;
      cursor: pointer;
      font-size: 13px;
    }

    .bf-controls-row button:hover {
      background: #eee;
    }

    .bf-checkbox-row {
      display: flex;
      flex-direction: column;
      gap: 2px;
      margin-bottom: 8px;
      font-size: 13px;
    }

    .bf-msg-info {
      color: #05668d;
    }

    .bf-msg-error {
      color: #b00020;
    }
  `;
  document.head.appendChild(style);
  stylesInjected = true;
}

function pieceToChar(piece) {
  const map = {
    p: "♟",
    r: "♜",
    n: "♞",
    b: "♝",
    q: "♛",
    k: "♚",
    P: "♙",
    R: "♖",
    N: "♘",
    B: "♗",
    Q: "♕",
    K: "♔",
  };
  return map[piece] || "";
}

export function createBoardView(rootEl, gameState, eventBus) {
  ensureStyles();

  let selectedSquare = null;
  let highlightedTargets = new Set();

  function clearSelection() {
    selectedSquare = null;
    highlightedTargets = new Set();
  }

  function needsPromotion(from, to) {
    const fen = gameState.getFen();
    const board = fenToBoard(fen);
    const fromRow = 7 - parseInt(from[1]) + 1;
    const fromCol = from.charCodeAt(0) - 97;
    const toRow = 7 - parseInt(to[1]) + 1;

    const piece = board[fromRow][fromCol];

    // Check if it's a pawn moving to the 8th rank (row 0) or 1st rank (row 7)
    if (piece === 'P' && toRow === 0) return true;
    if (piece === 'p' && toRow === 7) return true;

    return false;
  }

  function promptPromotion() {
    const piece = prompt("Promote to (q/r/b/n):", "q");
    if (!piece) return "q";
    const normalized = piece.toLowerCase();
    if (["q", "r", "b", "n"].includes(normalized)) {
      return normalized;
    }
    return "q";
  }

  function onSquareClick(square) {
    const config = gameState.getConfig();

    if (!selectedSquare) {
      const moves = gameState.getLegalMovesFrom(square);
      if (!moves || moves.length === 0) return;

      selectedSquare = square;
      if (config.highlight_valid_moves) {
        highlightedTargets = new Set(moves.map((m) => m.to));
      } else {
        highlightedTargets = new Set();
      }
      render();
      return;
    }

    if (square === selectedSquare) {
      clearSelection();
      render();
      return;
    }

    // Check if promotion is needed
    let promotion = undefined;
    if (needsPromotion(selectedSquare, square)) {
      promotion = promptPromotion();
    }

    const fromSquare = selectedSquare;
    const res = gameState.applyMove(fromSquare, square, promotion);
    if (!res.success) {
      eventBus.emit(
        "status:error",
        `Illegal move: ${fromSquare} → ${square}`
      );
    } else {
      // Use move.from and move.to from the chess.js move object
      const moveFrom = res.move?.from || fromSquare;
      const moveTo = res.move?.to || square;
      eventBus.emit(
        "status:info",
        `Move played: ${moveFrom} → ${moveTo}`
      );
    }

    clearSelection();
    render();
  }

  function render() {
    const fen = gameState.getFen();
    const board = fenToBoard(fen);

    rootEl.innerHTML = "";
    const boardEl = document.createElement("div");
    boardEl.className = "bf-board";

    for (let row = 0; row < 8; row++) {
      for (let col = 0; col < 8; col++) {
        const squareName = indexToSquare(row, col);
        const piece = board[row][col];

        const sqEl = document.createElement("div");
        const isLight = (row + col) % 2 === 0;
        sqEl.className =
          "bf-square " + (isLight ? "light" : "dark");

        if (selectedSquare === squareName) {
          sqEl.classList.add("selected");
        }
        if (highlightedTargets.has(squareName)) {
          sqEl.classList.add("highlight");
        }

        sqEl.dataset.square = squareName;
        sqEl.textContent = piece ? pieceToChar(piece) : "";

        sqEl.addEventListener("click", () => onSquareClick(squareName));

        boardEl.appendChild(sqEl);
      }
    }

    rootEl.appendChild(boardEl);
  }

  // Subscribe to game state changes to re-render and clear selection
  eventBus?.on("gameStateChanged", () => {
    clearSelection();
    render();
  });

  return { render };
}
