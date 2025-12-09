export function getDefaultConfig() {
  return {
    highlight_valid_moves: true,
    allow_takeback: true,
  };
}

export function mergeConfig(base, patch) {
  return { ...base, ...(patch || {}) };
}
