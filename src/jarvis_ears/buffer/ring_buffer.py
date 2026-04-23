"""RAM-only ring buffer for recent audio bytes."""

from __future__ import annotations

from collections import deque


class RingBuffer:
    """Keep the most recent bytes up to a fixed capacity."""

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be greater than zero")
        self.capacity = capacity
        self._chunks: deque[bytes] = deque()
        self._size = 0

    @property
    def size(self) -> int:
        return self._size

    def append(self, data: bytes) -> None:
        if not data:
            return

        if len(data) >= self.capacity:
            self._chunks.clear()
            self._chunks.append(data[-self.capacity :])
            self._size = self.capacity
            return

        self._chunks.append(data)
        self._size += len(data)
        self._trim()

    def get_bytes(self) -> bytes:
        return b"".join(self._chunks)

    def clear(self) -> None:
        self._chunks.clear()
        self._size = 0

    def _trim(self) -> None:
        overflow = self._size - self.capacity
        while overflow > 0 and self._chunks:
            oldest = self._chunks[0]
            if len(oldest) <= overflow:
                self._chunks.popleft()
                self._size -= len(oldest)
                overflow -= len(oldest)
                continue

            self._chunks[0] = oldest[overflow:]
            self._size -= overflow
            overflow = 0
