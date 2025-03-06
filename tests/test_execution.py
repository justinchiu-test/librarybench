"""Tests for the execution module."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import asyncio

from librarybench.execution import execute_test, run_unit_tests_async


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.post")
async def test_execute_test(mock_post):
    """Test executing a test against the execution API."""
    # Mock the response
    mock_response = AsyncMock()
    mock_response.json.return_value = {"passed": True}
    mock_post.return_value.__aenter__.return_value = mock_response

    # Create test data
    session = MagicMock()
    code = "def add(a, b): return a + b"
    test = {"stdin": "1 2", "stdout": "3"}
    semaphore = asyncio.Semaphore(1)

    # Execute the test
    result = await execute_test(session, code, test, semaphore)

    # Check the result
    assert result["passed"] is True
    mock_post.assert_called_once()


@pytest.mark.asyncio
@patch("librarybench.execution.execute_test")
async def test_run_unit_tests_async(mock_execute_test):
    """Test running multiple unit tests asynchronously."""
    # Mock the execute_test function to return test results
    mock_execute_test.side_effect = [
        {"passed": True},
        {"passed": False, "exec_output": {"run_output": {"stderr": "Error"}}},
    ]

    # Create test data
    generations = ["def add(a, b): return a + b"]
    tests = [{"stdin": "1 2", "stdout": "3"}, {"stdin": "3 4", "stdout": "7"}]

    # Run the tests
    results = await run_unit_tests_async(generations, tests)

    # Check the results
    assert len(results) == 1  # One generation
    assert len(results[0]) == 2  # Two tests
    assert results[0][0]["passed"] is True
    assert results[0][1]["passed"] is False
    assert mock_execute_test.call_count == 2
