import asyncio
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.brain.config_loader import config
from src.brain.mcp_manager import mcp_manager


async def check_mcp():
    print("--- MCP Diagnostic ---")
    servers = mcp_manager.config.get("mcpServers", {})

    for server_name in servers:
        if server_name.startswith("_") or servers[server_name].get("disabled"):
            print( "[SKIP] {server_name}")
            continue

        print(f"Connecting to {server_name}...")
        try:
            session = await mcp_manager.get_session(server_name)
            if session:
                result = await session.list_tools()
                tools = result.tools
                if tools:
                    print( "[OK] {server_name}: Found {len(tools)} tools")
                else:
                    print( "[FAIL] {server_name}: No tools found")
            else:
                print( "[FAIL] {server_name}: Could not establish session")
        except Exception as e:
            print( "[ERROR] {server_name}: {e}")


if __name__ == "__main__":
    asyncio.run(check_mcp())
