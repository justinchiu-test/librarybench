"""Command-line interface for PyPatternGuard."""

import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any

from .complexity_analyzer import ComplexityAnalyzer
from .memory_leak_detector import MemoryLeakDetector
from .database_pattern_analyzer import DatabasePatternAnalyzer
from .concurrency_analyzer import ConcurrencyAnalyzer
from .performance_regression_tracker import PerformanceRegressionTracker


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="PyPatternGuard - Performance Pattern Detection Engine"
    )
    
    parser.add_argument(
        "path",
        help="Path to Python file or directory to analyze"
    )
    
    parser.add_argument(
        "--analyze",
        choices=["all", "complexity", "memory", "database", "concurrency", "regression"],
        default="all",
        help="Type of analysis to perform"
    )
    
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format"
    )
    
    parser.add_argument(
        "--baseline",
        action="store_true",
        help="Update performance baseline (for regression analysis)"
    )
    
    parser.add_argument(
        "--severity",
        choices=["all", "high", "medium", "low"],
        default="all",
        help="Minimum severity level to report"
    )
    
    args = parser.parse_args()
    
    # Run analysis
    results = run_analysis(args.path, args.analyze, args.baseline)
    
    # Filter by severity
    if args.severity != "all":
        results = filter_by_severity(results, args.severity)
    
    # Output results
    if args.output == "json":
        print(json.dumps(results, indent=2))
    else:
        print_text_results(results)
    
    # Return exit code based on findings
    return 0 if not has_high_severity_issues(results) else 1


def run_analysis(path: str, analysis_type: str, update_baseline: bool) -> Dict[str, Any]:
    """Run the specified analysis on the given path."""
    results = {
        "path": path,
        "analysis_type": analysis_type,
        "issues": []
    }
    
    path_obj = Path(path)
    
    if analysis_type in ["all", "complexity"]:
        analyzer = ComplexityAnalyzer()
        if path_obj.is_file():
            complexity_results = analyzer.analyze_file(path)
        else:
            complexity_results = []
            for py_file in path_obj.rglob("*.py"):
                complexity_results.extend(analyzer.analyze_file(str(py_file)))
        
        results["complexity"] = [
            {
                "function": r.function_name,
                "time_complexity": r.time_complexity.value,
                "space_complexity": r.space_complexity.value,
                "line": r.line_number,
                "details": r.details
            }
            for r in complexity_results
        ]
    
    if analysis_type in ["all", "memory"]:
        analyzer = MemoryLeakDetector()
        if path_obj.is_file():
            memory_issues = analyzer.analyze_file(path)
        else:
            memory_issues = []
            for py_file in path_obj.rglob("*.py"):
                memory_issues.extend(analyzer.analyze_file(str(py_file)))
        
        results["memory_leaks"] = [
            {
                "type": issue.leak_type.value,
                "location": issue.location,
                "line": issue.line_number,
                "severity": issue.severity,
                "description": issue.description,
                "recommendation": issue.recommendation
            }
            for issue in memory_issues
        ]
    
    if analysis_type in ["all", "database"]:
        analyzer = DatabasePatternAnalyzer()
        if path_obj.is_file():
            db_issues = analyzer.analyze_file(path)
        else:
            db_issues = []
            for py_file in path_obj.rglob("*.py"):
                db_issues.extend(analyzer.analyze_file(str(py_file)))
        
        results["database_issues"] = [
            {
                "type": issue.issue_type.value,
                "location": issue.location,
                "line": issue.line_number,
                "severity": issue.severity,
                "description": issue.description,
                "recommendation": issue.recommendation,
                "orm": issue.orm_type
            }
            for issue in db_issues
        ]
    
    if analysis_type in ["all", "concurrency"]:
        analyzer = ConcurrencyAnalyzer()
        if path_obj.is_file():
            concurrency_issues = analyzer.analyze_file(path)
        else:
            concurrency_issues = []
            for py_file in path_obj.rglob("*.py"):
                concurrency_issues.extend(analyzer.analyze_file(str(py_file)))
        
        results["concurrency_issues"] = [
            {
                "type": issue.issue_type.value,
                "location": issue.location,
                "line": issue.line_number,
                "severity": issue.severity,
                "description": issue.description,
                "recommendation": issue.recommendation,
                "context": issue.context
            }
            for issue in concurrency_issues
        ]
    
    if analysis_type in ["all", "regression"]:
        if not path_obj.is_dir():
            results["regression_error"] = "Regression analysis requires a directory path"
        else:
            tracker = PerformanceRegressionTracker()
            
            if update_baseline:
                tracker.update_baseline(path)
                results["baseline_updated"] = True
            else:
                regressions = tracker.analyze_codebase(path)
                results["regressions"] = [
                    {
                        "type": reg.regression_type.value,
                        "function": reg.function_name,
                        "module": reg.module_path,
                        "severity": reg.severity,
                        "description": reg.description,
                        "recommendation": reg.recommendation,
                        "impact": reg.impact_estimate
                    }
                    for reg in regressions
                ]
    
    return results


