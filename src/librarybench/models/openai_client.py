"""Client for OpenAI models."""

import os
import re
import openai

from librarybench.models.llm_client import LlmClient


class OpenAiClient(LlmClient):
    """Client for OpenAI models."""
    type = "openai"

    def __init__(self, model: str = "o3-mini"):
        # Load API key from environment variable
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Please set the OPENAI_API_KEY environment variable")

        # Create OpenAI client
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self._model = model

    async def generate_completion(self, prompt: str, system_prompt: str) -> str:
        """Generate a completion using OpenAI API."""
        response = await self.client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        if len(response.choices) == 0:
            return "Error: len(response.choices) == 0"
        content = response.choices[0].message.content
        return content if content is not None else ""

    def extract_code(self, solution: str) -> str:
        """Extract code from OpenAI solution using dash pattern."""
        # Try to extract code between ```python and ``` markers
        code_pattern = r"```python\n(.*?)\n```"
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
        return self._model.replace("-", "_")
