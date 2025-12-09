from __future__ import annotations

import time
from typing import Any, Dict, Tuple, Optional

from .config import settings


class SimpleCache:
    """
    Minimal in-memory cache keyed by (fen, depth).
    Intended as a drop-in placeholder for a future Redis-based cache.
    """

    def __init__(self) -> None:
        self._store: Dict[Tuple[str, int], Tuple[float, Any]] = {}
        self.ttl_seconds = 300  # 5 minutes

    def make_key(self, fen: str, depth: int) -> Tuple[str, int]:
        return fen, depth

    def get(self, fen: str, depth: int) -> Optional[Any]:
        if not settings.CACHE_ENABLED:
            return None

        key = self.make_key(fen, depth)
        item = self._store.get(key)
        if not item:
            return None
        ts, value = item
        if time.time() - ts > self.ttl_seconds:
            self._store.pop(key, None)
            return None
        return value

    def set(self, fen: str, depth: int, value: Any) -> None:
        if not settings.CACHE_ENABLED:
            return
        key = self.make_key(fen, depth)
        self._store[key] = (time.time(), value)


cache = SimpleCache()
