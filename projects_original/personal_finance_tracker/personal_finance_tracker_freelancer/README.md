# Freelancer Financial Management System

A specialized financial management system designed for freelancers and independent contractors who experience irregular income patterns and project-based earnings.

## Features

- Income smoothing calculations for consistent budgeting
- Project profitability analysis to compare time invested against revenue
- Tax obligation forecasting with quarterly estimated payment scheduling
- Business versus personal expense separation
- Cash runway visualization for financial planning

## Installation

```bash
pip install -e .
```

## Development

```bash
# Install development dependencies
pip install pytest pytest-json-report

# Run tests
pytest --json-report --json-report-file=pytest_results.json
```