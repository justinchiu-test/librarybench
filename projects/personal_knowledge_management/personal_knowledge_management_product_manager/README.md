# ProductInsight - Strategic Product Knowledge System

A specialized personal knowledge management system for product managers to organize user feedback, feature requests, market research, and strategic decision making.

## Overview

ProductInsight is a comprehensive knowledge management system designed specifically for product managers who oversee complex software products with multiple stakeholders. The system excels at organizing and analyzing user feedback, tracking competitive intelligence, documenting strategic decisions, and aligning feature development with business objectives.

## Key Features

- **Customer Feedback Clustering**: Automatically group and analyze similar requests and pain points
- **Feature Prioritization Framework**: Create structured relationships linking requests to strategic objectives
- **Competitive Intelligence Tracking**: Monitor and analyze market positioning against alternatives
- **Decision Documentation**: Capture and preserve context and rationale for product choices
- **Stakeholder Perspective Mapping**: Visualize and track different viewpoints on product direction
- **Knowledge Discovery**: Find connections between different knowledge domains

## System Architecture

ProductInsight is built as a modular Python application with the following components:

- **Feedback Management**: Processing, clustering, and analyzing customer feedback
- **Strategic Objectives**: Managing product vision, goals, and strategic initiatives
- **Feature Prioritization**: Scoring and ranking features using multiple prioritization models
- **Competitive Analysis**: Tracking and comparing competitor products and capabilities
- **Decision Management**: Documenting and retrieving product decisions with context
- **Stakeholder Management**: Tracking stakeholders, their perspectives, and relationships
- **Knowledge Discovery**: Searching across domains and generating insights

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd personal_knowledge_management_product_manager

# Install using uv (recommended)
uv sync

# Or install using pip
pip install -e .

# For development
uv sync --all
```

## Usage

```bash
# Initialize data directory
python -m product_insight.main --init

# Process and cluster feedback
python -m product_insight.main feedback cluster

# Prioritize features
python -m product_insight.main feature prioritize --method weighted

# Get top features
python -m product_insight.main feature top --limit 10

# Search across knowledge domains
python -m product_insight.main search "export functionality" --limit 20

# Generate insights
python -m product_insight.main insight all

# Generate trend analysis
python -m product_insight.main insight trends --days 90 --interval 30
```

## Development

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=product_insight

# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type check
uv run pyright
```

## Project Structure

```
product_insight/
├── __init__.py
├── main.py
├── models.py
├── competitive/       # Competitive analysis
├── decisions/         # Decision management
├── discovery/         # Search and insights
├── feedback/          # Feedback management
├── prioritization/    # Feature prioritization
├── stakeholders/      # Stakeholder management
├── strategy/          # Strategic objectives
└── storage/           # Data persistence

tests/
├── fixtures/          # Test fixtures and mock data
├── test_competitive.py
├── test_decisions.py
├── test_discovery.py
├── test_feedback.py
├── test_integration.py
├── test_models.py
├── test_performance.py
├── test_prioritization.py
├── test_stakeholders.py
└── test_storage.py
```

## Key Constraints

- All data is stored locally as plain text files for longevity and accessibility
- No external API dependencies for core functionality
- System works offline for executive presentations and travel
- Data structures prioritize integrity and prevent unintentional data loss
- Supports concurrent use by product team members with shared repositories

## License

MIT License
