"""Tests for the execution module."""

import os
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import asyncio
import requests
import json
import aiohttp

from librarybench.execution import execute_test, run_unit_tests_async, run_unit_tests, CYBER_URL


def run_unit_tests_sync(
    generations: list[str], tests: list[str]
) -> list[list[dict[str, str]]]:
    """Synchronous implementation of test execution.
    
    Args:
        generations: List of code generations to test
        tests: List of assertion-based tests
        
    Returns:
        List of test results for each generation
    """
    num_tests_per_generation = []
    outputs = []
    
    # Get API URL from environment variable
    url = os.getenv("CYBER_URL")
    if not url:
        raise ValueError("CYBER_URL environment variable is not set")
    
    for generation in generations:
        num_tests_per_generation.append(len(tests))
        for test in tests:
            code_dict = {
                "code": generation,
                "test": test,
            }
            params = {
                "language": "python",
                "environment": "default",
                "timeout": 30,
                "generation_formatting": "true",
                "fill_missing_imports": "true",
            }
            response = requests.post(url, json=code_dict, params=params)
            outputs.append(response.json())
            
    # Unflatten the results
    idx = 0
    generation_tests = []
    for num_tests in num_tests_per_generation:
        generation_tests.append([outputs[idx + i] for i in range(num_tests)])
        idx += num_tests
    return generation_tests


def test_run_unit_tests_sync():
    """Test synchronous implementation of test execution using real API calls.
    
    Note: This test requires the CYBER_URL environment variable to be set.
    It will make actual API calls to the execution service.
    """
    # Check if CYBER_URL is set
    url = os.getenv("CYBER_URL")
    if not url:
        pytest.skip("CYBER_URL environment variable is not set")
    
    # Test data
    generations = ["def f(): return 1", "def f(): return 2"]
    tests = ["assert f() == 1", "assert f() == 2"]
    
    # Run the tests
    results = run_unit_tests_sync(generations, tests)
    
    # Verify results structure
    assert len(results) == 2, "Should have results for 2 generations"
    assert len(results[0]) == 2, "Each generation should have 2 test results"
    assert len(results[1]) == 2, "Each generation should have 2 test results"
    
    # Verify results match expected behavior
    # First generation returns 1, should pass test 1 and fail test 2
    assert results[0][0].get("passed", False) is True, "def f(): return 1 should pass 'assert f() == 1'"
    assert results[0][1].get("passed", False) is False, "def f(): return 1 should fail 'assert f() == 2'"
    
    # Second generation returns 2, should fail test 1 and pass test 2
    assert results[1][0].get("passed", False) is False, "def f(): return 2 should fail 'assert f() == 1'"
    assert results[1][1].get("passed", False) is True, "def f(): return 2 should pass 'assert f() == 2'"
    

@pytest.mark.asyncio
async def test_sync_and_async_correctness():
    """Test that both sync and async implementations work correctly with string test format."""
    # Check if CYBER_URL is set
    url = os.getenv("CYBER_URL")
    if not url:
        pytest.skip("CYBER_URL environment variable is not set")
    
    # Test cases with expected outcomes
    test_cases = [
        {
            "generation": "def f(): return 1", 
            "test": "assert f() == 1",
            "expected": True  # Expected to pass
        },
        {
            "generation": "def f(): return 1", 
            "test": "assert f() == 2",
            "expected": False  # Expected to fail
        }
    ]
    
    for case in test_cases:
        generation = case["generation"]
        test = case["test"]
        expected_result = case["expected"]
        
        # Run test with sync implementation
        sync_results = run_unit_tests_sync([generation], [test])
        sync_passed = sync_results[0][0].get("passed", False)
        
        # Run test with async implementation - using string format
        async with aiohttp.ClientSession() as session:
            # Use string format directly (like sync implementation)
            string_test = test
            semaphore = asyncio.Semaphore(1)
            async_result = await execute_test(session, generation, string_test, semaphore)
            async_passed = async_result.get("passed", False)
        
        # Verify both implementations match the expected result
        assert sync_passed == expected_result, f"Sync implementation failed for test: {test}"
        assert async_passed == expected_result, f"Async implementation failed for test: {test}"
        
        # Verify both implementations match each other
        assert sync_passed == async_passed, "Sync and async implementations returned different results"
    
    print("\nBoth sync and async implementations work correctly with string test format")


@patch("librarybench.execution.CYBER_URL", "https://mock-url.com")
@patch("librarybench.execution.asyncio.run")
def test_run_unit_tests(mock_asyncio_run):
    """Test that run_unit_tests correctly calls run_unit_tests_async using asyncio.run."""
    # Setup test data
    generations = ["def add(a, b): return a + b"]
    tests = ["assert add(1, 2) == 3"]
    concurrency = 10
    
    # Mock the return value of asyncio.run
    expected_results = [[{"passed": True}]]
    mock_asyncio_run.return_value = expected_results
    
    # Call the function under test
    results = run_unit_tests(generations, tests, concurrency)
    
    # Verify that asyncio.run was called
    mock_asyncio_run.assert_called_once()
    
    # Verify the results were correctly returned from asyncio.run
    assert results == expected_results
    
    print("\nrun_unit_tests correctly wraps the async function with asyncio.run")
