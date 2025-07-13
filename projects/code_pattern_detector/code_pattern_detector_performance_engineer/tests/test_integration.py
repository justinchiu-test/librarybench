"""Integration tests for PyPatternGuard."""

import pytest
import tempfile
import os
import json
import subprocess
import sys
from pathlib import Path


class TestIntegration:
    """Integration tests for the complete system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_project_dir = os.path.join(self.temp_dir, "test_project")
        os.makedirs(self.test_project_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_test_project(self):
        """Create a test project with various performance issues."""
        # Create main.py with multiple issues
        main_content = '''
import threading
import time

# Global cache without eviction
cache = {}

class DataProcessor:
    def __init__(self):
        self.data = []
        self.lock = threading.Lock()
        # Missing cleanup for resources
        self.file = open("data.txt", "w")
    
    def process_items(self, items):
        """O(n^2) complexity - nested loops"""
        results = []
        for item in items:
            for other in items:
                if item != other:
                    results.append((item, other))
        return results
    
    def add_to_cache(self, key, value):
        """Unbounded cache growth"""
        cache[key] = value
    
    def unsafe_increment(self):
        """Race condition - unprotected shared state"""
        self.data.append(1)  # Not protected by lock

# N+1 query pattern
def get_user_posts(users):
    all_posts = []
    for user in users:
        # Simulating database query in loop
        posts = db.query(f"SELECT * FROM posts WHERE user_id = {user.id}")
        all_posts.extend(posts)
    return all_posts

# Blocking operation in async context
async def fetch_data():
    # Blocking I/O in async function
    with open("data.txt", "r") as f:
        return f.read()

# Circular reference
class Node:
    def __init__(self, value, parent=None):
        self.value = value
        self.parent = parent
        if parent:
            parent.child = self  # Circular reference
'''
        
        with open(os.path.join(self.test_project_dir, "main.py"), "w") as f:
            f.write(main_content)
        
        # Create db_operations.py with database patterns
        db_content = '''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def inefficient_query(session):
    # Missing limit clause
    all_users = session.query(User).all()
    
    # N+1 query pattern
    for user in all_users:
        for order in user.orders:  # Lazy loading in loop
            print(order.total)
    
    return all_users

def bulk_insert_wrong(session, items):
    # Should use bulk operations
    for item in items:
        new_item = Item(name=item['name'])
        session.add(new_item)
        session.commit()  # Committing in loop!
'''
        
        with open(os.path.join(self.test_project_dir, "db_operations.py"), "w") as f:
            f.write(db_content)
        
        # Create utils.py with moderate complexity
        utils_content = '''
def fibonacci(n):
    """Exponential complexity O(2^n)"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def binary_search(arr, target):
    """Logarithmic complexity O(log n)"""
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

def create_matrix(n):
    """O(n^2) space complexity"""
    return [[0 for _ in range(n)] for _ in range(n)]
