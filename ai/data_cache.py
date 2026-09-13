"""Shared in-process market/data cache for one Donmulwon analysis session.

Concurrent specialists should share identical requests, but different cache keys
must never block each other while a network request is running.
"""
import copy
import threading
import time
from typing import Any, Callable

_DEFAULT_TTL = 45.0
_CACHE: dict[tuple[str, str], tuple[float, Any]] = {}
_LOCK = threading.RLock()
_INFLIGHT: dict[tuple[str, str], threading.Event] = {}
_STATS = {"hits": 0, "misses": 0}


def _key(namespace: str, value: Any) -> tuple[str, str]:
    return namespace, repr(value)


def get_or_fetch(namespace: str, value: Any, fetcher: Callable[[], Any], ttl: float = _DEFAULT_TTL) -> Any:
    """Return cached data; deduplicate the same key without a global network lock."""
    key = _key(namespace, value)
    while True:
        with _LOCK:
            cached = _CACHE.get(key)
            if cached and time.monotonic() - cached[0] < ttl:
                _STATS["hits"] += 1
                return copy.deepcopy(cached[1])
            event = _INFLIGHT.get(key)
            if event is None:
                event = threading.Event()
                _INFLIGHT[key] = event
                _STATS["misses"] += 1
                owner = True
            else:
                owner = False
        if owner:
            try:
                result = fetcher()
                with _LOCK:
                    _CACHE[key] = (time.monotonic(), copy.deepcopy(result))
                return copy.deepcopy(result)
            finally:
                with _LOCK:
                    _INFLIGHT.pop(key, None)
                    event.set()
        event.wait()


def clear() -> None:
    with _LOCK:
        _CACHE.clear()
        _INFLIGHT.clear()
        _STATS["hits"] = 0
        _STATS["misses"] = 0


def stats() -> dict[str, int]:
    with _LOCK:
        return dict(_STATS)
