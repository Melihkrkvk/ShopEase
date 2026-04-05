import time
from threading import RLock

from app.cache.cache_service import CacheService


class InMemoryCache(CacheService):
    """
    Thread-safe in-memory cache with TTL support.

    Stores values in a plain dict. Expired entries are lazily evicted
    on read. Uses RLock for safe concurrent access.

    Attributes:
        _store (dict): Maps cache keys to (value, expires_at) tuples.
        _lock (RLock): Reentrant lock protecting all store operations.
    """

    def __init__(self) -> None:
        """Initialize an empty in-memory cache with a reentrant lock."""
        self._store: dict[str, tuple[object, float]] = {}
        self._lock = RLock()

    def get(self, key: str) -> object | None:
        """
        Retrieve a cached value, evicting it if expired.

        Args:
            key (str): The cache key to look up.

        Returns:
            object | None: The cached value, or None if missing or expired.
        """
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if time.time() > expires_at:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: object, ttl: int = 300) -> None:
        """
        Store a value with an expiry timestamp.

        Args:
            key (str): The cache key.
            value (object): The value to store.
            ttl (int): Seconds until expiry. Defaults to 300.
        """
        with self._lock:
            self._store[key] = (value, time.time() + ttl)

    def delete(self, key: str) -> None:
        """
        Remove a single cache entry.

        Args:
            key (str): The key to remove. No-op if not present.
        """
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        """Remove all cache entries."""
        with self._lock:
            self._store.clear()
