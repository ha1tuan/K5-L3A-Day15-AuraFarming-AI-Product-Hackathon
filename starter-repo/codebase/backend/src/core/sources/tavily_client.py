"""Tìm kiếm web qua Tavily, có cache. Thiếu key ở live/record -> SearchUnavailable."""
import os
import re
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

from . import SearchUnavailable
from .cache import cached_call

TAVILY_URL = "https://api.tavily.com/search"


@dataclass
class SearchHit:
    title: str
    url: str
    snippet: str
    domain: str


def _trim_sentences(text: str, n: int = 2) -> str:
    parts = re.split(r"(?<=[.!?])\s+", (text or "").strip())
    return " ".join(parts[:n])


def _domain(url: str) -> str:
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def _fetch(query: str, max_results: int) -> list[dict]:
    key = os.environ.get("TAVILY_API_KEY")
    if not key:
        raise SearchUnavailable("thiếu TAVILY_API_KEY")
    resp = httpx.post(
        TAVILY_URL,
        json={"api_key": key, "query": query, "max_results": max_results},
        timeout=20,
    )
    resp.raise_for_status()
    return [
        {
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "domain": _domain(r.get("url", "")),
            "snippet": _trim_sentences(r.get("content", "")),
        }
        for r in resp.json().get("results", [])
    ]


def search(query: str, max_results: int = 8) -> list[SearchHit]:
    try:
        raw = cached_call("tavily", {"query": query, "max_results": max_results},
                          lambda: _fetch(query, max_results))
    except (httpx.HTTPError, ValueError) as e:  # ValueError: phản hồi không phải JSON
        raise SearchUnavailable(str(e)) from e
    return [SearchHit(r["title"], r["url"], r["snippet"], r["domain"]) for r in raw]
