const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function analyzePosition(fen, maxDepth = 8) {
  const res = await fetch(`${API_BASE}/analysis/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fen, max_depth: maxDepth }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Analysis API error ${res.status}: ${text}`);
  }

  return res.json();
}

export async function getGPUStatus() {
  const res = await fetch(`${API_BASE}/opponent/gpu-status`);

  if (!res.ok) {
    throw new Error(`GPU status API error ${res.status}`);
  }

  return res.json();
}

export async function toggleGPU(enable) {
  const res = await fetch(`${API_BASE}/opponent/gpu-toggle?enable=${enable}`, {
    method: "POST",
  });

  if (!res.ok) {
    throw new Error(`GPU toggle API error ${res.status}`);
  }

  return res.json();
}

export async function getOpponentMove(fen, profile = "random") {
  const res = await fetch(`${API_BASE}/opponent/move`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fen, profile }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Opponent move API error ${res.status}: ${text}`);
  }

  return res.json();
}