def filter_by_severity(results: Dict[str, Any], min_severity: str) -> Dict[str, Any]:
    """Filter results by minimum severity level."""
    severity_levels = {"low": 1, "medium": 2, "high": 3}
    min_level = severity_levels[min_severity]
    
    filtered = results.copy()
    
    for key in ["memory_leaks", "database_issues", "concurrency_issues", "regressions"]:
        if key in filtered:
            filtered[key] = [
                issue for issue in filtered[key]
                if severity_levels.get(issue.get("severity", "low"), 1) >= min_level
            ]
    
    return filtered


def has_high_severity_issues(results: Dict[str, Any]) -> bool:
    """Check if there are any high severity issues."""
    for key in ["memory_leaks", "database_issues", "concurrency_issues", "regressions"]:
        if key in results:
            for issue in results[key]:
                if issue.get("severity") == "high":
                    return True
    return False


def print_text_results(results: Dict[str, Any]) -> None:
    """Print results in human-readable text format."""
    print(f"\n=== PyPatternGuard Analysis Results ===")
    print(f"Path: {results['path']}")
    print(f"Analysis Type: {results['analysis_type']}\n")
    
    if "complexity" in results:
        print("--- Complexity Analysis ---")
        for func in results["complexity"]:
            print(f"  {func['function']} (line {func['line']}):")
            print(f"    Time: {func['time_complexity']}, Space: {func['space_complexity']}")
            if func["details"].get("recursive"):
                print(f"    Warning: Recursive function")
        print()
    
    if "memory_leaks" in results:
        print("--- Memory Leak Detection ---")
        if not results["memory_leaks"]:
            print("  No memory leaks detected")
        else:
            for issue in results["memory_leaks"]:
                print(f"  [{issue['severity'].upper()}] {issue['type']} at {issue['location']} (line {issue['line']})")
                print(f"    {issue['description']}")
                print(f"    Fix: {issue['recommendation']}")
        print()
    
    if "database_issues" in results:
        print("--- Database Pattern Analysis ---")
        if not results["database_issues"]:
            print("  No database issues detected")
        else:
            for issue in results["database_issues"]:
                orm_info = f" ({issue['orm']})" if issue.get('orm') else ""
                print(f"  [{issue['severity'].upper()}] {issue['type']}{orm_info} at {issue['location']} (line {issue['line']})")
                print(f"    {issue['description']}")
                print(f"    Fix: {issue['recommendation']}")
        print()
    
    if "concurrency_issues" in results:
        print("--- Concurrency Analysis ---")
        if not results["concurrency_issues"]:
            print("  No concurrency issues detected")
        else:
            for issue in results["concurrency_issues"]:
                ctx_info = f" ({issue['context']})" if issue.get('context') else ""
                print(f"  [{issue['severity'].upper()}] {issue['type']}{ctx_info} at {issue['location']} (line {issue['line']})")
                print(f"    {issue['description']}")
                print(f"    Fix: {issue['recommendation']}")
        print()
    
    if "regressions" in results:
        print("--- Performance Regression Analysis ---")
        if not results["regressions"]:
            print("  No performance regressions detected")
        else:
            for reg in results["regressions"]:
                print(f"  [{reg['severity'].upper()}] {reg['type']} in {reg['function']} ({reg['module']})")
                print(f"    {reg['description']}")
                print(f"    Fix: {reg['recommendation']}")
                if reg.get('impact'):
                    print(f"    Impact: {reg['impact']}")
        print()
    
    if "baseline_updated" in results:
        print("✓ Performance baseline updated successfully")
    
    # Summary
    total_issues = sum(
        len(results.get(key, []))
        for key in ["memory_leaks", "database_issues", "concurrency_issues", "regressions"]
    )
    
    print(f"\n=== Summary ===")
    print(f"Total issues found: {total_issues}")
    
    if total_issues > 0:
        high_count = sum(
            1 for key in ["memory_leaks", "database_issues", "concurrency_issues", "regressions"]
            if key in results
            for issue in results[key]
            if issue.get("severity") == "high"
        )
        if high_count > 0:
            print(f"High severity issues: {high_count} (requires immediate attention)")


if __name__ == "__main__":
    sys.exit(main())