# PyPatternGuard - Performance Pattern Detection Engine

A specialized code pattern detection system designed for performance engineers to identify code patterns that impact application performance. PyPatternGuard detects inefficient algorithms, resource-intensive operations, and performance anti-patterns before they reach production.

## Features

- **Algorithm Complexity Analysis**: Detects Big O notation complexity for functions
- **Memory Leak Detection**: Identifies circular references and missing resource cleanup
- **Database Pattern Analysis**: Finds N+1 queries and inefficient database operations
- **Concurrency Analysis**: Detects race conditions and thread safety issues
- **Performance Regression Tracking**: Compares performance metrics across code versions

## Installation

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd pypatternguard

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Requirements

- Python 3.8 or higher
- No external dependencies for core functionality
- pytest and pytest-json-report for running tests

## Usage

### Command Line Interface

Analyze a single file:
```bash
pypatternguard path/to/file.py
```

Analyze an entire directory:
```bash
pypatternguard path/to/project/
```

### Analysis Options

```bash
# Run specific analysis type
pypatternguard path/to/code --analyze complexity
pypatternguard path/to/code --analyze memory
pypatternguard path/to/code --analyze database
pypatternguard path/to/code --analyze concurrency
pypatternguard path/to/code --analyze regression

# Filter by severity
pypatternguard path/to/code --severity high

# Output in JSON format
pypatternguard path/to/code --output json

# Update performance baseline
pypatternguard path/to/project --analyze regression --baseline
```

### Python API

```python
from pypatternguard import (
    ComplexityAnalyzer,
    MemoryLeakDetector,
    DatabasePatternAnalyzer,
    ConcurrencyAnalyzer,
    PerformanceRegressionTracker
)

# Analyze complexity
analyzer = ComplexityAnalyzer()
results = analyzer.analyze_file("example.py")
for result in results:
    print(f"{result.function_name}: {result.time_complexity}")

# Detect memory leaks
detector = MemoryLeakDetector()
issues = detector.analyze_file("example.py")
for issue in issues:
    print(f"{issue.leak_type}: {issue.description}")

# Track performance regressions
tracker = PerformanceRegressionTracker()
regressions = tracker.analyze_codebase("./src")
for regression in regressions:
    print(f"{regression.function_name}: {regression.description}")
```

## Analysis Types

### Complexity Analysis

Detects algorithmic complexity patterns:
- O(1) - Constant time
- O(log n) - Logarithmic
- O(n) - Linear
- O(n log n) - Linearithmic
- O(n²) - Quadratic
- O(n³) - Cubic
- O(2ⁿ) - Exponential
- O(n!) - Factorial

### Memory Leak Detection

Identifies:
- Circular references between objects
- Missing cleanup in `__del__` methods
- Unbounded global cache growth
- Generator exhaustion issues
- Event listener leaks

### Database Pattern Analysis

Detects:
- N+1 query problems
- Missing bulk operations
- Inefficient pagination
- Missing index usage
- Excessive joins
- Unbounded result sets

Supports Django, SQLAlchemy, Peewee, and generic SQL patterns.

### Concurrency Analysis

Finds:
- Race conditions in shared state access
- Potential deadlocks from lock ordering
- Missing synchronization
- Blocking operations in async contexts
- Thread-unsafe operations

### Performance Regression Tracking

Monitors:
- Complexity increases across versions
- New inefficiencies introduced
- Removed optimizations
- Resource usage increases
- Concurrency degradation

## Examples

### Example 1: Detecting O(n²) Complexity

```python
# Input code
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                duplicates.append(items[i])
    return duplicates

# PyPatternGuard output:
# find_duplicates: O(n²) time complexity
# Recommendation: Consider using a set or dictionary for O(n) solution
```

### Example 2: Finding N+1 Queries

```python
# Input code
def get_user_orders(users):
    for user in users:
        orders = Order.objects.filter(user=user).all()
        print(f"{user.name}: {len(orders)}")

# PyPatternGuard output:
# N+1 Query Problem detected at line 3
# Recommendation: Use select_related() or prefetch_related()
```

### Example 3: Detecting Race Conditions

```python
# Input code
counter = 0

def increment():
    global counter
    counter += 1  # Race condition!

# PyPatternGuard output:
# Race Condition: Unprotected shared state mutation
# Recommendation: Use threading.Lock or atomic operations
```

## Running Tests

Install test dependencies:
```bash
pip install pytest pytest-json-report
```

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=pypatternguard
```

Generate JSON test report:
```bash
pytest --json-report --json-report-file=pytest_results.json
```

## Configuration

PyPatternGuard stores performance baselines in `.performance_baseline.json` in your project root. This file is used for regression tracking and should be committed to version control.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and feature requests, please use the GitHub issue tracker.