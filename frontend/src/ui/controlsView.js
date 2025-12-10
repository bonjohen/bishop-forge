import {
  analyzePosition,
  getGPUStatus,
  toggleGPU,
  getOpponentMove
} from "../api/backendClient.js";

export function createControlsView(rootEl, gameState, eventBus) {
  let gpuStatus = null;
  let opponentConfig = gameState.getOpponentConfig();

  async function loadGPUStatus() {
    try {
      gpuStatus = await getGPUStatus();
      render();
    } catch (err) {
      console.error("Failed to load GPU status:", err);
    }
  }

  function render() {
    const config = gameState.getConfig();

    rootEl.innerHTML = "";
    const card = document.createElement("div");
    card.className = "bf-card";

    const h = document.createElement("h3");
    h.textContent = "Controls";
    card.appendChild(h);

    // === GPU Status and Opponent Selection (Top Section) ===
    const topSection = document.createElement("div");
    topSection.className = "bf-controls-top-section";
    topSection.style.cssText = "margin-bottom: 15px; padding: 10px; background: #f5f5f5; border-radius: 4px;";

    // GPU Status Row
    if (gpuStatus && gpuStatus.gpu_available) {
      const gpuRow = document.createElement("div");
      gpuRow.style.cssText = "margin-bottom: 10px;";

      const gpuLabel = document.createElement("label");
      const gpuChk = document.createElement("input");
      gpuChk.type = "checkbox";
      gpuChk.checked = gpuStatus.gpu_enabled;
      gpuChk.onchange = async () => {
        try {
          await toggleGPU(gpuChk.checked);
          eventBus.emit("status:info", `GPU ${gpuChk.checked ? 'enabled' : 'disabled'}`);
          await loadGPUStatus();
        } catch (err) {
          console.error("GPU toggle failed:", err);
          eventBus.emit("status:error", "Failed to toggle GPU");
        }
      };
      gpuLabel.appendChild(gpuChk);
      gpuLabel.append(` Use GPU (${gpuStatus.backend_info})`);
      gpuLabel.style.cssText = "font-weight: bold; color: #2c5aa0;";
      gpuRow.appendChild(gpuLabel);
      topSection.appendChild(gpuRow);
    }

    // Opponent Selection Row
    const opponentRow = document.createElement("div");
    opponentRow.style.cssText = "display: flex; align-items: center; gap: 10px;";

    const opponentLabel = document.createElement("label");
    opponentLabel.textContent = "Play against:";
    opponentLabel.style.cssText = "font-weight: bold;";
    opponentRow.appendChild(opponentLabel);

    const opponentSelect = document.createElement("select");
    opponentSelect.style.cssText = "flex: 1; padding: 5px;";

    const opponents = [
      { value: "none", label: "Human (No Computer)" },
      { value: "random", label: "Random Mover" },
      { value: "aggressive", label: "High Aggressive" },
      { value: "defensive", label: "High Defensive" },
      { value: "moderate", label: "Moderate" },
      { value: "defensive_passive", label: "Defensive Passive" }
    ];

    opponents.forEach(opp => {
      const option = document.createElement("option");
      option.value = opp.value;
      option.textContent = opp.label;
      if (opp.value === (opponentConfig.enabled ? opponentConfig.profile : "none")) {
        option.selected = true;
      }
      opponentSelect.appendChild(option);
    });

    opponentSelect.onchange = () => {
      const value = opponentSelect.value;
      if (value === "none") {
        gameState.setOpponent(false, null);
        eventBus.emit("status:info", "Playing against human");
      } else {
        gameState.setOpponent(true, value);
        const opponentName = opponents.find(o => o.value === value)?.label || value;
        eventBus.emit("status:info", `Playing against: ${opponentName}`);
      }
      opponentConfig = gameState.getOpponentConfig();
    };

    opponentRow.appendChild(opponentSelect);
    topSection.appendChild(opponentRow);
    card.appendChild(topSection);

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

  // Load GPU status on init
  loadGPUStatus();

  return { render };
}
