"""Improvement module for iterative solution repair in LibraryBench."""

from .iterative_repair import (
    improve_solution,
    batch_improve_solutions,
    query_model,
)

__all__ = [
    "improve_solution",
    "batch_improve_solutions",
    "query_model",
]
