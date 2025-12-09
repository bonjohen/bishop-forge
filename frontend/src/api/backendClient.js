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
