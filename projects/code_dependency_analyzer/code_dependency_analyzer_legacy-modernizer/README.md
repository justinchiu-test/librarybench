# Legacy System Modernization Analyzer

A specialized dependency analysis tool designed for consultants modernizing legacy codebases. It helps understand tangled dependencies, plan incremental modernization strategies, and safely extract modules without breaking existing functionality.

## Overview

The Legacy System Modernization Analyzer provides comprehensive analysis capabilities for legacy Python codebases:

- **Legacy Pattern Detection**: Identifies common anti-patterns like god classes, circular dependencies, and spaghetti code
- **Database Coupling Analysis**: Detects shared database access patterns and raw SQL usage
- **Strangler Fig Planning**: Recommends optimal boundaries for incremental modernization
- **Module Extraction Feasibility**: Assesses how easily modules can be extracted and decoupled
- **Modernization Roadmap Generation**: Creates phased, actionable modernization plans

## Installation

### Prerequisites

- Python 3.8 or higher
- pip or uv package manager

### Install from source

```bash
# Clone the repository
git clone <repository-url>
cd legacy-modernization-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .

# Install development dependencies (for running tests)
pip install -e ".[dev]"
```

### Using uv (recommended)

```bash
# Create virtual environment
uv venv
source .venv/bin/activate

# Install the package
uv pip install -e .

# Install with dev dependencies
uv pip install -e ".[dev]"
```

## Usage

### Basic Analysis

```python
from legacy_analyzer import LegacyAnalyzer

# Create analyzer instance
analyzer = LegacyAnalyzer()

# Analyze a codebase
result = analyzer.analyze_codebase("/path/to/legacy/codebase")

# Access analysis results
print(f"Found {len(result.legacy_patterns)} legacy patterns")
print(f"Found {len(result.database_couplings)} database couplings")
print(f"Identified {len(result.strangler_boundaries)} potential boundaries")

# View summary
print(result.summary)
```

### Analyzing Specific Modules

```python
# Analyze extraction feasibility for specific modules
result = analyzer.analyze_codebase(
    "/path/to/codebase",
    modules_to_extract=["auth/login.py", "auth/logout.py"]
)

for feasibility in result.extraction_feasibilities:
    print(f"{feasibility.module_path}: {feasibility.feasibility_score:.2f}")
    print(f"Effort: {feasibility.estimated_effort_hours} hours")
    print(f"Risks: {', '.join(feasibility.risks)}")
```

### Generating Modernization Roadmap

```python
# Generate a comprehensive modernization roadmap
result = analyzer.analyze_codebase(
    "/path/to/codebase",
    generate_roadmap=True  # Default
)

roadmap = result.modernization_roadmap
print(f"Project duration: {roadmap.total_duration_days} days")
print(f"Number of phases: {len(roadmap.phases)}")

# View critical path
for milestone in roadmap.critical_path:
    print(f"- {milestone}")
```

### Working with Results

```python
# Legacy Patterns
for pattern in result.legacy_patterns:
    if pattern.risk.value == "critical":
        print(f"CRITICAL: {pattern.pattern_type.value} in {pattern.module_path}")
        print(f"  Description: {pattern.description}")
        print(f"  Difficulty: {pattern.difficulty.value}")

# Database Couplings
for coupling in result.database_couplings:
    if coupling.coupling_strength > 0.8:
        print(f"High coupling between: {', '.join(coupling.coupled_modules)}")
        print(f"  Shared tables: {', '.join(coupling.shared_tables)}")
        print(f"  Decoupling effort: {coupling.decoupling_effort_hours} hours")

# Strangler Fig Boundaries
for boundary in result.strangler_boundaries:
    print(f"Boundary: {boundary.boundary_name}")
    print(f"  Modules: {len(boundary.internal_modules)}")
    print(f"  Isolation score: {boundary.isolation_score:.2f}")
    print(f"  Recommended order: {boundary.recommended_order}")
```

## Features

### Legacy Pattern Detection

- **God Classes**: Large classes with too many responsibilities
- **Circular Dependencies**: Modules that depend on each other
- **Spaghetti Dependencies**: Modules with excessive external dependencies
- **Feature Envy**: Modules overly dependent on other modules
- **Shotgun Surgery**: Changes requiring modifications to many modules
- **Monolithic Structure**: Insufficient modularization

### Database Coupling Detection

- Identifies shared table access across modules
- Detects raw SQL queries that complicate modernization
- Recognizes ORM model sharing
- Calculates coupling strength and decoupling effort

### Strangler Fig Pattern Planning

- Identifies strongly connected components
- Detects natural module boundaries
- Calculates isolation scores
- Prioritizes boundaries by implementation difficulty
- Estimates effort for each boundary

### Module Extraction Feasibility

- Analyzes dependencies that need breaking
- Identifies backward compatibility requirements
- Assesses extraction risks
- Provides actionable recommendations
- Estimates extraction effort in hours

### Modernization Roadmap Generation

- Creates phased implementation plan
- Identifies critical path through modernization
- Assesses project risks
- Defines success metrics
- Estimates total project duration

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=legacy_analyzer

# Run specific test file
pytest tests/test_pattern_detector.py

# Run with verbose output
pytest -v

# Generate JSON report (required for verification)
pytest --json-report --json-report-file=pytest_results.json
```

## Performance

The analyzer is designed to handle large legacy codebases efficiently:

- Analyzes 100,000+ lines of code within 10 minutes
- Generates extraction plans for 50 modules in under 5 minutes
- Detects database coupling in 1,000 files in under 2 minutes
- Creates modernization roadmaps in under 60 seconds

## Architecture

The analyzer consists of several specialized components:

1. **PatternDetector**: Identifies legacy code patterns using AST analysis
2. **DatabaseCouplingDetector**: Finds database-related dependencies
3. **StranglerFigPlanner**: Plans optimal modernization boundaries
4. **ExtractionAnalyzer**: Assesses module extraction feasibility
5. **RoadmapGenerator**: Creates phased modernization plans
6. **LegacyAnalyzer**: Orchestrates all components

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.