"""Data models for solution generation and improvement."""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator


class StdinStdout(BaseModel):
    stdin: str
    stdout: str

class ExecutionOutput(BaseModel):
    """Output of the execution of a generation on a test."""

    run_output: dict[str, Any] = Field(default_factory=dict)
    compile_output: dict[str, Any] | None = None


class EvaluationResult(BaseModel):
    """Result of evaluating a single code snippet against a single test."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    code: str
    test: StdinStdout
    passed: bool = False
    exec_output: ExecutionOutput = Field(default_factory=ExecutionOutput)
    uncaught_exception: str | None = None
    error_type: str | None = None

    @field_validator("uncaught_exception", mode="after")
    def validate_uncaught_exception(cls, field) -> Optional[str]:
        if isinstance(field, Exception):
            field = str(field)
        if field is not None and not isinstance(field, str):
            raise ValueError("uncaught_exception must be a string or None")
        return field


class ProblemEvaluationResult(BaseModel):
    """Results of evaluating all solutions for a single problem."""

    problem_id: int
    model_tests_passed: int = 0
    model_tests_total: int = 0
    human_tests_passed: int = 0
    human_tests_total: int = 0
    detailed_model_results: list[dict[str, Any]] = Field(default_factory=list)
    detailed_human_results: list[dict[str, Any]] = Field(default_factory=list)
    
    # Allow arbitrary fields
    model_config = ConfigDict(extra="allow")


class EvaluationResults(BaseModel):
    """Collection of evaluation results for multiple problems."""

    results: List[ProblemEvaluationResult] = Field(default_factory=list)
    model_total_passed: int = 0
    model_total_tests: int = 0
    human_total_passed: int = 0
    human_total_tests: int = 0
    
    # Allow arbitrary fields
    model_config = ConfigDict(extra="allow")


class Problem(BaseModel):
    problem_id: int
    question: str
    tests: list[StdinStdout]
    source: str
    difficulty: str
    human_solutions: list[str]
    original_code: str | None


class SolutionResult(BaseModel):
    """Result of solution generation or improvement."""

    problem: Problem
    status: str = "success"
    code: str
    pass_ratio: float = 0.0
    tests_passed: int = 0
    tests_total: int = 0
    iterations: int = 1
    history: list[dict[str, Any]] = Field(default_factory=list)
    model_type: str
    model_name: str


class BatchResult(BaseModel):
    """Result of a batch solution operation."""

    status: str = "success"
    generated_files: dict[str, str] = Field(default_factory=dict)
    model_type: str
    model: str
    total_problems: int = 0
    completed: int = 0
    errors: int = 0
    avg_initial_ratio: float = 0.0
    avg_final_ratio: float = 0.0
    avg_improvement: float = 0.0
