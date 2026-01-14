#!/usr/bin/env python3
import asyncio
import os
import sys

sys.path.insert(0, "src")
from brain.agents.grisha import Grisha  # noqa: E402
from brain.mcp_manager import mcp_manager  # noqa: E402


async def run():
    nav = await mcp_manager.call_tool(
        "puppeteer", "puppeteer_navigate", {"url": "https://accounts.google.com/signup"}
    )
    print("Navigate content:", [(getattr(c, "text", None) or "")[:80] for c in nav.content])
    shot = await mcp_manager.call_tool(
        "puppeteer", "puppeteer_screenshot", {"name": "google_signup", "encoded": True}
    )
    print("Screenshot content types:", [getattr(c, "type", None) for c in shot.content])
    screen_path = None
    for c in shot.content:
        if getattr(c, "type", "") == "image":
            import base64  # noqa: E402

            b = base64.b64decode(c.data)
            tf = os.path.join("/tmp", "grisha_google_signup.png")
            with open(tf, "wb") as f:
                f.write(b)
            screen_path = tf
            print("Saved screenshot to", tf)
            break

    step = {
        "id": 1,
        "action": "Launch a browser and navigate to https://accounts.google.com/signup.",
        "expected_result": "Browser window opens at the Google account signup page. (visual)",
    }
    result = {"success": True, "output": "Navigated to accounts.google.com/signup"}

    gr = Grisha()
    verification = await gr.verify_step(step, result, screenshot_path=screen_path)
    # Save verification result to file to avoid noisy logs
    out = {
        "verified": bool(verification.verified),
        "confidence": float(verification.confidence),
        "description": verification.description,
    }
    with open("/tmp/grisha_verification_result.json", "w") as f:
        import json  # noqa: E402

        json.dump(out, f)

    await mcp_manager.cleanup()


if __name__ == "__main__":
    asyncio.run(run())
