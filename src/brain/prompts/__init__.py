from .common import DEFAULT_REALM_CATALOG  # re-export default catalog
from .atlas import ATLAS
from .tetyana import TETYANA
from .grisha import GRISHA
from ..config import WORKSPACE_DIR

__all__ = ["DEFAULT_REALM_CATALOG", "ATLAS", "TETYANA", "GRISHA", "AgentPrompts"]


class AgentPrompts:
    """Compatibility wrapper that exposes the same interface while sourcing prompts from modular files"""

    ATLAS = ATLAS
    TETYANA = TETYANA
    GRISHA = GRISHA

    @staticmethod
    def tetyana_reasoning_prompt(
        step: str, context: dict, tools_summary: str = "", feedback: str = ""
    ) -> str:
        feedback_section = f"\n        PREVIOUS REJECTION FEEDBACK (from Grisha):\n        {feedback}\n" if feedback else ""
        
        return f"""Analyze how to execute this atomic step: {step}.

        CONTEXT: {context}
        {feedback_section}
        {tools_summary}

        Your task is to choose the BEST tool and arguments.
        CRITICAL: Follow the 'Schema' provided for each tool EXACTLY. Ensure parameter names and types match.
        If there is feedback from Grisha above, ADAPT your strategy to address his concerns.

        Respond in JSON:
        {{
            "thought": "Internal technical analysis in ENGLISH (Which tool? Which args? Why based on schema?)",
            "proposed_action": {{ "tool": "name", "args": {{...}} }},
            "voice_message": "Ukrainian message for the user describing the action"
        }}
        """

    @staticmethod
    def tetyana_reflexion_prompt(
        step: str, error: str, history: list, tools_summary: str = ""
    ) -> str:
        return f"""Analysis of Failure: {error}.

        Step: {step}
        History of attempts: {history}
        {tools_summary}

        Determine if you can fix this by changing the TOOL or ARGUMENTS for THIS step.
        If the failure is logical or requires changing the goal, set "requires_atlas": true.

        Respond in JSON:
        {{
            "analysis": "Technical cause of failure (English)",
            "fix_attempt": {{ "tool": "name", "args": {{...}} }},
            "requires_atlas": true/false,
            "voice_message": "Ukrainian explanation of why it failed and how you are fixing it"
        }}
        """

    @staticmethod
    def tetyana_execution_prompt(step: str, context_results: list) -> str:
        return f"""Execute this task step: {step}.
    Current context results: {context_results}
    Respond ONLY with JSON:
    {{
        "analysis": "Ukrainian explanation",
        "tool_call": {{ "name": "...", "args": {{...}} }},
        "voice_message": "Ukrainian message for user"
    }}
    """

    @staticmethod
    def grisha_strategy_prompt(
        step_action: str, expected_result: str, context: dict, overall_goal: str = ""
    ) -> str:
        return f"""You are the Verification Strategist.

        OVERALL GOAL: {overall_goal}
        Step: {step_action}
        Expected Result: {expected_result}

        Create a verification strategy:
        1. VISION FIRST: What should I see on the screenshot to confirm success?
        2. TOOL FALLBACK: If the screen is not enough, what MCP tool (ls, grep, etc.) should I use?

        Strategy:
        """

    @staticmethod
    def grisha_verification_prompt(
        strategy_context: str,
        step_id: int,
        step_action: str,
        expected: str,
        actual: str,
        context_info: dict,
        history: list,
        overall_goal: str = "",
    ) -> str:
        return f"""Verify the result of the following step using MCP tools FIRST, screenshots only when necessary.

    OVERALL GOAL: {overall_goal}
    STRATEGIC GUIDANCE (Follow this!):
    {strategy_context}

    Step {step_id}: {step_action}
    Expected Result: {expected}
    Actual Output/Result: {actual}

    Shared Context (for correct paths and global situation): {context_info}

    Verification History (Tool actions taken during this verification): {history}

    PRIORITY ORDER FOR VERIFICATION:
    1. Use MCP tools to verify results (filesystem, terminal, git, etc.)
    2. Check files, directories, command outputs directly
    3. ONLY use screenshots for visual/UI verification when explicitly needed

    Analyze the current situation. If you can verify using MCP tools, do that first.
    Use 'macos-use.screenshot' ONLY when you need to verify visual elements, UI, or when explicitly mentioned in expected result.

    CRITICAL: When rejecting a result (verified: false), you MUST provide:
    1. "description": Detailed technical explanation in English (what went wrong, what was expected vs what happened)
    2. "issues": Array of specific problems found (e.g., ["File not created", "Command failed", "Wrong directory structure"])
    3. "voice_message": Clear Ukrainian message for Atlas and Tetyana explaining the rejection
    4. "confidence": Your confidence level (0.0-1.0)
    5. "remediation_suggestions": Array of actionable fixes (e.g., ["Create missing file", "Run command with correct flags"])"""
