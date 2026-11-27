"""Cache JSON theo khoá sha1(params). SEARCH_MODE: live (mặc định) | record | replay, đọc lúc gọi."""
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Callable

from . import CacheMiss

_DEFAULT_DIR = Path(__file__).resolve().parents[5] / "data" / "cache"


def cache_dir() -> Path:
    return Path(os.environ.get("CACHE_DIR") or _DEFAULT_DIR)


def search_mode() -> str:
    return os.environ.get("SEARCH_MODE", "live").strip().lower() or "live"


def cached_call(namespace: str, params: dict, fetch: Callable[[], Any]) -> Any:
    key = hashlib.sha1(json.dumps(params, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    path = cache_dir() / namespace / f"{key}.json"
    mode = search_mode()
    if mode != "record" and path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    if mode == "replay":
        raise CacheMiss(namespace, params)
    result = fetch()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    return result
