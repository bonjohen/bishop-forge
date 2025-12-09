export function createEventBus() {
  const handlers = new Map();

  function on(event, handler) {
    if (!handlers.has(event)) handlers.set(event, new Set());
    handlers.get(event).add(handler);
  }

  function off(event, handler) {
    if (!handlers.has(event)) return;
    handlers.get(event).delete(handler);
  }

  function emit(event, payload) {
    if (!handlers.has(event)) return;
    for (const fn of handlers.get(event)) {
      try {
        fn(payload);
      } catch (err) {
        console.error(`EventBus handler error for "${event}"`, err);
      }
    }
  }

  return { on, off, emit };
}
