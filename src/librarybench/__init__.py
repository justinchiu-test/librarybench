"""LibraryBench: A framework for evaluating and improving AI model solutions to coding problems."""

# Export legacy modules
from . import execution
from . import feedback
from . import analysis
from . import utils

# Export the unified API
from librarybench.unified_models import SolutionResult, BatchResult
from librarybench.unified_processor import unified_solution_process
from librarybench.models import LlmClient, ClaudeClient, OpenAiClient

__version__ = "0.1.0"

__all__ = [
    # Legacy modules
    "execution",
    "feedback",
    "analysis",
    "utils",
    
    # Unified API
    "SolutionResult",
    "BatchResult",
    "unified_solution_process",
    "LlmClient",
    "ClaudeClient",
    "OpenAiClient",
]
