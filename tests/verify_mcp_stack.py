import asyncio
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
            print(f"❌ Failed to connect to {name}")
            return False

        tools = await mcp_manager.list_tools(name)
        print(f"✅ Connected. Tool count: {len(tools)}")
        for t in tools[:5]:  # Show first 5
            print(f"   - {t.name}")
        return True
    except Exception as e:
        print(f"❌ Error verifying {name}: {e}")
        return False


async def main():
    logger.setLevel("CRITICAL")  # Reduce noise

    servers_to_test = ["macos-use", "filesystem", "apple-mcp", "chrome-devtools"]

    results = {}

    print("Starting MCP Verification...")

    for server in servers_to_test:
        results[server] = await verify_server(server)

    print("\n\n=== SUMMARY ===")
    all_passed = True
    for server, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{server}: {status}")
        if not passed:
            all_passed = False

    await mcp_manager.cleanup()

    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
