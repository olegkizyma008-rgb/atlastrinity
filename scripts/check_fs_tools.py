import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.brain.mcp_manager import mcp_manager


async def main():
    print("Checking filesystem tools...")
    try:
        session = await mcp_manager.get_session("filesystem")
        if not session:
            print("Failed to get session")
            return

        result = await session.list_tools()
        tools = [t.name for t in result.tools]
        print(f"TOOLS: {tools}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
