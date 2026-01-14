#!/usr/bin/env python3
import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


async def verify_active_servers():
    print(f"\n{BOLD}{BLUE}=== MCP Active Servers Verification ==={RESET}\n")

    # Import mcp_manager after project root is added
    try:
        from src.brain.mcp_manager import mcp_manager  # noqa: E402
    except ImportError as e:
        print(f"{RED}Error: Could not import mcp_manager. {e}{RESET}")
        return

    mcp_config = mcp_manager.config.get("mcpServers", {})
    active_servers = [
        name
        for name, cfg in mcp_config.items()
        if not name.startswith("_") and not cfg.get("disabled", False)
    ]

    if not active_servers:
        print(f"{YELLOW}No active servers found in configuration.{RESET}")
        return

    print(f"Found {len(active_servers)} active servers: {', '.join(active_servers)}")
    print("-" * 50)

    for server_name in active_servers:
        print(f"\n{BOLD}[{server_name}]{RESET} Initializing...", end=" ", flush=True)

        try:
            # 60 second timeout per server for connection + tool listing
            session = await asyncio.wait_for(mcp_manager.get_session(server_name), timeout=60)

            if session:
                print(f"{GREEN}CONNECTED{RESET}")

                tools = await mcp_manager.list_tools(server_name)
                print(f"{BOLD}Available Tools ({len(tools)}):{RESET}")

                for tool in tools:
                    name = getattr(tool, "name", "N/A")
                    description = getattr(tool, "description", "No description available")
                    print(f"  • {BOLD}{name}{RESET}: {description}")
            else:
                print(f"{RED}FAILED (No session returned){RESET}")

        except asyncio.TimeoutError:
            print(f"{RED}TIMEOUT (>60s){RESET}")
        except Exception as e:
            print(f"{RED}ERROR: {type(e).__name__}: {e}{RESET}")

    # Cleanup
    print(f"\n{BLUE}Cleaning up connections...{RESET}")
    await mcp_manager.cleanup()
    print(f"{GREEN}Done.{RESET}\n")


if __name__ == "__main__":
    asyncio.run(verify_active_servers())
