"""Client for Anthropic Claude models."""

import os
import re

from librarybench.models.llm_client import LlmClient


class ClaudeClient(LlmClient):
    """Client for Anthropic Claude models."""
    type = "claude"

    def __init__(self, model: str = "claude-3-7-sonnet-20250219"):
        try:
            from anthropic import AsyncAnthropic
        except ImportError:
            raise ImportError(
                "Please install the anthropic package: pip install anthropic"
            )

        # Load API key from environment variable
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Please set the ANTHROPIC_API_KEY environment variable")

        # Create Anthropic client
        self.client = AsyncAnthropic(api_key=api_key)
        self._model = model

    async def generate_completion(self, prompt: str, system_prompt: str) -> str:
        """Generate a completion using Anthropic API."""
        response = await self.client.messages.create(
            model=self._model,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096,
        )
        if not response.content or len(response.content) == 0:
            return ""
        # Access the text content safely
        try:
            # Check if content is a list of content blocks (new API)
            if isinstance(response.content, list):
                text_blocks = []
                for block in response.content:
                    # TODO: thinking blocks might have a different field?
                    if hasattr(block, "text"):
                        text_blocks.append(block.text) # type: ignore
                return "".join(text_blocks)
            # Legacy API access
            return response.content
        except (AttributeError, IndexError):
            return ""

    def extract_code(self, solution: str) -> str:
        """Extract code from Claude solution using markdown code blocks."""
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

        # If no markers found, try to extract the first code-like block
        code_pattern = r"class .*?:|def .*?:"
        match = re.search(code_pattern, solution)
        if match:
            # Get the position of the match
            start_pos = match.start()
            # Extract from this position to the end
            return solution[start_pos:]

        return solution

    @property
    def model_name(self) -> str:
        """Return the model name for result naming."""
        return self._model.replace("-", "_").replace(".", "_")
