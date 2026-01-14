"""
Common constants and shared fragments for prompts
"""

DEFAULT_REALM_CATALOG = """
AVAILABLE REALMS (MCP Servers):
- terminal: Shell access. Tool: execute_command.
- filesystem: File operations. Tools: read_file, write_file, list_directory.
- macos-use: UI automation and screenshots.
- puppeteer: Browser automation (navigate, click, type, screenshot).
- fetch: URL content extraction. Tool: fetch_url.
- duckduckgo-search: Web search. Tool: search.
- vibe: Self-healing and advanced debugging.
- notes: Storing/Reading feedback and reports. Tools: create_note, read_note.
- memory: Knowledge graph access.

CRITICAL: Do NOT invent high-level tools (e.g., 'scrape_and_extract'). Use only the real TOOLS found inside these Realms after Inspection.
"""
