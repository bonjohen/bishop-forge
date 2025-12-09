export function createStatusView(rootEl, gameState, eventBus) {
  const messages = [];

  function pushMessage(type, text) {
    const ts = new Date().toLocaleTimeString();
    messages.unshift({ type, text, ts });
    if (messages.length > 5) messages.pop();
    render();
  }

  function render() {
    const status = gameState.getStatus();
    const history = gameState.getHistory();

    rootEl.innerHTML = "";

    const card = document.createElement("div");
    card.className = "bf-card";

    const h = document.createElement("h3");
    h.textContent = "Status";
    card.appendChild(h);

    const turnText = status.turn === "w" ? "White" : "Black";
    let line = `Turn: ${turnText}`;
    if (status.isCheckmate) line += " — Checkmate";
    else if (status.isStalemate) line += " — Stalemate";
    else if (status.isDraw) line += " — Draw";
    else if (status.isCheck) line += " — Check";

    const p = document.createElement("p");
    p.textContent = line;
    card.appendChild(p);

    const movesTitle = document.createElement("strong");
    movesTitle.textContent = "Moves:";
    card.appendChild(movesTitle);

    const ol = document.createElement("ol");
    ol.style.paddingLeft = "20px";
    history.forEach((m) => {
      const li = document.createElement("li");
      li.textContent = m.san || `${m.from}-${m.to}`;
      ol.appendChild(li);
    });
    card.appendChild(ol);

    const msgTitle = document.createElement("strong");
    msgTitle.textContent = "Messages:";
    card.appendChild(msgTitle);

    const ul = document.createElement("ul");
    ul.style.paddingLeft = "20px";
    messages.forEach((m) => {
      const li = document.createElement("li");
      li.className =
        m.type === "error" ? "bf-msg-error" : "bf-msg-info";
      li.textContent = `[${m.ts}] ${m.text}`;
      ul.appendChild(li);
    });
    card.appendChild(ul);

    rootEl.appendChild(card);
  }

  eventBus.on("gameStateChanged", () => render());
  eventBus.on("status:info", (t) => pushMessage("info", t));
  eventBus.on("status:error", (t) => pushMessage("error", t));

  return { render };
}
