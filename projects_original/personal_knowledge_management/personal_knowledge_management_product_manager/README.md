# ProductMind

A specialized knowledge management system designed for product managers who need to organize customer feedback, track feature requests, monitor competitive intelligence, document strategic decisions, and map stakeholder perspectives.

## Core Features

1. **Feedback Analysis Engine**: Processes user input through NLP, clustering, sentiment analysis, and trend detection.
2. **Strategic Prioritization Framework**: Evaluates features using multi-criteria scoring, strategic alignment, and resource constraints.
3. **Competitive Analysis System**: Manages competitor profiles, comparative analysis, and market positioning.
4. **Decision Registry**: Captures decision rationale, alternatives considered, and context preservation.
5. **Stakeholder Insight Manager**: Handles stakeholder perspectives, conflict detection, and consensus building.

## Installation

```bash
pip install -e .
```

## Testing

Run tests with pytest:

```bash
pytest
```

To generate test reports:

```bash
pytest --json-report --json-report-file=pytest_results.json
```

## Usage

This package provides a Python API for product knowledge management. All data is stored locally in plain text formats.

```python
from productmind.feedback_analysis import FeedbackAnalysisEngine
from productmind.prioritization import PrioritizationFramework
from productmind.competitive_analysis import CompetitiveAnalysisSystem
from productmind.decision_registry import DecisionRegistry
from productmind.stakeholder_insights import StakeholderInsightManager

# Initialize components
feedback_engine = FeedbackAnalysisEngine()
prioritization = PrioritizationFramework()
competitive = CompetitiveAnalysisSystem()
decisions = DecisionRegistry()
stakeholders = StakeholderInsightManager()

# Use APIs to manage product knowledge
```