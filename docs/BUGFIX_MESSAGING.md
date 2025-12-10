# Bug Fix: Messaging Issues

## Date: 2025-12-10

## Issues Fixed

### 1. Messages Not Cleared on "New Game"
**Problem**: When clicking "New Game", old messages remained in the status view.

**Root Cause**: The `messages` array in `statusView.js` was never cleared when a new game started.

**Solution**:
1. Added `clearMessages()` function to `statusView.js`
2. Added event listener for `status:clear` event
3. Emit `status:clear` event before "New game started" message in `controlsView.js`

**Files Modified**:
- `frontend/src/ui/statusView.js`: Added `clearMessages()` function and event listener
- `frontend/src/ui/controlsView.js`: Emit `status:clear` before new game message

### 2. Move Played Message Shows "null → d5"
**Problem**: Move messages showed `Move played: null → d5` instead of `Move played: d7 → d5`.

**Root Cause**: The `selectedSquare` variable was being used after `clearSelection()` was called, or the variable was being cleared before the message was emitted.

**Solution**:
1. Store `selectedSquare` in a local variable `fromSquare` before applying the move
2. Use the move result's SAN notation if available: `res.move?.san`
3. Fall back to `${fromSquare} → ${square}` if SAN is not available

**Files Modified**:
- `frontend/src/ui/boardView.js`: Store `fromSquare` before move, use SAN notation from move result

## Code Changes

### statusView.js
```javascript
function clearMessages() {
  messages.length = 0;
  render();
}

// Added event listener
eventBus.on("status:clear", () => clearMessages());
```

### controlsView.js
```javascript
newBtn.onclick = () => {
  gameState.newGame();
  eventBus.emit("status:clear");  // Clear messages first
  eventBus.emit("status:info", "New game started.");
};
```

### boardView.js
```javascript
const fromSquare = selectedSquare;  // Store before clearing
const res = gameState.applyMove(fromSquare, square, promotion);
if (!res.success) {
  eventBus.emit("status:error", `Illegal move: ${fromSquare} → ${square}`);
} else {
  // Use SAN notation from move result
  const moveStr = res.move?.san || `${fromSquare} → ${square}`;
  eventBus.emit("status:info", `Move played: ${moveStr}`);
}
```

## Testing

### Manual Testing Steps
1. Start the frontend application
2. Make a move (e.g., e2 → e4)
3. Verify message shows: `Move played: e4` (SAN notation)
4. Make another move
5. Click "New Game"
6. Verify messages are cleared
7. Verify only "New game started" message appears
8. Make a move (e.g., d7 → d5)
9. Verify message shows: `Move played: d5` (not "null → d5")

### Expected Results
- ✅ Messages cleared on new game
- ✅ Move messages show correct SAN notation (e.g., "e4", "Nf3", "d5")
- ✅ No "null" values in move messages

## Status
✅ **FIXED** - Both issues resolved and ready for testing

