"""Abstract base class for LLM clients."""

import abc


class LlmClient(abc.ABC):
    """Abstract base class for LLM clients."""

    type = "OVERWRITE"

    @abc.abstractmethod
    async def generate_completion(self, prompt: str, system_prompt: str) -> str:
        """Generate a completion for the given prompt."""
        pass

    @abc.abstractmethod
    def extract_code(self, solution: str) -> str:
        """Extract code from the model's solution text."""
        pass

    @property
    @abc.abstractmethod
    def model_name(self) -> str:
        """Return the name of the model being used."""
        pass
