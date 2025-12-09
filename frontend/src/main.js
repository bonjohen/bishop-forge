import { createEventBus } from "./utils/eventBus.js";
import { createGameState } from "./core/gameState.js";
import { getDefaultConfig } from "./core/rulesConfig.js";
import { createBoardView } from "./ui/boardView.js";
import { createControlsView } from "./ui/controlsView.js";
import { createStatusView } from "./ui/statusView.js";

const appEl = document.getElementById("app");

function bootstrap() {
  const bus = createEventBus();
  const gameState = createGameState(bus, getDefaultConfig());

  const layout = document.createElement("div");
  layout.className = "bf-layout";

  const leftCol = document.createElement("div");
  const rightCol = document.createElement("div");
  rightCol.className = "bf-sidepanel";

  const boardRoot = document.createElement("div");
  const controlsRoot = document.createElement("div");
  const statusRoot = document.createElement("div");

  // Controls above board, status below
  leftCol.appendChild(controlsRoot);
  leftCol.appendChild(boardRoot);
  leftCol.appendChild(statusRoot);

  layout.appendChild(leftCol);
  layout.appendChild(rightCol);
  appEl.appendChild(layout);

  const boardView = createBoardView(boardRoot, gameState, bus);
  const controlsView = createControlsView(
    controlsRoot,
    gameState,
    bus
  );
  const statusView = createStatusView(statusRoot, gameState, bus);

  controlsView.render();
  boardView.render();
  statusView.render();

  bus.on("gameStateChanged", () => boardView.render());

  console.log("Project BishopForge frontend initialized.");
}

bootstrap();
