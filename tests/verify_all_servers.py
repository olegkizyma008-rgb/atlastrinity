import asyncio
import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parents[1]))

from src.brain.logger import logger  # noqa: E402
from src.brain.mcp_manager import mcp_manager  # noqa: E402


async def verify_server(name: str):
    print(f"\n--- Verifying {name} ---")
    try:
        session = await mcp_manager.get_session(name)
        if not session:
            # Check if it was filtered out due to missing env
            server_config = mcp_manager.config.get("mcpServers", {}).get(name)
            if not server_config:
                print(
                    f"❌ Failed to connect to {name}: Server not found in processed config (check logs for missing env)"
                )
            else:
                print(f"❌ Failed to connect to {name}: get_session returned None")
            return False

        tools = await mcp_manager.list_tools(name)
        print(f"✅ Connected. Tool count: {len(tools)}")
        if tools:
            print(f"   Example tools: {', '.join([t.name for t in tools[:3]])}...")
        return True
    except Exception as e:
        print(f"❌ Error verifying {name}: {e}")
        return False


async def main():
    logger.setLevel("INFO")  # show connection logs for debugging

    # Load config to get all servers
    config_path = Path(__file__).parents[1] / "src" / "mcp_server" / "config.json"
    with open(config_path, "r") as f:
        config = json.load(f)

    servers_to_test = []
    for name, server_config in config.get("mcpServers", {}).items():
        if name.startswith("_") or server_config is None:
            continue
        if server_config.get("disabled", False):
            continue
        servers_to_test.append(name)

    print(f"Found {len(servers_to_test)} enabled servers: {', '.join(servers_to_test)}")
    print(f"Check SLACK_BOT_TOKEN: {'SET' if os.environ.get('SLACK_BOT_TOKEN') else 'MISSING'}")
    print("Starting Comprehensive MCP Verification...")

    results = {}

    for server in servers_to_test:
        results[server] = await verify_server(server)
        await asyncio.sleep(5)  # Give system air between spawns

    print("\n\n=== VERIFICATION SUMMARY ===")
    all_passed = True
    print(f"{'SERVER':<25} | {'STATUS':<10}")
    print("-" * 40)
    for server, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{server:<25} | {status}")
        if not passed:
            all_passed = False

    await mcp_manager.cleanup()

    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
