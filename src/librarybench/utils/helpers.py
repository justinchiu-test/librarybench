"""Utility functions for LibraryBench."""

import re
from typing import Optional


def extract_code(solution: str, model_type: Optional[str] = None) -> str:
    """
    Extract code from model solutions.

    Args:
        solution: String containing the model's solution
        model_type: Optional string indicating the model type ('openai' or 'claude')
                   If None, will try to detect from solution format

    Returns:
        The extracted code
    """
    # Auto-detect model type based on solution patterns if not provided
    if model_type is None:
        # Check for OpenAI's dash pattern (more specific)
        dashed_code_pattern = r"[-]{5,}\n(.*?)[-]{5,}"
        if re.search(dashed_code_pattern, solution, re.DOTALL):
            model_type = "openai"
        else:
            # Default to Claude-style extraction (which is more general)
            model_type = "claude"

    if model_type == "openai":
        # For O3 mini solutions, try to extract code between dashed lines
        dashed_code_pattern = r"[-]{5,}\n(.*?)[-]{5,}"
        match = re.search(dashed_code_pattern, solution, re.DOTALL)
        if match:
            return match.group(1)

        # Try to extract code between ```python and ``` markers
        code_pattern = r"```python\n(.*?)\n```"
        match = re.search(code_pattern, solution, re.DOTALL)
        if match:
            return match.group(1)
    else:  # claude
        # Try to extract code between ```python and ``` markers (Claude's standard format)
        code_pattern = r"```python\n(.*?)\n```"
        match = re.search(code_pattern, solution, re.DOTALL)
        if match:
            return match.group(1)

        # If no python markers found, try with any language marker
        code_pattern = r"```(?:\w+)?\n(.*?)\n```"
        match = re.search(code_pattern, solution, re.DOTALL)
        if match:
            return match.group(1)

    # If no markers found, try to extract the first code-like block (works for both models)
    code_pattern = r"class .*?:|def .*?:"
    match = re.search(code_pattern, solution)
    if match:
        # Get the position of the match
        start_pos = match.start()
        # Extract from this position to the end
        return solution[start_pos:]

    return solution
