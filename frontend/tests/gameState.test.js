import { describe, it, expect } from "vitest";
import { createEventBus } from "../src/utils/eventBus.js";
import { createGameState } from "../src/core/gameState.js";
import { getDefaultConfig } from "../src/core/rulesConfig.js";

describe("gameState", () => {
  function setup() {
    const bus = createEventBus();
    const gs = createGameState(bus, getDefaultConfig());
    return { bus, gs };
  }

  it("starts a new game with white to move", () => {
    const { gs } = setup();
    const status = gs.getStatus();
    expect(status.turn).toBe("w");
  });

  it("applies a legal move and changes turn", () => {
    const { gs } = setup();
    const res = gs.applyMove("e2", "e4");
    expect(res.success).toBe(true);
    const status = gs.getStatus();
    expect(status.turn).toBe("b");
  });

  it("respects allow_takeback=false", () => {
    const { gs } = setup();
    gs.updateConfig({ allow_takeback: false });
    const res = gs.requestUndo();
    expect(res.success).toBe(false);
    expect(res.reason).toBe("not_allowed");
  });

  it("undoes a move when allowed", () => {
    const { gs } = setup();
    gs.applyMove("e2", "e4");
    const res = gs.requestUndo();
    expect(res.success).toBe(true);
    const status = gs.getStatus();
    expect(status.turn).toBe("w");
  });
});
