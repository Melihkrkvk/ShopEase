import time

import pytest

from app.cache.in_memory_cache import InMemoryCache


@pytest.fixture
def cache():
    return InMemoryCache()


def test_get_returns_none_for_missing_key(cache):
    """Cache returns None when key does not exist."""
    assert cache.get("missing") is None


def test_set_and_get_returns_stored_value(cache):
    """Cache returns the value that was stored."""
    cache.set("product:1", {"id": 1, "name": "Widget"})
    assert cache.get("product:1") == {"id": 1, "name": "Widget"}


def test_get_returns_none_after_ttl_expires(cache):
    """Cache returns None after the TTL has elapsed."""
    cache.set("product:1", {"id": 1}, ttl=1)
    time.sleep(1.1)
    assert cache.get("product:1") is None


def test_delete_removes_entry(cache):
    """Cache returns None after an entry is deleted."""
    cache.set("product:1", {"id": 1})
    cache.delete("product:1")
    assert cache.get("product:1") is None


def test_delete_nonexistent_key_does_not_raise(cache):
    """Deleting a key that does not exist is a no-op."""
    cache.delete("nonexistent")  # should not raise


def test_clear_removes_all_entries(cache):
    """Cache is empty after clear is called."""
    cache.set("product:1", {"id": 1})
    cache.set("product:2", {"id": 2})
    cache.clear()
    assert cache.get("product:1") is None
    assert cache.get("product:2") is None


def test_set_overwrites_existing_key(cache):
    """Setting an existing key replaces the old value."""
    cache.set("k", "old")
    cache.set("k", "new")
    assert cache.get("k") == "new"


def test_concurrent_set_and_get_does_not_raise():
    """Concurrent reads and writes do not raise errors or corrupt state."""
    import threading
    cache = InMemoryCache()
    errors = []

    def writer():
        for i in range(100):
            try:
                cache.set(f"k{i}", i, ttl=10)
            except Exception as e:
                errors.append(e)

    def reader():
        for i in range(100):
            try:
                cache.get(f"k{i}")
            except Exception as e:
                errors.append(e)

    threads = [threading.Thread(target=writer) for _ in range(5)]
    threads += [threading.Thread(target=reader) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == []
