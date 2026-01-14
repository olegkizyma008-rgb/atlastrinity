import asyncio
import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.brain.mcp_manager import mcp_manager  # noqa: E402


async def check_all_servers():
    print("--- Probing All Configured MCP Servers ---")

    # Reload config to be sure
    mcp_manager.config = mcp_manager._load_config()
    servers = mcp_manager.config.get("mcpServers", {})

    tasks = []
    server_names = []

    for name, cfg in servers.items():
        if name.startswith("_"):
            continue
        if cfg.get("disabled", False):
            print(f"⚪️ {name}: DISABLED")
            continue

        server_names.append(name)
        tasks.append(mcp_manager.get_session(name))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for name, session in zip(server_names, results):
        if isinstance(session, Exception):
            print(f"❌ {name}: ERROR - {type(session).__name__}: {session}")
        elif session:
            print(f"✅ {name}: CONNECTED")
            # Try a quick list_tools
            try:
                tools = await mcp_manager.list_tools(name)
                print(f"   Tools: {len(tools)} available")
            except Exception as e:
                print(f"   ⚠️ {name}: Tools check failed - {e}")
        else:
            print(f"❌ {name}: FAILED TO CONNECT")

    await mcp_manager.cleanup()


if __name__ == "__main__":
    asyncio.run(check_all_servers())
