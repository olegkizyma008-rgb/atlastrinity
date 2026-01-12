"""
MCP Config Loader
Loads MCP server configurations from config.yaml
"""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml


def load_mcp_config() -> Dict[str, Any]:
    """Load MCP configuration from config.yaml"""
    config_path = Path.home() / ".config" / "atlastrinity" / "config.yaml"

    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
            return config.get("mcp", {})
        except Exception as e:
            print(f"⚠️  Error loading {config_path}: {e}")

    return {}


def get_server_config(server_name: str) -> Dict[str, Any]:
    """Get configuration for a specific MCP server"""
    mcp_config = load_mcp_config()
    return mcp_config.get(server_name, {})


def get_config_value(server_name: str, key: str, default: Any = None) -> Any:
    """Get a specific config value for a server"""
    config = get_server_config(server_name)
    return config.get(key, default)
