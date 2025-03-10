"""LibraryBench: A framework for evaluating and improving AI model solutions to coding problems."""

# Export legacy modules
from . import execution
from . import feedback
from . import analysis
from . import utils

# Export the main API
from librarybench.processor import solution_process
from librarybench.models import LlmClient, ClaudeClient, OpenAiClient

# Import explicitly with the file's full path to avoid package confusion
import importlib.util
import sys
import os

# Load the models.py file directly
spec = importlib.util.spec_from_file_location(
    "models_file", 
    os.path.join(os.path.dirname(__file__), "models.py")
)
models_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(models_module)

# Get the classes
SolutionResult = models_module.SolutionResult
BatchResult = models_module.BatchResult

__version__ = "0.1.0"

__all__ = [
    # Legacy modules
    "execution",
    "feedback",
    "analysis",
    "utils",
    # Main API
    "SolutionResult",
    "BatchResult",
    "solution_process",
    "LlmClient",
    "ClaudeClient",
    "OpenAiClient",
]
