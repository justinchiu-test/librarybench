"""Pytest configuration file."""

import os
import tempfile
from pathlib import Path

import pytest


def pytest_addoption(parser):
    """Add custom command line options to pytest."""
    parser.addoption(
        "--run-performance",
        action="store_true",
        default=False,
        help="Run performance tests which are skipped by default",
    )


def pytest_configure(config):
    """Configure pytest environment."""
    # Register custom markers
    config.addinivalue_line("markers", "performance: mark test as a performance test")
    
    # Set environment variable if --run-performance is used
    if config.getoption("--run-performance"):
        os.environ["RUN_LARGE_PERFORMANCE_TESTS"] = "1"


def pytest_collection_modifyitems(config, items):
    """Modify collected tests based on options."""
    if not config.getoption("--run-performance"):
        # Skip performance tests unless explicitly enabled
        skip_performance = pytest.mark.skip(reason="Need --run-performance option to run")
        for item in items:
            if "performance" in item.keywords or "test_performance.py" in item.nodeid:
                item.add_marker(skip_performance)