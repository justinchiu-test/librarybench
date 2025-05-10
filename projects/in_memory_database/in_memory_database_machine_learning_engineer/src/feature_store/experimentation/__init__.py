"""
Experimentation framework with A/B testing support.

This module provides tools for A/B testing with randomized but consistent record
selection. It enables controlled experiments with feature variations through
deterministic assignment of entities to experimental groups.
"""

from feature_store.experimentation.experiment import Experiment
from feature_store.experimentation.assignment import AssignmentStrategy
from feature_store.experimentation.consistent_hash import ConsistentHash

__all__ = ["Experiment", "AssignmentStrategy", "ConsistentHash"]