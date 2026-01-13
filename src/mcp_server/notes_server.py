"""
Notes MCP Server - Simple text-based note taking and reporting system.
Complements the memory server for structured text storage and retrieval.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from mcp.server import FastMCP

server = FastMCP("notes")


def _notes_dir() -> Path:
    """Get or create notes directory"""
    notes_path = Path.home() / ".config" / "atlastrinity" / "notes"
    notes_path.mkdir(parents=True, exist_ok=True)
    return notes_path


def _index_path() -> Path:
    """Path to notes index"""
    return _notes_dir() / "index.json"


def _load_index() -> Dict[str, Any]:
    """Load notes index"""
    if not _index_path().exists():
        return {"notes": []}
    try:
        return json.loads(_index_path().read_text(encoding="utf-8"))
    except Exception:
        return {"notes": []}


def _save_index(index: Dict[str, Any]) -> None:
    """Save notes index"""
    _index_path().write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
    )


@server.tool()
def create_note(
    title: str, content: str, category: str = "general", tags: List[str] = None
) -> Dict[str, Any]:
    """
    Create a new note with title and content.

    Args:
        title: Note title
        content: Note content (can be multiline text)
        category: Category (e.g., "verification_report", "error_log", "analysis")
        tags: Optional list of tags

    Returns:
        Dict with note_id and confirmation
    """
    if tags is None:
        tags = []

    timestamp = datetime.now().isoformat()
    note_id = f"{category}_{timestamp.replace(':', '-').replace('.', '-')}"

    # Save note file
    note_file = _notes_dir() / f"{note_id}.md"
    note_content = f"""# {title}

**Category:** {category}
**Tags:** {', '.join(tags) if tags else 'None'}
**Created:** {timestamp}

---

{content}
"""
    note_file.write_text(note_content, encoding="utf-8")

    # Update index
    index = _load_index()
    index["notes"].append(
        {
            "id": note_id,
            "title": title,
            "category": category,
            "tags": tags,
            "timestamp": timestamp,
            "file": str(note_file),
        }
    )
    _save_index(index)

    return {
        "success": True,
        "note_id": note_id,
        "file": str(note_file),
        "message": f"Note created: {title}",
    }


@server.tool()
def search_notes(
    query: str = None, category: str = None, tags: List[str] = None, limit: int = 10
) -> Dict[str, Any]:
    """
    Search notes by query, category, or tags.

    Args:
        query: Text to search in title and content
        category: Filter by category
        tags: Filter by tags (matches any)
        limit: Maximum number of results

    Returns:
        Dict with matching notes
    """
    index = _load_index()
    notes = index.get("notes", [])

    results = []
    for note in notes:
        # Category filter
        if category and note.get("category") != category:
            continue

        # Tag filter
        if tags:
            note_tags = note.get("tags", [])
            if not any(tag in note_tags for tag in tags):
                continue

        # Text search
        if query:
            note_file = Path(note["file"])
            if note_file.exists():
                content = note_file.read_text(encoding="utf-8")
                if (
                    query.lower() not in content.lower()
                    and query.lower() not in note.get("title", "").lower()
                ):
                    continue

        results.append(note)

        if len(results) >= limit:
            break

    return {"success": True, "count": len(results), "notes": results}


@server.tool()
def read_note(note_id: str) -> Dict[str, Any]:
    """
    Read full content of a note by ID.

    Args:
        note_id: Note identifier

    Returns:
        Dict with note content
    """
    index = _load_index()

    for note in index.get("notes", []):
        if note["id"] == note_id:
            note_file = Path(note["file"])
            if note_file.exists():
                content = note_file.read_text(encoding="utf-8")
                return {
                    "success": True,
                    "note_id": note_id,
                    "title": note["title"],
                    "category": note["category"],
                    "content": content,
                }

    return {"success": False, "error": f"Note not found: {note_id}"}


@server.tool()
def delete_note(note_id: str) -> Dict[str, Any]:
    """
    Delete a note by ID.

    Args:
        note_id: Note identifier

    Returns:
        Dict with confirmation
    """
    index = _load_index()
    notes = index.get("notes", [])

    for i, note in enumerate(notes):
        if note["id"] == note_id:
            # Delete file
            note_file = Path(note["file"])
            if note_file.exists():
                note_file.unlink()

            # Remove from index
            notes.pop(i)
            index["notes"] = notes
            _save_index(index)

            return {"success": True, "message": f"Note deleted: {note_id}"}

    return {"success": False, "error": f"Note not found: {note_id}"}


@server.tool()
def list_categories() -> Dict[str, Any]:
    """
    List all note categories with counts.

    Returns:
        Dict with categories and counts
    """
    index = _load_index()
    notes = index.get("notes", [])

    categories = {}
    for note in notes:
        cat = note.get("category", "general")
        categories[cat] = categories.get(cat, 0) + 1

    return {"success": True, "categories": categories, "total_notes": len(notes)}


if __name__ == "__main__":
    server.run()
