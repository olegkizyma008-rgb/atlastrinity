import os
import subprocess
from typing import Any, Dict, List, Optional

from mcp.server import FastMCP

server = FastMCP("git")


def _run_git(args: List[str], cwd: Optional[str] = None, timeout_s: float = 20.0) -> Dict[str, Any]:
    try:
        p = subprocess.run(
            ["git", *args],
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=float(timeout_s),
            check=False,
            env=os.environ.copy(),
        )
        return {
            "success": p.returncode == 0,
            "returncode": p.returncode,
            "stdout": (p.stdout or "").strip(),
            "stderr": (p.stderr or "").strip(),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _repo_root(cwd: Optional[str] = None) -> Optional[str]:
    res = _run_git(["rev-parse", "--show-toplevel"], cwd=cwd, timeout_s=10.0)
    if not res.get("success"):
        return None
    out = (res.get("stdout") or "").strip()
    return out or None


@server.tool()
def git_repo_root(path: str = ".") -> Dict[str, Any]:
    """
    Find the root directory of the git repository.

    Args:
        path: Path to start searching from (default: current directory)
    """
    root = _repo_root(cwd=path)
    if not root:
        return {"error": "not a git repository"}
    return {"success": True, "root": root}


@server.tool()
def git_status(path: str = ".", porcelain: bool = True, timeout_s: float = 20.0) -> Dict[str, Any]:
    """
    Get the status of the git repository.

    Args:
        path: Path within the repository (default: current directory)
        porcelain: Whether to return machine-readable output (default: True)
        timeout_s: Command timeout in seconds (default: 20.0)
    """
    args = ["status"]
    if porcelain:
        args.append("--porcelain")
    root = _repo_root(cwd=path)
    if not root:
        return {"error": "not a git repository"}
    return _run_git(args, cwd=root, timeout_s=timeout_s)


@server.tool()
def git_diff(path: str = ".", staged: bool = False, timeout_s: float = 20.0) -> Dict[str, Any]:
    """
    Get the diff of the git repository.

    Args:
        path: Path within the repository (default: current directory)
        staged: Whether to show staged changes (default: False)
        timeout_s: Command timeout in seconds (default: 20.0)
    """
    args = ["diff"]
    if staged:
        args.append("--staged")
    root = _repo_root(cwd=path)
    if not root:
        return {"error": "not a git repository"}
    return _run_git(args, cwd=root, timeout_s=timeout_s)


@server.tool()
def git_log(path: str = ".", limit: int = 20, timeout_s: float = 20.0) -> Dict[str, Any]:
    """
    Get the commit log of the git repository.

    Args:
        path: Path within the repository (default: current directory)
        limit: Maximum number of commits to return (default: 20)
        timeout_s: Command timeout in seconds (default: 20.0)
    """
    lim = max(1, min(int(limit), 200))
    args = ["log", f"-{lim}", "--pretty=format:%H %s"]
    root = _repo_root(cwd=path)
    if not root:
        return {"error": "not a git repository"}
    return _run_git(args, cwd=root, timeout_s=timeout_s)


@server.tool()
def git_show(
    path: str = ".",
    rev: str = "HEAD",
    file_path: Optional[str] = None,
    timeout_s: float = 20.0,
) -> Dict[str, Any]:
    """
    Show the contents of a specific revision or file at a revision.

    Args:
        path: Path within the repository (default: current directory)
        rev: Revision to show (default: HEAD)
        file_path: Optional specific file path to show content of
        timeout_s: Command timeout in seconds (default: 20.0)
    """
    args = ["show", rev]
    if file_path:
        args[-1] = f"{rev}:{file_path}"
    root = _repo_root(cwd=path)
    if not root:
        return {"error": "not a git repository"}
    return _run_git(args, cwd=root, timeout_s=timeout_s)


@server.tool()
def git_branch_list(path: str = ".", timeout_s: float = 20.0) -> Dict[str, Any]:
    """
    List all branches in the repository.

    Args:
        path: Path within the repository (default: current directory)
        timeout_s: Command timeout in seconds (default: 20.0)
    """
    args = ["branch", "--format=%(refname:short)"]
    root = _repo_root(cwd=path)
    if not root:
        return {"error": "not a git repository"}
    return _run_git(args, cwd=root, timeout_s=timeout_s)


@server.tool()
def git_current_branch(path: str = ".", timeout_s: float = 20.0) -> Dict[str, Any]:
    """
    Get the current branch name.

    Args:
        path: Path within the repository (default: current directory)
        timeout_s: Command timeout in seconds (default: 20.0)
    """
    args = ["rev-parse", "--abbrev-re", "HEAD"]
    root = _repo_root(cwd=path)
    if not root:
        return {"error": "not a git repository"}
    return _run_git(args, cwd=root, timeout_s=timeout_s)


if __name__ == "__main__":
    server.run()
