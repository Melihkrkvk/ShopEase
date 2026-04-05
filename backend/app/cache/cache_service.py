from abc import ABC, abstractmethod


class CacheService(ABC):
    """
    Abstract base class for all cache implementations.

    Defines a simple key-value interface with TTL support.
    Services depend on this abstraction — the concrete implementation
    (InMemoryCache or any future backend) is injected via DI.
    """

    @abstractmethod
    def get(self, key: str) -> object | None:
        """
        Retrieve a cached value by key.

        Args:
            key (str): The cache key to look up.

        Returns:
            object | None: The cached value, or None if not found or expired.
        """
        ...

    @abstractmethod
    def set(self, key: str, value: object, ttl: int = 300) -> None:
        """
        Store a value in the cache with a time-to-live.

        Args:
            key (str): The cache key.
            value (object): The value to store.
            ttl (int): Seconds until the entry expires. Defaults to 300.
        """
        ...

    @abstractmethod
    def delete(self, key: str) -> None:
        """
        Remove a single entry from the cache.

        Args:
            key (str): The cache key to remove.
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Remove all entries from the cache."""
        ...
