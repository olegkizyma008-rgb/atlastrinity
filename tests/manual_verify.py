import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.brain.logger import logger  # noqa: E402
from src.brain.orchestrator import Trinity  # noqa: E402


async def run_verification():
    print("Initializing Trinity...")
    trinity = Trinity()
    await trinity.initialize()

    print("\n\n--- TEST 1: Large Output Truncation ---")
    # This command produces numbers from 1 to 100000, which is > 500KB text.
    # We expect the tool output to be truncated.
    task1 = "Run the command 'seq 100000' and tell me the last number."
    print(f"Running Task: {task1}")
    result1 = await trinity.run(task1)
    print(f"Result 1 Status: {result1.get('status')}")
    print(f"Result 1 Output: {str(result1.get('result'))[:200]}...")  # Print preview

    print("\n\n--- TEST 2: Grisha Strategy Optimization ---")
    # This task requires counting files. Grisha should NOT try to read a massive list.
    task2 = "Count the total number of files in the current directory recursively."
    print(f"Running Task: {task2}")
    result2 = await trinity.run(task2)
    print(f"Result 2 Status: {result2.get('status')}")
    print(f"Result 2 Output: {str(result2.get('result'))[:500]}...")

    await trinity.mcp_manager.cleanup()


if __name__ == "__main__":
    asyncio.run(run_verification())
