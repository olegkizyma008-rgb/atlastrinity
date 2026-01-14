import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.brain.config import ensure_dirs  # noqa: E402
from src.brain.mcp_manager import mcp_manager  # noqa: E402


async def verify_all():
    ensure_dirs()
    print("Starting Comprehensive MCP Audit...")

    server_configs = mcp_manager.config.get("mcpServers", {})
    results = []

    # Check top priority servers first
    priority = ["slack", "sequential-thinking", "macos-use", "filesystem", "terminal"]
    others = [s for s in server_configs if s not in priority]

    all_servers = priority + others

    for server_name in all_servers:
        if server_configs.get(server_name, {}).get("disabled", False):
            print(f"Skipping {server_name} (Disabled)")
            continue

        print("[{server_name}] Checking...", end=" ", flush=True)
        try:
            # We use a wrapper with a total timeout for the entire check
            session = await asyncio.wait_for(mcp_manager.get_session(server_name), timeout=180)
            if session:
                tools = await mcp_manager.list_tools(server_name)
                print(f"✅ ONLINE ({len(tools)} tools)")
                results.append((server_name, "Online", len(tools)))
            else:
                print("❌ OFFLINE")
                results.append((server_name, "Offline", 0))
        except asyncio.TimeoutError:
            print("❌ TIMEOUT")
            results.append((server_name, "Timeout", 0))
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append((server_name, "Error", 0))

    print("\n" + "=" * 40)
    print(f"{'SERVER':<25} | {'STATUS':<10} | {'TOOLS'}")
    print("-" * 40)
    for name, status, tools in results:
        icon = "✅" if status == "Online" else "❌"
        print(f"{icon} {name:<22} | {status:<10} | {tools}")

    await mcp_manager.cleanup()


if __name__ == "__main__":
    asyncio.run(verify_all())
