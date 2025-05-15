# VectorDB: Vector-Optimized In-Memory Database for ML Applications

A specialized in-memory database optimized for machine learning feature storage and retrieval that provides efficient vector operations, feature versioning, batch prediction support, automatic feature transformations, and A/B testing capabilities to accelerate ML inference workflows while ensuring data consistency.

## Features

- Vector Data Types with Optimized Distance Calculations
- Feature Store with Versioning and Lineage
- Batch Prediction Optimization
- Automatic Feature Normalization and Transformation
- A/B Testing Support

## Installation

```bash
# Install in development mode
uv pip install -e .
```

## Testing

```bash
# Install pytest and json-report plugin
pip install pytest-json-report

# Run tests
pytest --json-report --json-report-file=pytest_results.json
```