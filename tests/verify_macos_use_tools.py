import asyncio
import json
import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

async def run_mcp_test():
    print("=== TESTING MACOS-USE SWIFT BINARY TOOLS ===")
    
    # 1. Locate Binary
    project_root = Path(__file__).parent.parent
    config_path = project_root / "src" / "mcp_server" / "config.json"
    
    with open(config_path) as f:
        config = json.load(f)
    
    cmd_template = config["mcpServers"]["macos-use"]["command"]
    binary_path = cmd_template.replace("${PROJECT_ROOT}", str(project_root))
    
    print(f"Binary Path: {binary_path}")
    if not os.path.exists(binary_path):
        print(f"ERROR: Binary not found at {binary_path}")
        return

    # 2. Start Server Process
    process = await asyncio.create_subprocess_exec(
        binary_path,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    print("Server process started.")

    async def read_response():
        line = await process.stdout.readline()
        if not line:
            return None
        return json.loads(line.decode())

    async def send_request(req):
        msg = json.dumps(req) + "\n"
        process.stdin.write(msg.encode())
        await process.stdin.drain()

    # 3. Initialize
    print("\n--- Sending Initialize ---")
    await send_request({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"}
        }
    })
    
    # Read init response
    while True:
        resp = await read_response()
        if not resp: break
        if resp.get("id") == 1:
            print("Initialize Response Received")
            break

    await send_request({
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    })

    # 4. List Tools
    print("\n--- Listing Tools ---")
    await send_request({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    })
    
    tools = []
    while True:
        resp = await read_response()
        if not resp: break
        if resp.get("id") == 2:
            tools = resp["result"]["tools"]
            print(f"Found {len(tools)} tools:")
            for t in tools:
                print(f" - {t['name']}")
            break

    # 5. Test execute_command
    print("\n--- Testing execute_command ---")
    await send_request({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "execute_command",
            "arguments": {"command": "echo 'MCP Test Success'"}
        }
    })
    while True:
        resp = await read_response()
        if not resp: break
        if resp.get("id") == 3:
            content = resp["result"]["content"][0]["text"]
            print(f"Result: {content.strip()}")
            if "MCP Test Success" in content:
                print("✅ execute_command PASSED")
            else:
                print("❌ execute_command FAILED")
            break

    # 6. Test Screenshot
    print("\n--- Testing macos-use_take_screenshot ---")
    await send_request({
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "macos-use_take_screenshot",
            "arguments": {}
        }
    })
    while True:
        resp = await read_response()
        if not resp: break
        if resp.get("id") == 4:
            if "error" in resp: # Should check isError or result error
                print(f"❌ Screenshot FAILED (Expected if headless/no permission): {resp}")
            elif resp.get("result", {}).get("isError"):
                 print(f"❌ Screenshot FAILED (Tool Error): {resp['result']['content'][0]['text']}")
            else:
                content = resp["result"]["content"][0]["text"]
                if len(content) > 100:
                    print(f"✅ Screenshot PASSED (Base64 length: {len(content)})")
                else:
                    print(f"❌ Screenshot FAILED (Content too short): {content}")
            break

    # 7. Test Vision Analysis
    print("\n--- Testing macos-use_analyze_screen ---")
    await send_request({
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "macos-use_analyze_screen",
            "arguments": {}
        }
    })
    while True:
        resp = await read_response()
        if not resp: break
        if resp.get("id") == 5:
            if resp.get("result", {}).get("isError"):
                 print(f"❌ Vision FAILED (Tool Error): {resp['result']['content'][0]['text']}")
            else:
                content = resp["result"]["content"][0]["text"]
                try:
                    data = json.loads(content)
                    print(f"✅ Vision Analysis PASSED (Found {len(data)} elements)")
                except:
                    print(f"❌ Vision FAILED (Invalid JSON): {content}")
            break

    # 8. Test Open App (Finder)
    print("\n--- Testing macos-use_open_application_and_traverse (Finder) ---")
    await send_request({
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "macos-use_open_application_and_traverse",
            "arguments": {"identifier": "Finder"}
        }
    })
    finder_pid = None
    while True:
        resp = await read_response()
        if not resp: break
        if resp.get("id") == 6:
            res_data = json.loads(resp["result"]["content"][0]["text"])
            if "pid" in res_data:
                finder_pid = res_data["pid"]
                print(f"✅ Open App PASSED (PID: {finder_pid})")
            else:
                print(f"❌ Open App FAILED: {res_data}")
            break

    # 9. Test Refresh Traversal
    if finder_pid:
        print(f"\n--- Testing macos-use_refresh_traversal (PID: {finder_pid}) ---")
        await send_request({
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "macos-use_refresh_traversal",
                "arguments": {"pid": finder_pid}
            }
        })
        while True:
            resp = await read_response()
            if not resp: break
            if resp.get("id") == 7:
                 # Should return the tree again
                 res_data = json.loads(resp["result"]["content"][0]["text"])
                 if "pid" in res_data and res_data["pid"] == finder_pid:
                     print("✅ Refresh Traversal PASSED")
                 else:
                     print(f"❌ Refresh Traversal FAILED: {res_data}")
                 break

    print("\nAll tests completed.")
    process.terminate()

if __name__ == "__main__":
    asyncio.run(run_mcp_test())
