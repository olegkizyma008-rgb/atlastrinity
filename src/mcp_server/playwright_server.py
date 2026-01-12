"""
Playwright MCP Server

Exposes web browsing capabilities via Playwright.
"""

import os
import tempfile

from mcp.server import FastMCP
from playwright.async_api import async_playwright

# Initialize FastMCP server
server = FastMCP("playwright")

# Global browser instance (reused for performance in one-shot calls if needed,
# although FastMCP might restart the script depending on mcp_manager)
_browser = None
_context = None
_page = None


async def get_page():
    global _browser, _context, _page
    if not _page:
        playwright = await async_playwright().start()
        _browser = await playwright.chromium.launch(headless=True)
        _context = await _browser.new_context()
        _page = await _context.new_page()
    return _page


@server.tool()
async def playwright_navigate(url: str) -> str:
    """Navigate to a URL."""
    try:
        pw = await async_playwright().start()
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        title = await page.title()
        # Keep it simple for one-shot: we can't easily persist the browser across calls
        # in the current MCPManager one-shot model.
        # So we return some content.
        await browser.close()
        return f"Navigated to {url}. Page Title: {title}"
    except Exception as e:
        return f"Navigation failed: {str(e)}"


@server.tool()
async def playwright_screenshot() -> str:
    """Take a screenshot of the current page (Demo: returns path)."""
    # In a one-shot model, this is tricky as the page is gone.
    # We will just return a message saying it needs persistent connection
    # OR we implement a combined tool if needed.
    return (
        "Screenshot tool requires a persistent session (not yet supported in one-shot)."
    )


@server.tool()
async def playwright_click(selector: str, url_context: str = None) -> str:
    """Click an element. If url_context is provided, navigates first."""
    try:
        pw = await async_playwright().start()
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        if url_context:
            await page.goto(url_context, wait_until="networkidle")
        await page.click(selector)
        await browser.close()
        return f"Clicked {selector}"
    except Exception as e:
        return f"Click failed: {str(e)}"


@server.tool()
async def playwright_fill(selector: str, value: str, url_context: str = None) -> str:
    """Fill an input. If url_context is provided, navigates first."""
    try:
        pw = await async_playwright().start()
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        if url_context:
            await page.goto(url_context, wait_until="networkidle")
        await page.fill(selector, value)
        await browser.close()
        return f"Filled {selector} with {value}"
    except Exception as e:
        return f"Fill failed: {str(e)}"


if __name__ == "__main__":
    server.run()
