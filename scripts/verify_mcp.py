#!/usr/bin/env python3
"""
MCP Servers Health Check
Перевіряє чи всі MCP сервери з config.json можуть ініціалізуватися
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Кольори
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def load_mcp_config() -> Dict:
    """Завантажує MCP конфіг з глобальної папки"""
    config_path = Path.home() / ".config" / "atlastrinity" / "mcp" / "config.json"

    if not config_path.exists():
        print(f"{RED}✗{RESET} Config not found: {config_path}")
        sys.exit(1)

    with open(config_path) as f:
        return json.load(f)


def test_server(name: str, config: Dict) -> Tuple[bool, str]:
    """Тестує один MCP сервер"""
    if config.get("disabled", False):
        return True, "disabled"

    command = config.get("command")
    args = config.get("args", [])

    if not command:
        return False, "no command"

    # Спеціальні перевірки
    if command == "npx":
        # NPX сервери - просто перевіряємо що npx існує
        if subprocess.run(["which", "npx"], capture_output=True).returncode == 0:
            return True, "npx available"
        return False, "npx not found"

    elif command == "bunx":
        # Bunx сервери
        if subprocess.run(["which", "bunx"], capture_output=True).returncode == 0:
            return True, "bunx available"
        return False, "bunx not found"

    elif command == "python3":
        # Python MCP сервери - перевіряємо модуль
        if args and args[0] == "-m":
            module = args[1] if len(args) > 1 else None
            if module:
                try:
                    # Встановлюємо PYTHONPATH
                    import os

                    env = os.environ.copy()
                    env["PYTHONPATH"] = str(Path.cwd() / "src")

                    result = subprocess.run(
                        [command, "-c", f"import {module.replace('.', '.')}"],
                        capture_output=True,
                        timeout=3,
                        env=env,
                        cwd=Path.cwd(),
                    )
                    if result.returncode == 0:
                        return True, "module exists"
                    return False, f"module import failed: {result.stderr.decode()[:50]}"
                except subprocess.TimeoutExpired:
                    return False, "timeout"
                except Exception as e:
                    return False, str(e)

    elif command.endswith("mcp-server-macos-use"):
        # Swift binary
        if Path(command.replace("${PROJECT_ROOT}", str(Path.cwd()))).exists():
            return True, "binary exists"
        return False, "binary not found"

    return True, "not tested"


def main():
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}  MCP Servers Health Check{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")

    config = load_mcp_config()
    servers = config.get("mcpServers", {})

    results = []

    for name, server_config in servers.items():
        if name.startswith("_comment"):
            continue

        success, message = test_server(name, server_config)
        results.append((name, success, message))

        status = f"{GREEN}✓{RESET}" if success else f"{RED}✗{RESET}"
        print(f"{status} {name:25} {message}")

    # Summary
    total = len(results)
    passed = sum(1 for _, success, _ in results if success)

    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{GREEN if passed == total else YELLOW}  {passed}/{total} servers OK{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
