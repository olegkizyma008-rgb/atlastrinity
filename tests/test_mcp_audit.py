#!/usr/bin/env python3
"""
Comprehensive MCP Server Audit Test
Tests ALL configured MCP servers individually.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.brain.mcp_manager import mcp_manager  # noqa: E402

# All servers from config
ALL_SERVERS = [
    # Core
    "filesystem",
    "terminal",
    "computer-use",
    "applescript",
    # Web
    "puppeteer",
    "brave-search",
    "fetch",
    # Dev
    "github",
    "git",
    # Data
    "memory",
    "postgres",
    # AI
    "whisper-stt",
    # Productivity
    "time",
    "sequential-thinking",
]


async def run_server_test(name: str) -> dict:
    """Test a single server."""
    result = {"name": name, "status": "unknown", "tools": 0, "error": None}
    try:
        tools = await mcp_manager.list_tools(name)
        if tools:
            result["status"] = "ok"
            result["tools"] = len(tools)
            print(f"✅ {name:25} | {len(tools):3} tools")
        else:
            result["status"] = "no_tools"
            print(f"⚠️  {name:25} | No tools found")
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)[:50]
        print(f"❌ {name:25} | Error: {str(e)[:40]}")
    return result


# Pytest wrapper
import pytest  # noqa: E402


@pytest.mark.asyncio
async def test_mcp_server_individual(name: str):
    result = await run_server_test(name)
    assert result["status"] in (
        "ok",
        "no_tools",
    ), f"Server {name} error: {result.get('error')}"


async def main():
    print("=" * 60)
    print("MCP Server Audit - Individual Server Tests")
    print("=" * 60)
    print()

    results = []
    for server in ALL_SERVERS:
        result = await run_server_test(server)
        results.append(result)
        await asyncio.sleep(0.5)  # Small delay between tests

    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    ok = sum(1 for r in results if r["status"] == "ok")
    no_tools = sum(1 for r in results if r["status"] == "no_tools")
    errors = sum(1 for r in results if r["status"] == "error")
    print(f"✅ OK: {ok} | ⚠️  No Tools: {no_tools} | ❌ Errors: {errors}")
    print()

    if errors > 0:
        print("Servers with errors:")
        for r in results:
            if r["status"] == "error":
                print(f"  - {r['name']}: {r['error']}")

    await mcp_manager.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
