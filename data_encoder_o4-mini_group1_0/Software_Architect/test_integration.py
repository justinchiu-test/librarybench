import pytest
from Software_Architect.compatibility import run_integration_tests

def test_run_integration_tests_all_pass():
    def t1(): return True
    def t2(): return 1        # truthy
    suite = {
        "test_pass_1": t1,
        "test_pass_2": t2
    }
    results = run_integration_tests(suite)
    assert results == {
        "test_pass_1": {"success": True, "error": None},
        "test_pass_2": {"success": True, "error": None},
    }

def test_run_integration_tests_all_fail_without_error():
    def f1(): return False
    def f2(): return 0       # falsey
    suite = {
        "fail_1": f1,
        "fail_2": f2
    }
    results = run_integration_tests(suite)
    assert results == {
        "fail_1": {"success": False, "error": None},
        "fail_2": {"success": False, "error": None},
    }

def test_run_integration_tests_raises_exception():
    def bomb(): raise RuntimeError("Integration system down")
    suite = {"explosive_test": bomb}
    results = run_integration_tests(suite)
    assert "explosive_test" in results
    entry = results["explosive_test"]
    assert entry["success"] is False
    assert "Integration system down" in entry["error"]

def test_run_integration_tests_mixed_results():
    def good(): return True
    def bad(): return False
    def error(): raise ValueError("Something went wrong")
    suite = {
        "good_case": good,
        "bad_case": bad,
        "error_case": error
    }
    results = run_integration_tests(suite)
    assert results == {
        "good_case": {"success": True,  "error": None},
        "bad_case":  {"success": False, "error": None},
        "error_case": {"success": False, "error": "Something went wrong"},
    }

def test_run_integration_tests_empty_suite():
    results = run_integration_tests({})
    assert results == {}
