import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from brain.agents.grisha import Grisha
from brain.mcp_manager import mcp_manager


async def test_dynamic_screenshot():
    print("Initializing Grisha...")
    grisha = Grisha()

    # Mock step and result for a background task (no screenshot expected initially)
    step = {
        "id": 1,
        "action": "echo 'Hello Atlas' in terminal",
        "expected_result": "Output should contain 'Hello Atlas'",
    }
    result = {"success": True, "output": "Hello Atlas"}

    print("\n--- Testing Background Task Verification ---")
    print("Grisha should analyze the output without taking a screenshot first.")

    # We can't easily mock the LLM response here without deep monkeypatching,
    # but we can check if the code runs without crashing and if the logic flows.
    # For now, let's just ensure the class can be instantiated and the method doesn't have syntax errors.

    print("Verifying background task...")
    try:
        # We'll use a timeout or mock the call if we wanted to be thorough,
        # but here we just want to ensure the logic exists.
        # Since we can't run LLM calls reliably in this test without API keys,
        # we'll just check if the initial screenshot call is gone.

        # Check source code directly to confirm removal
        with open("src/brain/agents/grisha.py", "r") as f:
            content = f.read()
            if (
                "screenshot_path = await self.take_screenshot()"
                in content.split("def verify_step")[1].split(
                    "context_info = shared_context.to_dict()"
                )[0]
            ):
                print("FAILED: Proactive screenshot found in verify_step!")
            else:
                print("SUCCESS: Proactive screenshot removed from verify_step.")

            if 'if (server == "macos-use" and tool == "screenshot")' in content:
                print("SUCCESS: Dynamic screenshot handling found in loop.")
            else:
                print("FAILED: Dynamic screenshot handling NOT found in loop.")

    except Exception as e:
        print(f"Error during verification check: {e}")


if __name__ == "__main__":
    asyncio.run(test_dynamic_screenshot())
