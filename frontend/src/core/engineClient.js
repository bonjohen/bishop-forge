import { Chess } from "chess.js";

export function createEngineClient() {
  let game = new Chess();

  function initGame(initialFen) {
    if (initialFen) {
      const tmp = new Chess();
      if (!tmp.load(initialFen)) {
        throw new Error("Invalid FEN in initGame");
      }
      game = tmp;
    } else {
      game = new Chess();
    }
  }

  function getFen() {
    return game.fen();
  }

  function getStatus() {
    return {
      turn: game.turn(), // 'w' | 'b'
      isCheck: game.isCheck(),
      isCheckmate: game.isCheckmate(),
      isStalemate: game.isStalemate(),
      isDraw: game.isDraw(),
    };
  }

  function getHistory() {
    return game.history({ verbose: true });
  }

  function getLegalMoves(fromSquare) {
    const moves = game.moves({ verbose: true });
    if (!fromSquare) return moves;
    return moves.filter((m) => m.from === fromSquare);
  }

  function makeMove(from, to, promotion) {
    if (game.isGameOver()) return { success: false, reason: "game_over" };
    try {
      const move = game.move(
        promotion ? { from, to, promotion } : { from, to }
      );
      if (!move) return { success: false, reason: "illegal" };
      return { success: true, move, status: getStatus() };
    } catch (error) {
      return { success: false, reason: "illegal" };
    }
  }

  function undoMove() {
    const undone = game.undo();
    if (!undone) return { success: false, reason: "no_move" };
    return { success: true, move: undone, status: getStatus() };
  }

  initGame();

  return {
    initGame,
    getFen,
    getStatus,
    getHistory,
    getLegalMoves,
    makeMove,
    undoMove,
  };
}
