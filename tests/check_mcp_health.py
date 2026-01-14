#!/usr/bin/env python3
"""
Live MCP Server Health Check
Tests each MCP server for connectivity and lists available tools.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.brain.logger import logger  # noqa: E402
from src.brain.mcp_manager import mcp_manager  # noqa: E402


# Color codes
class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


async def check_server(server_name: str, timeout: float = 10.0) -> dict:
    """Check if MCP server is healthy and list tools."""
    result = {
        "server": server_name,
        "status": "unknown",
        "tools": [],
        "tool_count": 0,
        "error": None,
        "response_time": 0,
    }

    import time  # noqa: E402

    start = time.time()

    try:
        # Try to get session
        session = await asyncio.wait_for(mcp_manager.get_session(server_name), timeout=timeout)

        if not session:
            result["status"] = "not_configured"
            result["error"] = "Server not configured"
            return result

        # Try to list tools
        tools = await asyncio.wait_for(session.list_tools(), timeout=timeout)

        if not tools or not tools.tools:
            result["status"] = "no_tools"
            result["tool_count"] = 0
            return result

        result["status"] = "online"
        result["tools"] = [{"name": t.name, "description": t.description} for t in tools.tools]
        result["tool_count"] = len(tools.tools)
        result["response_time"] = round(time.time() - start, 2)

        return result

    except asyncio.TimeoutError:
        result["status"] = "timeout"
        result["error"] = f"Connection timeout (>{timeout}s)"
        result["response_time"] = round(time.time() - start, 2)
        return result
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)[:100]
        result["response_time"] = round(time.time() - start, 2)
        return result


async def main():
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║         🔍 AtlasTrinity MCP Server Health Check          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")

    # Get list of configured servers
    servers = list(mcp_manager.config.get("mcpServers", {}).keys())

    # Filter out comments
    servers = [s for s in servers if not s.startswith("_")]

    print(f"Testing {len(servers)} configured MCP servers...\n")

    results = []
    for server_name in sorted(servers):
        print(f"{Colors.OKBLUE}→ {server_name:20}{Colors.ENDC}", end="", flush=True)
        result = await check_server(server_name)
        results.append(result)

        # Status icon
        if result["status"] == "online":
            print(
                f" {Colors.OKGREEN}✓ ONLINE{Colors.ENDC} ({result['tool_count']} tools, {result['response_time']}s)"
            )
        elif result["status"] == "no_tools":
            print(f" {Colors.WARNING}⚠ NO TOOLS{Colors.ENDC} ({result['response_time']}s)")
        elif result["status"] == "not_configured":
            print(f" {Colors.WARNING}⏭️  NOT CONFIGURED{Colors.ENDC}")
        elif result["status"] == "timeout":
            print(f" {Colors.FAIL}⏱️  TIMEOUT{Colors.ENDC} (>{result['response_time']}s)")
        else:
            print(f" {Colors.FAIL}✗ ERROR{Colors.ENDC}: {result['error']}")

    # Summary
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║                     Summary Report                       ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")

    online = [r for r in results if r["status"] == "online"]
    timeouts = [r for r in results if r["status"] == "timeout"]
    errors = [r for r in results if r["status"] == "error"]
    not_configured = [r for r in results if r["status"] == "not_configured"]
    no_tools = [r for r in results if r["status"] == "no_tools"]

    total_tools = sum(r["tool_count"] for r in online)
    avg_response = sum(r["response_time"] for r in online) / len(online) if online else 0

    print(f"\n{Colors.OKGREEN}Online:{Colors.ENDC} {len(online)}/{len(servers)} servers")
    if online:
        for r in online:
            print(f"  • {r['server']:20} → {r['tool_count']:2} tools ({r['response_time']}s)")

    if not_configured:
        print(f"\n{Colors.WARNING}Not Configured:{Colors.ENDC} {len(not_configured)} servers")
        for r in not_configured:
            print(f"  • {r['server']}")

    if timeouts:
        print(f"\n{Colors.FAIL}Timeouts:{Colors.ENDC} {len(timeouts)} servers")
        for r in timeouts:
            print(f"  • {r['server']}")

    if errors:
        print(f"\n{Colors.FAIL}Errors:{Colors.ENDC} {len(errors)} servers")
        for r in errors:
            print(f"  • {r['server']}: {r['error']}")

    if no_tools:
        print(f"\n{Colors.WARNING}No Tools:{Colors.ENDC} {len(no_tools)} servers")
        for r in no_tools:
            print(f"  • {r['server']}")

    print(f"\n{Colors.BOLD}Statistics:{Colors.ENDC}")
    print(f"  • Total tools available: {total_tools}")
    print(f"  • Average response time: {avg_response:.2f}s")
    print(f"  • Health score: {len(online)}/{len(servers)} ({100 * len(online) // len(servers)}%)")

    print(f"\n{Colors.ENDC}")

    # Cleanup
    await mcp_manager.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
