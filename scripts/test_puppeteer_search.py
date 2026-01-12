#!/usr/bin/env python3
"""Puppeteer realistic scenario test: search for a torrent and extract first link."""
import asyncio
import urllib.parse

from src.brain.mcp_manager import mcp_manager


async def run_search():
    query = "Горнична 2026"
    encoded = urllib.parse.quote(query)
    url = f"https://1337x.to/search/{encoded}/1/"

    print("Navigating to:", url)
    nav = await mcp_manager.call_tool("puppeteer", "puppeteer_navigate", {"url": url})
    print("Navigate result:", nav)

    print("Waiting a moment for page to stabilize...")
    await asyncio.sleep(2)

    print("Taking search screenshot (base64)...")
    shot = await mcp_manager.call_tool(
        "puppeteer", "puppeteer_screenshot", {"name": "1337x_search", "encoded": True}
    )
    print(
        "Screenshot result:", "ok" if shot and not shot.get("isError", False) else shot
    )

    print("Attempting to extract first torrent link via evaluate script...")
    script = """(() => {
        // Try several common selectors for 1337x-like layouts
        const selectors = [
            'table.table-list a[href*="/torrent/"]',
            'a[href*="/torrent/"]',
            'table tr a'
        ];
        for (const sel of selectors) {
            const el = document.querySelector(sel);
            if (el) {
                return el.href || el.getAttribute('href');
            }
        }
        return null;
    })();"""

    eval_res = await mcp_manager.call_tool(
        "puppeteer", "puppeteer_evaluate", {"script": script}
    )
    print("Evaluate result:", eval_res)

    # Cleanup
    healthy = await mcp_manager.health_check("puppeteer")
    print("Puppeteer health:", healthy)
    await mcp_manager.cleanup()


if __name__ == "__main__":
    asyncio.run(run_search())
