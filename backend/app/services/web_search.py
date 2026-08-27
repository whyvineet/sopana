from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

logger = logging.getLogger(__name__)

_query_cache: dict[str, tuple[float, list["SearchResult"]]] = {}
_CACHE_TTL_SECONDS = 3600 


@dataclass
class SearchResult:
    title: str
    url: str
    content: str
    score: float | None = None


class WebSearchService:
    def __init__(self, tavily_api_key: str = "", timeout: int = 10, max_results: int = 5) -> None:
        self._tavily_key = tavily_api_key
        self._timeout = timeout
        self._max_results = max_results

    def search(self, query: str, max_results: int | None = None) -> list[SearchResult]:
        n = max_results or self._max_results
        cache_key = self._cache_key(query, n)

        if cache_key in _query_cache:
            ts, results = _query_cache[cache_key]
            if time.time() - ts < _CACHE_TTL_SECONDS:
                logger.debug("Web search cache hit: %s", query[:60])
                return results

        results = self._search_uncached(query, n)
        _query_cache[cache_key] = (time.time(), results)
        return results

    def search_multiple(
        self, queries: list[str], max_per_query: int = 3
    ) -> list[SearchResult]:
        seen_urls: set[str] = set()
        combined: list[SearchResult] = []
        for q in queries:
            try:
                for r in self.search(q, max_results=max_per_query):
                    if r.url not in seen_urls:
                        seen_urls.add(r.url)
                        combined.append(r)
            except Exception as exc:
                logger.warning("Query failed (%s): %s", q[:50], exc)
        return combined


    def _search_uncached(self, query: str, max_results: int) -> list[SearchResult]:
        if self._tavily_key:
            try:
                return self._tavily_search(query, max_results)
            except Exception as exc:
                logger.warning("Tavily search failed (%s); trying DuckDuckGo", exc)

        try:
            return self._duckduckgo_search(query, max_results)
        except Exception as exc:
            logger.warning("DuckDuckGo search failed (%s); returning empty results", exc)
            return []

    def _tavily_search(self, query: str, max_results: int) -> list[SearchResult]:
        from tavily import TavilyClient
        client = TavilyClient(api_key=self._tavily_key)
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="basic",
        )
        results: list[SearchResult] = []
        for item in response.get("results", []):
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                content=item.get("content", item.get("snippet", "")),
                score=item.get("score"),
            ))
        return results

    def _duckduckgo_search(self, query: str, max_results: int) -> list[SearchResult]:
        from duckduckgo_search import DDGS
        results: list[SearchResult] = []
        with DDGS() as ddgs:
            for item in ddgs.text(query, max_results=max_results):
                results.append(SearchResult(
                    title=item.get("title", ""),
                    url=item.get("href", ""),
                    content=item.get("body", ""),
                ))
        return results

    @staticmethod
    def _cache_key(query: str, max_results: int) -> str:
        raw = f"{query}::{max_results}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


_search_service: WebSearchService | None = None


@lru_cache
def get_web_search_service() -> WebSearchService:
    from app.core.config import get_settings
    settings = get_settings()
    return WebSearchService(
        tavily_api_key=settings.tavily_api_key,
        timeout=settings.search_timeout_seconds,
        max_results=settings.search_max_results,
    )
