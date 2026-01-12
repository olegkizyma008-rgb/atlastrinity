
# MCP Architecture Decisons: Custom vs. Original

## Why Custom Python Servers?

While "original" (official/community) MCP servers exist as NPM or PyPI packages, we use **Custom Python FastMCP via the official `mcp` package** for several practical reasons:

### 1. Reliability & Environment Control
During the setup of this project, several NPM-based servers (like `@modelcontextprotocol/server-playwright` and `@modelcontextprotocol/server-terminal`) encountered **404 errors** or **registry access issues** on this local system. 
By implementing them as local Python scripts:
*   We eliminate external dependency failures.
*   We leverage the existing Python environment (3.11/3.12) already configured for the "Brain" (LangGraph).
*   Everything is managed via `requirements.txt` instead of a fragmented `node_modules` structure.

### 2. Interaction Model (One-Shot vs. Persistent)
The current `MCPManager` uses a **One-Shot** logic:
1.  Launch Server.
2.  Call Tool.
3.  Kill Server.

"Original" servers (especially Playwright) are often designed for persistent sessions. In a one-shot model, a standard Playwright server would close the browser window immediately after opening a page, making it useless for the next step.
Our **Custom Servers** are designed to be "stateless-friendly" or ready for our specific persistent management needs.

### 3. Native Integration
The project's agents (**Tetyana**, **Atlas**, **Grisha**) are Python-based.
*   Using Python for MCP tools allows for **shared logs** and **shared utility functions**.
*   We can use `pyobjc` for deep macOS integration more easily within a Python MCP than via a separate Node process.

---

## Why No "Original AppleScript MCP"?

There is no single "Official" AppleScript MCP. Most community versions are wrappers around the same `osascript` command.

We chose to **embed AppleScript directly into our `computer-use` server**:
*   **Example:** Our `keyboard_paste` tool uses `osascript` to trigger a system Cmd+V.
*   **Benefits:** We get the power of AppleScript (controlling System Events, Finder, Mail) combined with the power of Python (handling image recognition, complex logic).
*   **Flexibility:** Adding a new AppleScript feature takes 5 lines of Python code in `src/mcp/computer_use.py`, rather than installing and configuring an entirely new server.

---

## Summary
"Original" does not always mean "Better". In this architecture, **Custom** means **Stable, Integrated, and Optimized** for the AtlasTrinity loop.
