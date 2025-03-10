"""Data models for solution generation and improvement."""

from typing import Dict, List, Any
from pydantic import BaseModel, Field


class SolutionResult(BaseModel):
    """Result of solution generation or improvement."""

    problem_id: int
    status: str = "success"
    code: str
    pass_ratio: float = 0.0
    tests_passed: int = 0
    tests_total: int = 0
    iterations: int = 1
    history: List[Dict[str, Any]] = Field(default_factory=list)


class BatchResult(BaseModel):
    """Result of a batch solution operation."""

    status: str = "success"
    generated_files: Dict[str, str] = Field(default_factory=dict)
    model_key: str
    total_problems: int = 0
    completed: int = 0
    errors: int = 0
    avg_initial_ratio: float = 0.0
    avg_final_ratio: float = 0.0
    avg_improvement: float = 0.0
