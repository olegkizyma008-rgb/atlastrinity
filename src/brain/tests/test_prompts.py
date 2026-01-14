import pytest
from brain.prompts import AgentPrompts


def test_agent_prompts_exports():
    assert hasattr(AgentPrompts, "ATLAS")
    assert hasattr(AgentPrompts, "TETYANA")
    assert hasattr(AgentPrompts, "GRISHA")


def test_grisha_prompt_contains_swift_preference():
    grisha = AgentPrompts.GRISHA
    assert isinstance(grisha, dict)
    sys_prompt = grisha.get("SYSTEM_PROMPT", "")
    assert "SWIFT LOCAL MCP PREFERENCE" in sys_prompt or "DYNAMIC: Choose between Vision and MCP tools" in sys_prompt
