#!/usr/bin/env python3
"""Simple test runner to exercise Puppeteer MCP via mcp_manager."""
import asyncio
import os

from src.brain.mcp_manager import mcp_manager


async def run_test():
    print("Listing configured puppeteer tools...")
    tools = await mcp_manager.list_tools("puppeteer")
    print("Tools:", tools)

    print("Navigating to example.com via puppeteer...")
    nav = await mcp_manager.call_tool(
        "puppeteer", "puppeteer_navigate", {"url": "https://example.com"}
    )
    print("Navigate result:", nav)

    print("Taking page screenshot via puppeteer...")
    shot = await mcp_manager.call_tool("puppeteer", "puppeteer_screenshot", {})
    print("Screenshot result:", shot)

    # Health check
    healthy = await mcp_manager.health_check("puppeteer")
    print("Puppeteer health:", healthy)

    # Cleanup
    await mcp_manager.cleanup()


if __name__ == "__main__":
    asyncio.run(run_test())
