from __future__ import annotations

import time
from threading import Lock


class GlobalRateLimiter:
    def __init__(self, *, max_requests: int, per_seconds: int):
        if max_requests <= 0:
            raise ValueError("max_requests inválido")
        if per_seconds <= 0:
            raise ValueError("per_seconds inválido")
        self._min_interval = per_seconds / max_requests
        self._lock = Lock()
        self._last_at: float | None = None

    def wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            if self._last_at is None:
                self._last_at = now
                return

            elapsed = now - self._last_at
            if elapsed < self._min_interval:
                time.sleep(self._min_interval - elapsed)

            self._last_at = time.monotonic()
