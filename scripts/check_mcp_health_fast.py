
import asyncio
import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.brain.mcp_manager import mcp_manager

async def check_server(name):
    try:
        # 10 second timeout for EACH server connection
        session = await asyncio.wait_for(mcp_manager.get_session(name), timeout=15.0)
        if session:
            tools = await asyncio.wait_for(mcp_manager.list_tools(name), timeout=5.0)
            return f"✅ {name}: CONNECTED ({len(tools)} tools)"
        else:
            return f"❌ {name}: FAILED TO CONNECT (Empty session)"
    except asyncio.TimeoutError:
        return f"⏰ {name}: TIMEOUT"
    except Exception as e:
        return f"❌ {name}: ERROR - {str(e)[:100]}"

async def check_all_servers_fast():
    print("--- Rapid MCP Server Health Check ---")
    
    mcp_manager.config = mcp_manager._load_config()
    servers = mcp_manager.config.get("mcpServers", {})
    
    server_names = [n for n in servers if not n.startswith("_") and not servers[n].get("disabled", False)]
    
    # Run checks in parallel with a total cap
    results = await asyncio.gather(*[check_server(name) for name in server_names])
    
    for res in sorted(results):
        print(res)

    await mcp_manager.cleanup()

if __name__ == "__main__":
    asyncio.run(check_all_servers_fast())
