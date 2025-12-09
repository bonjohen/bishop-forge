// FEN -> 8x8 array; row 0 = rank 8, col 0 = file a
export function fenToBoard(fen) {
  const [position] = fen.split(" ");
  const rows = position.split("/");
  if (rows.length !== 8) throw new Error("Invalid FEN");

  const board = [];
  for (const row of rows) {
    const out = [];
    for (const ch of row) {
      if (/[1-8]/.test(ch)) {
        const n = parseInt(ch, 10);
        for (let i = 0; i < n; i++) out.push(null);
      } else {
        out.push(ch);
      }
    }
    if (out.length !== 8) throw new Error("Invalid FEN row");
    board.push(out);
  }
  return board;
}

export function indexToSquare(row, col) {
  const files = "abcdefgh";
  const ranks = "87654321";
  return files[col] + ranks[row];
}
