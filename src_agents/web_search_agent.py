from __future__ import annotations

import html
import os
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import parse_qs, quote_plus, unquote, urlparse
from urllib.request import Request, urlopen


@dataclass
class WebResult:
    title: str
    url: str
    snippet: str


class DuckDuckGoHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.results: list[WebResult] = []
        self._in_title = False
        self._in_snippet = False
        self._current_title: list[str] = []
        self._current_snippet: list[str] = []
        self._current_url = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key: value or "" for key, value in attrs}
        classes = attr.get("class", "")

        if tag == "a" and "result__a" in classes:
            self._in_title = True
            self._current_title = []
            self._current_snippet = []
            self._current_url = _clean_duckduckgo_url(attr.get("href", ""))
        elif "result__snippet" in classes:
            self._in_snippet = True
            self._current_snippet = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._current_title.append(data)
        elif self._in_snippet:
            self._current_snippet.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._in_title:
            self._in_title = False
        elif self._in_snippet and tag in {"a", "div"}:
            self._in_snippet = False
            title = _clean_text(" ".join(self._current_title))
            snippet = _clean_text(" ".join(self._current_snippet))
            if title and self._current_url:
                self.results.append(
                    WebResult(title=title, url=self._current_url, snippet=snippet)
                )


def web_search(query: str, limit: int | None = None) -> list[WebResult]:
    if os.getenv("ENABLE_WEB_SEARCH", "1").strip() != "1":
        return []

    limit = limit or int(os.getenv("WEB_SEARCH_LIMIT", "5"))
    url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
            )
        },
    )
    with urlopen(request, timeout=20) as response:
        body = response.read().decode("utf-8", errors="replace")

    parser = DuckDuckGoHTMLParser()
    parser.feed(body)
    return parser.results[:limit]


async def run_web_search(query: str) -> str:
    try:
        results = web_search(query)
    except Exception as exc:
        return f"Web search failed for {query!r}: {type(exc).__name__}: {exc}"

    if not results:
        return f"No web results found for {query!r}."

    output = []
    for index, result in enumerate(results, start=1):
        marker = f"[Web: {result.title}]"
        output.append(
            f"{index}. {marker}\n"
            f"URL: {result.url}\n"
            f"Snippet: {result.snippet or 'No snippet available.'}"
        )
    return "\n\n".join(output)


def _clean_duckduckgo_url(raw_url: str) -> str:
    raw_url = html.unescape(raw_url)
    parsed = urlparse(raw_url)
    query = parse_qs(parsed.query)
    if "uddg" in query and query["uddg"]:
        return unquote(query["uddg"][0])
    return raw_url


def _clean_text(value: str) -> str:
    return " ".join(html.unescape(value).split())
