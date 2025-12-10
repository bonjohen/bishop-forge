import { analyzePosition } from "../api/backendClient.js";

export function createControlsView(rootEl, gameState, eventBus) {
  function render() {
    const config = gameState.getConfig();

    rootEl.innerHTML = "";
    const card = document.createElement("div");
    card.className = "bf-card";

    const h = document.createElement("h3");
    h.textContent = "Controls";
    card.appendChild(h);

    // Row: new game / undo / analyze
    const row1 = document.createElement("div");
    row1.className = "bf-controls-row";

    const newBtn = document.createElement("button");
    newBtn.textContent = "New Game";
    newBtn.onclick = () => {
      gameState.newGame();
      eventBus.emit("status:clear");
      eventBus.emit("status:info", "New game started.");
    };
    row1.appendChild(newBtn);

    const undoBtn = document.createElement("button");
    undoBtn.textContent = "Undo";
    undoBtn.onclick = () => {
      const res = gameState.requestUndo();
      if (!res.success) {
        eventBus.emit("status:error", `Undo failed: ${res.reason}`);
      } else {
        eventBus.emit("status:info", "Move undone.");
      }
    };
    row1.appendChild(undoBtn);

    const analyzeBtn = document.createElement("button");
    analyzeBtn.textContent = "Analyze (Backend)";
    analyzeBtn.onclick = async () => {
      try {
        const fen = gameState.getFen();
        const result = await analyzePosition(fen, 8);
        const best = result.best_move;
        eventBus.emit(
          "status:info",
          `Engine suggests: ${best.san || best.uci || "?"}`
        );
      } catch (err) {
        console.error(err);
        eventBus.emit(
          "status:error",
          "Backend analysis failed or not available."
        );
      }
    };
    row1.appendChild(analyzeBtn);

    card.appendChild(row1);

    // Checkboxes
    const checkBoxBlock = document.createElement("div");
    checkBoxBlock.className = "bf-checkbox-row";

    const hlLabel = document.createElement("label");
    const hlChk = document.createElement("input");
    hlChk.type = "checkbox";
    hlChk.checked = config.highlight_valid_moves;
    hlChk.onchange = () =>
      gameState.updateConfig({
        highlight_valid_moves: hlChk.checked,
      });
    hlLabel.appendChild(hlChk);
    hlLabel.append(" Highlight legal moves");
    checkBoxBlock.appendChild(hlLabel);

    const tbLabel = document.createElement("label");
    const tbChk = document.createElement("input");
    tbChk.type = "checkbox";
    tbChk.checked = config.allow_takeback;
    tbChk.onchange = () =>
      gameState.updateConfig({
        allow_takeback: tbChk.checked,
      });
    tbLabel.appendChild(tbChk);
    tbLabel.append(" Allow takeback");
    checkBoxBlock.appendChild(tbLabel);

    card.appendChild(checkBoxBlock);

    rootEl.appendChild(card);
  }

  // re-render if config changes
  eventBus.on("configChanged", () => render());

  return { render };
}
