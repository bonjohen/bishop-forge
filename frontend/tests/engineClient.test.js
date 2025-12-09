import { describe, it, expect } from "vitest";
import { createEngineClient } from "../src/core/engineClient.js";

describe("engineClient", () => {
  it("initializes to the standard starting position", () => {
    const engine = createEngineClient();
    const fen = engine.getFen();
    // Basic check: contains ' w KQkq - 0 1'
    expect(fen).toContain(" w ");
  });

  it("makes a legal move e2e4", () => {
    const engine = createEngineClient();
    const result = engine.makeMove("e2", "e4");
    expect(result.success).toBe(true);
    const status = engine.getStatus();
    expect(status.turn).toBe("b");
  });

  it("rejects an illegal move", () => {
    const engine = createEngineClient();
    const result = engine.makeMove("e2", "e5");
    expect(result.success).toBe(false);
    expect(result.reason).toBe("illegal");
  });

  it("undoMove returns no_move when history empty", () => {
    const engine = createEngineClient();
    const result = engine.undoMove();
    expect(result.success).toBe(false);
    expect(result.reason).toBe("no_move");
  });
});
