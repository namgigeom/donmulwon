"""Shared in-process market/data cache for one Donmulwon analysis session.

The four specialist agents run concurrently. Without a shared cache, identical
market-data requests can hit Yahoo/API endpoints several times in the same
question. This module deduplicates those requests and gives every specialist
access to the same snapshot for the duration of a short TTL.

Locking design
--------------
`_CACHE_LOCK` only ever guards quick in-memory dict reads/writes - it is never
held while `fetcher()` (a network call) is running. Per-key locks in
`_KEY_LOCKS` make sure two threads asking for the *same* key don't both hit the
network, while threads asking for *different* keys never block each other. This
is what lets the four analyst roles in batch_engine actually run concurrently
instead of taking turns.
"""

import copy
import threading
import time
from typing import Any, Callable

_DEFAULT_TTL = 45.0
_CACHE: dict[tuple[str, str], tuple[float, Any]] = {}
_CACHE_LOCK = threading.RLock()
_KEY_LOCKS: dict[tuple[str, str], threading.Lock] = {}
_KEY_LOCKS_GUARD = threading.Lock()
_STATS = {"hits": 0, "misses": 0}
_STATS_LOCK = threading.Lock()


def _key(namespace: str, value: Any) -> tuple[str, str]:
    return namespace, repr(value)


def _get_key_lock(key: tuple[str, str]) -> threading.Lock:
    with _KEY_LOCKS_GUARD:
        lock = _KEY_LOCKS.get(key)
        if lock is None:
            lock = threading.Lock()
            _KEY_LOCKS[key] = lock
        return lock


def _record(stat: str) -> None:
    with _STATS_LOCK:
        _STATS[stat] += 1


def _read_cache(key: tuple[str, str], ttl: float):
    with _CACHE_LOCK:
        cached = _CACHE.get(key)
        if cached and time.monotonic() - cached[0] < ttl:
            return copy.deepcopy(cached[1])
    return None


def get_or_fetch(namespace: str, value: Any, fetcher: Callable[[], Any], ttl: float = _DEFAULT_TTL) -> Any:
    """Return cached data or fetch it once.

    Network calls never hold the global cache lock. A per-key lock prevents
    duplicate concurrent requests for the same market-data key, while unrelated
    keys remain fully concurrent.
    """
    key = _key(namespace, value)
    hit = _read_cache(key, ttl)
    if hit is not None:
        _record("hits")
        return hit

    key_lock = _get_key_lock(key)
    with key_lock:
        hit = _read_cache(key, ttl)
        if hit is not None:
            _record("hits")
            return hit
        _record("misses")
        result = fetcher()
        with _CACHE_LOCK:
            _CACHE[key] = (time.monotonic(), copy.deepcopy(result))
        return copy.deepcopy(result)


def clear() -> None:
    with _CACHE_LOCK:
        _CACHE.clear()
    with _KEY_LOCKS_GUARD:
        _KEY_LOCKS.clear()
    with _STATS_LOCK:
        _STATS["hits"] = 0
        _STATS["misses"] = 0


def stats() -> dict[str, int]:
    with _STATS_LOCK:
        return dict(_STATS)
