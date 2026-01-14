import asyncio

# Setup paths (for standalone run if needed)
import os
import sys
from typing import Any, Dict

from mcp.server import FastMCP

current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(current_dir, "..", "..")
sys.path.insert(0, os.path.abspath(root))

from src.brain.db.manager import db_manager  # noqa: E402
from src.brain.knowledge_graph import knowledge_graph  # noqa: E402

server = FastMCP("graph")


@server.tool()
async def get_graph_json() -> Dict[str, Any]:
    """
    Returns the entire Knowledge Graph in JSON format (nodes and edges).
    Useful for D3.js or Cytoscape.js visualizations.
    """
    await db_manager.initialize()
    return await knowledge_graph.get_graph_data()


@server.tool()
async def generate_mermaid() -> str:
    """
    Generates a Mermaid.js flowchart representation of the current Knowledge Graph.
    """
    await db_manager.initialize()
    data = await knowledge_graph.get_graph_data()

    if "error" in data:
        return f"Error: {data['error']}"

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    if not nodes:
        return "graph TD\n  Empty[Graph is empty]"

    mermaid = "graph TD\n"

    # 1. Add Nodes with types as styles
    # Clean IDs for Mermaid (no special chars, use aliases)
    node_map = {}
    for i, n in enumerate(nodes):
        alias = f"N{i}"
        node_map[n["id"]] = alias
        label = n["id"].split("/")[-1] or n["id"]
        # Limit label length
        if len(label) > 30:
            label = label[:27] + "..."

        type_icon = {
            "FILE": "📄",
            "TASK": "🎯",
            "TOOL": "🛠️",
            "USER": "👤",
            "CONCEPT": "💡",
        }.get(n["type"], "⚪")

        mermaid += f'  {alias}["{type_icon} {label}"]\n'

    # 2. Add Edges
    for e in edges:
        source_id = e.get("source")
        target_id = e.get("target")
        relation = e.get("relation", "rel")

        if source_id in node_map and target_id in node_map:
            mermaid += f'  {node_map[source_id]} -- "{relation}" --> {node_map[target_id]}\n'

    return mermaid


if __name__ == "__main__":
    server.run()
