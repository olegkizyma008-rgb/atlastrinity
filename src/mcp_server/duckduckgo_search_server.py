import html
import re
from typing import Any, Dict, List

import requests
from mcp.server import FastMCP

server = FastMCP("duckduckgo-search")


def _search_ddg(query: str, max_results: int, timeout_s: float) -> List[Dict[str, Any]]:
    url = "https://html.duckduckgo.com/html/"
    resp = requests.get(
        url,
        params={"q": query},
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        },
        timeout=timeout_s,
    )
    resp.raise_for_status()

    # DuckDuckGo HTML results include anchors with class="result__a"
    pattern = re.compile(
        r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
        re.IGNORECASE | re.DOTALL,
    )

    results: List[Dict[str, Any]] = []
    for match in pattern.finditer(resp.text):
        href = html.unescape(match.group(1)).strip()
        title_html = match.group(2)
        title = html.unescape(re.sub(r"<.*?>", "", title_html)).strip()
        if not href or not title:
            continue
        results.append({"title": title, "url": href})
        if len(results) >= max_results:
            break

    return results


@server.tool()
def duckduckgo_search(
    query: str, max_results: int = 5, timeout_s: float = 10.0
) -> Dict[str, Any]:
    if not query or not query.strip():
        return {"error": "query is required"}

    try:
        max_results_i = int(max_results)
        if max_results_i <= 0:
            return {"error": "max_results must be > 0"}
        max_results_i = min(max_results_i, 20)

        timeout_f = float(timeout_s)
        if timeout_f <= 0:
            return {"error": "timeout_s must be > 0"}

        results = _search_ddg(
            query=query.strip(), max_results=max_results_i, timeout_s=timeout_f
        )
        return {"success": True, "query": query.strip(), "results": results}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    server.run()
