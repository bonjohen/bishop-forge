import { createEngineClient } from "./engineClient.js";
import { getDefaultConfig, mergeConfig } from "./rulesConfig.js";

export function createGameState(eventBus, initialConfig) {
  const engine = createEngineClient();
  let config = mergeConfig(getDefaultConfig(), initialConfig);
  let status = engine.getStatus();
  let opponentEnabled = false;
  let opponentProfile = "random";
  let moveStartTime = null;
  let moveTimings = []; // Array of {moveIndex, timeMs, isComputer}

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
    moveStartTime = Date.now();
    moveTimings = [];
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

  function getMoveTimings() {
    return moveTimings;
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

  function applyMove(from, to, promotion, isComputer = false) {
    const res = engine.makeMove(from, to, promotion);
    if (!res.success) return res;

    // Track move timing
    const now = Date.now();
    const timeMs = moveStartTime ? now - moveStartTime : 0;
    const history = engine.getHistory();
    moveTimings.push({
      moveIndex: history.length - 1,
      timeMs,
      isComputer
    });
    moveStartTime = now;

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

  function setOpponent(enabled, profile) {
    opponentEnabled = enabled;
    opponentProfile = profile || "random";
  }

  function getOpponentConfig() {
    return {
      enabled: opponentEnabled,
      profile: opponentProfile,
    };
  }

  // init
  newGame();

  return {
    newGame,
    getFen,
    getStatus,
    getHistory,
    getMoveTimings,
    getConfig,
    updateConfig,
    getLegalMovesFrom,
    applyMove,
    requestUndo,
    setOpponent,
    getOpponentConfig,
  };
}
