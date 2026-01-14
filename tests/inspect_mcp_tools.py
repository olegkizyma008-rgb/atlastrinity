import asyncio
import os
import sys

sys.path.append(os.path.abspath(os.getcwd()))
from src.brain.mcp_manager import mcp_manager  # noqa: E402


async def inspect():
    server = "sequential-thinking"
    print(f"--- Inspecting {server} ---")
    try:
        session = await mcp_manager.get_session(server)
        if not session:
            print("Failed to connect.")
            return

        tools = await mcp_manager.list_tools(server)
        for t in tools:
            print(f"Tool: {t.name}")
            print(f"Schema: {t.inputSchema}")

    except Exception as e:
        print(f"Error: {e}")

    await mcp_manager.cleanup()


if __name__ == "__main__":
    asyncio.run(inspect())
