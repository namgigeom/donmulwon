"""Shared in-process market/data cache for one Donmulwon analysis session.

The four specialist agents run concurrently. Without a shared cache, identical
market-data requests can hit Yahoo/API endpoints several times in the same
question. This module deduplicates those requests and gives every specialist
access to the same snapshot for the duration of a short TTL.
"""

import copy
import threading
import time
from typing import Any, Callable


_DEFAULT_TTL = 45.0
_CACHE: dict[tuple[str, str], tuple[float, Any]] = {}
_LOCK = threading.RLock()
_STATS = {"hits": 0, "misses": 0}


def _key(namespace: str, value: Any) -> tuple[str, str]:
    return namespace, repr(value)


def get_or_fetch(
    namespace: str,
    value: Any,
    fetcher: Callable[[], Any],
    ttl: float = _DEFAULT_TTL,
) -> Any:
    """Return cached data or fetch it once.

    The lock intentionally covers the fetch on a cache miss. The analysis is
    short-lived and correctness/API deduplication is more important here than
    allowing duplicate concurrent requests.
    """
    key = _key(namespace, value)
    now = time.monotonic()

    with _LOCK:
        cached = _CACHE.get(key)
        if cached and now - cached[0] < ttl:
            _STATS["hits"] += 1
            return copy.deepcopy(cached[1])

        _STATS["misses"] += 1
        result = fetcher()
        _CACHE[key] = (time.monotonic(), copy.deepcopy(result))
        return copy.deepcopy(result)


def clear() -> None:
    with _LOCK:
        _CACHE.clear()
        _STATS["hits"] = 0
        _STATS["misses"] = 0


def stats() -> dict[str, int]:
    with _LOCK:
        return dict(_STATS)
