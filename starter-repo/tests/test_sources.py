import pytest

from src.core.sources import CacheMiss, SearchUnavailable, cache, geo, tavily_client


@pytest.fixture(autouse=True)
def _cache_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("CACHE_DIR", str(tmp_path))
    monkeypatch.delenv("SEARCH_MODE", raising=False)


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def test_cache_live_writes_then_reuses(tmp_path):
    calls = []

    def fetch():
        calls.append(1)
        return {"a": 1}

    assert cache.cached_call("ns", {"q": "x"}, fetch) == {"a": 1}
    assert cache.cached_call("ns", {"q": "x"}, fetch) == {"a": 1}
    assert len(calls) == 1
    assert len(list((tmp_path / "ns").glob("*.json"))) == 1


def test_cache_record_always_fetches(monkeypatch):
    calls = []
    monkeypatch.setenv("SEARCH_MODE", "record")
    cache.cached_call("ns", {"q": 1}, lambda: calls.append(1) or [1])
    cache.cached_call("ns", {"q": 1}, lambda: calls.append(1) or [2])
    assert len(calls) == 2
    monkeypatch.setenv("SEARCH_MODE", "replay")
    assert cache.cached_call("ns", {"q": 1}, lambda: pytest.fail("no fetch")) == [2]


def test_cache_replay_miss_raises(monkeypatch):
    monkeypatch.setenv("SEARCH_MODE", "replay")
    with pytest.raises(CacheMiss):
        cache.cached_call("ns", {"q": "missing"}, lambda: pytest.fail("no fetch"))


def test_search_trims_snippet_to_two_sentences(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "k")
    payload = {"results": [{
        "title": "Khach san A",
        "url": "https://www.vnexpress.net/bai-viet",
        "content": "Cau mot. Cau hai! Cau ba. Cau bon.",
    }]}
    monkeypatch.setattr(tavily_client.httpx, "post", lambda *a, **k: FakeResponse(payload))
    hits = tavily_client.search("khach san da lat")
    assert len(hits) == 1
    assert hits[0].snippet == "Cau mot. Cau hai!"
    assert hits[0].domain == "vnexpress.net"


def test_search_without_key_raises_unavailable(monkeypatch):
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    with pytest.raises(SearchUnavailable):
        tavily_client.search("khach san da lat")


def test_geocode_none_when_empty(monkeypatch):
    monkeypatch.setattr(geo.time, "sleep", lambda s: None)
    monkeypatch.setattr(geo.httpx, "get", lambda *a, **k: FakeResponse([]))
    assert geo.geocode("Nowhere") is None


def test_geocode_returns_point_and_uses_user_agent(monkeypatch):
    seen = {}

    def fake_get(url, params=None, headers=None, timeout=None):
        seen.update(params=params, headers=headers)
        return FakeResponse([{"lat": "11.94", "lon": "108.44", "address": {"country_code": "vn"}}])

    monkeypatch.setattr(geo.time, "sleep", lambda s: None)
    monkeypatch.setattr(geo.httpx, "get", fake_get)
    p = geo.geocode("Da Lat", domestic=True)
    assert (p.lat, p.lon, p.country_code) == (11.94, 108.44, "vn")
    assert seen["headers"]["User-Agent"] == "travel-planner-hackathon"
    assert seen["params"]["countrycodes"] == "vn"
    assert seen["params"]["limit"] == 1


def test_geocode_rate_limit(monkeypatch):
    sleeps = []
    now = [100.0]
    monkeypatch.setattr(geo.time, "monotonic", lambda: now[0])
    monkeypatch.setattr(geo.time, "sleep", lambda s: sleeps.append(s))
    monkeypatch.setattr(geo.httpx, "get", lambda *a, **k: FakeResponse([]))
    monkeypatch.setattr(geo, "_last_call", None)
    geo.geocode("A")
    now[0] += 0.25
    geo.geocode("B")
    assert sleeps and sleeps[-1] == pytest.approx(0.75)


def test_search_cache_keeps_only_trimmed_fields(monkeypatch, tmp_path):
    import json
    monkeypatch.setenv("TAVILY_API_KEY", "k")
    payload = {"results": [{
        "title": "T", "url": "https://www.vnexpress.net/x",
        "content": "Mot. Hai! Ba. Bon.", "raw_content": "long", "score": 0.9,
    }]}
    monkeypatch.setattr(tavily_client.httpx, "post", lambda *a, **k: FakeResponse(payload))
    tavily_client.search("q")
    files = list((tmp_path / "tavily").glob("*.json"))
    assert len(files) == 1
    rec = json.loads(files[0].read_text(encoding="utf-8"))[0]
    assert set(rec) == {"title", "url", "domain", "snippet"}
    assert rec["snippet"] == "Mot. Hai!"


def test_search_http_error_raises_unavailable(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "k")

    def boom(*a, **k):
        raise tavily_client.httpx.ConnectTimeout("t")

    monkeypatch.setattr(tavily_client.httpx, "post", boom)
    with pytest.raises(SearchUnavailable):
        tavily_client.search("q")


def test_geocode_http_error_returns_none(monkeypatch):
    def boom(*a, **k):
        raise geo.httpx.ConnectError("x")

    monkeypatch.setattr(geo.time, "sleep", lambda s: None)
    monkeypatch.setattr(geo.httpx, "get", boom)
    assert geo.geocode("Da Lat") is None
