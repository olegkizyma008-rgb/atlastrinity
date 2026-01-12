import base64
import os
from typing import Any, Dict, Optional

import requests
from mcp.server import FastMCP

server = FastMCP("github")


def _gh_headers() -> Dict[str, str]:
    token = os.getenv("GITHUB_TOKEN", "").strip()
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "atlastrinity-mcp-github",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _api_get(url: str, timeout_s: float = 15.0) -> Dict[str, Any]:
    try:
        resp = requests.get(url, headers=_gh_headers(), timeout=float(timeout_s))
        if resp.status_code >= 400:
            return {"error": f"HTTP {resp.status_code}", "details": resp.text[:500]}
        return {"success": True, "json": resp.json()}
    except Exception as e:
        return {"error": str(e)}


@server.tool()
def github_whoami(timeout_s: float = 15.0) -> Dict[str, Any]:
    """Returns the authenticated user (requires GITHUB_TOKEN)."""
    if not os.getenv("GITHUB_TOKEN"):
        return {"error": "GITHUB_TOKEN is not set"}
    return _api_get("https://api.github.com/user", timeout_s=timeout_s)


@server.tool()
def get_file_contents(
    owner: str, repo: str, path: str, ref: Optional[str] = None, timeout_s: float = 20.0
) -> Dict[str, Any]:
    """Fetch file contents from GitHub and return decoded text."""
    if not owner or not repo or not path:
        return {"error": "owner, repo, path are required"}

    q = f"?ref={ref}" if ref else ""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}{q}"
    res = _api_get(url, timeout_s=timeout_s)
    if not res.get("success"):
        return res

    data = res["json"]
    if isinstance(data, dict) and data.get("type") == "file":
        content_b64 = data.get("content") or ""
        try:
            raw = base64.b64decode(content_b64, validate=False)
            text = raw.decode("utf-8", errors="replace")
        except Exception as e:
            return {"error": f"Failed to decode content: {e}"}

        return {
            "success": True,
            "sha": data.get("sha"),
            "path": data.get("path"),
            "size": data.get("size"),
            "content": text,
        }

    return {"error": "Not a file", "json": data}


if __name__ == "__main__":
    server.run()