'''
        
        with open(os.path.join(self.test_project_dir, "utils.py"), "w") as f:
            f.write(utils_content)
    
    def test_full_analysis_all_modules(self):
        """Test analyzing all modules together."""
        self.create_test_project()
        
        # Run analysis using CLI
        from pypatternguard.cli import run_analysis
        
        results = run_analysis(self.test_project_dir, "all", False)
        
        # Verify all analysis types produced results
        assert "complexity" in results
        assert "memory_leaks" in results
        assert "database_issues" in results
        assert "concurrency_issues" in results
        
        # Verify specific issues were detected
        assert len(results["complexity"]) > 0
        assert any(c["time_complexity"] == "O(n^2)" for c in results["complexity"])
        assert any(c["time_complexity"] == "O(2^n)" for c in results["complexity"])
        
        assert len(results["memory_leaks"]) > 0
        # Check that we detected some memory issues
        assert any(m["type"] for m in results["memory_leaks"])
        
        assert len(results["database_issues"]) > 0
        assert any("N+1 Query" in d["type"] for d in results["database_issues"])
        
        assert len(results["concurrency_issues"]) > 0
        assert any("Race Condition" in c["type"] or "Shared State" in c["type"] 
                  for c in results["concurrency_issues"])
    
    def test_severity_filtering(self):
        """Test filtering results by severity."""
        self.create_test_project()
        
        from pypatternguard.cli import run_analysis, filter_by_severity
        
        # Get all results
        all_results = run_analysis(self.test_project_dir, "all", False)
        
        # Filter for high severity only
        high_only = filter_by_severity(all_results, "high")
        
        # Verify filtering worked
        for category in ["memory_leaks", "database_issues", "concurrency_issues"]:
            if category in high_only:
                assert all(issue["severity"] == "high" for issue in high_only[category])
    
    def test_json_output_format(self):
        """Test JSON output format is valid."""
        self.create_test_project()
        
        from pypatternguard.cli import run_analysis
        
        results = run_analysis(self.test_project_dir, "all", False)
        
        # Ensure results can be serialized to JSON
        json_output = json.dumps(results, indent=2)
        assert json_output
        
        # Ensure it can be parsed back
        parsed = json.loads(json_output)
        assert parsed["path"] == self.test_project_dir
    
    def test_single_file_analysis(self):
        """Test analyzing a single file."""
        self.create_test_project()
        
        from pypatternguard.cli import run_analysis
        
        single_file = os.path.join(self.test_project_dir, "utils.py")
        results = run_analysis(single_file, "complexity", False)
        
        assert "complexity" in results
        assert len(results["complexity"]) == 3  # Three functions in utils.py
        
        # Verify specific functions
        function_names = {c["function"] for c in results["complexity"]}
        assert "fibonacci" in function_names
        assert "binary_search" in function_names
        assert "create_matrix" in function_names
    
    def test_regression_tracking_workflow(self):
        """Test the complete regression tracking workflow."""
        # Create version 1
        v1_content = '''
def search_items(items, target):
    for item in items:
        if item == target:
            return True
    return False
'''
        
        with open(os.path.join(self.test_project_dir, "search.py"), "w") as f:
            f.write(v1_content)
        
        from pypatternguard.cli import run_analysis
        
        # Create baseline
        run_analysis(self.test_project_dir, "regression", True)
        
        # Create version 2 with worse complexity
        v2_content = '''
def search_items(items, target):
    # Inefficient nested loop version
    for i in range(len(items)):
        for j in range(len(items)):
            if items[j] == target:
                return True
    return False
'''
        
        with open(os.path.join(self.test_project_dir, "search.py"), "w") as f:
            f.write(v2_content)
        
        # Check for regressions
        results = run_analysis(self.test_project_dir, "regression", False)
        
        assert "regressions" in results
        assert len(results["regressions"]) > 0
        assert any("Complexity Increased" in r["type"] for r in results["regressions"])
    
    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        from pypatternguard.cli import run_analysis
        
        # Non-existent path
        results = run_analysis("/non/existent/path", "all", False)
        assert "path" in results
        
        # Invalid Python file
        invalid_file = os.path.join(self.temp_dir, "invalid.py")
        with open(invalid_file, "w") as f:
            f.write("this is not valid Python syntax {[}")
        
        results = run_analysis(invalid_file, "all", False)
        # Should handle gracefully and return empty results
        assert "complexity" in results
        assert len(results.get("complexity", [])) == 0
    
    def test_high_severity_exit_code(self):
        """Test that high severity issues affect exit code."""
        self.create_test_project()
        
        from pypatternguard.cli import has_high_severity_issues, run_analysis
        
        results = run_analysis(self.test_project_dir, "all", False)
        
        # Should have high severity issues
        assert has_high_severity_issues(results) is True
    
    def test_performance_metrics(self):
        """Test performance of analysis on larger codebase."""
        # Create a larger test project
        for i in range(10):
            module_content = f'''
def function_{i}_constant():
    return {i}

def function_{i}_linear(arr):
    total = 0
    for item in arr:
        total += item
    return total

def function_{i}_quadratic(matrix):
    result = []
    for row in matrix:
        for col in row:
            result.append(col)
    return result
'''
            with open(os.path.join(self.test_project_dir, f"module_{i}.py"), "w") as f:
                f.write(module_content)
        
        import time
        from pypatternguard.cli import run_analysis
        
        start_time = time.time()
        results = run_analysis(self.test_project_dir, "all", False)
        end_time = time.time()
        
        # Should complete within reasonable time (< 5 seconds for 10 files)
        assert end_time - start_time < 5.0
        
        # Should analyze all functions
        assert len(results["complexity"]) == 30  # 3 functions * 10 files