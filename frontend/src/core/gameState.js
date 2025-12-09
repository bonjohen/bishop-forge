import { createEngineClient } from "./engineClient.js";
import { getDefaultConfig, mergeConfig } from "./rulesConfig.js";

export function createGameState(eventBus, initialConfig) {
  const engine = createEngineClient();
  let config = mergeConfig(getDefaultConfig(), initialConfig);
  let status = engine.getStatus();

  function emitState() {
    eventBus?.emit("gameStateChanged", {
      fen: getFen(),
      status,
      history: getHistory(),
    });
  }

  function emitConfig() {
    eventBus?.emit("configChanged", getConfig());
  }

  function newGame(initialFen) {
    engine.initGame(initialFen);
    status = engine.getStatus();
    emitState();
  }

  function getFen() {
    return engine.getFen();
  }

  function getStatus() {
    return status;
  }

  function getHistory() {
    return engine.getHistory();
  }

  function getConfig() {
    return { ...config };
  }

  function updateConfig(patch) {
    config = mergeConfig(config, patch);
    emitConfig();
  }

  function getLegalMovesFrom(square) {
    return engine.getLegalMoves(square);
  }

  function applyMove(from, to, promotion) {
    const res = engine.makeMove(from, to, promotion);
    if (!res.success) return res;
    status = res.status;
    emitState();
    return res;
  }

  function requestUndo() {
    if (!config.allow_takeback) {
      return { success: false, reason: "not_allowed" };
    }
    const res = engine.undoMove();
    if (!res.success) return res;
    status = res.status;
    emitState();
    return res;
  }

  // init
  newGame();

  return {
    newGame,
    getFen,
    getStatus,
    getHistory,
    getConfig,
    updateConfig,
    getLegalMovesFrom,
    applyMove,
    requestUndo,
  };
}
