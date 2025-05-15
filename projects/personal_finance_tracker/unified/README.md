# Unified Financial Management Library

## Overview
This project provides a unified financial management library that serves both freelancers and socially responsible investors through a common architecture. It maintains the original package structure while sharing core functionality through a common library.

The primary packages are:
- `common` - Core shared functionality for all implementations
- `personal_finance_tracker` - Freelancer financial management functionality
- `ethical_finance` - Socially responsible investor functionality

## Key Features

### For Freelancers
- Income smoothing for irregular revenue
- Business vs. personal expense categorization
- Project profitability analysis
- Tax obligation forecasting
- Cash runway visualization

### For Socially Responsible Investors
- Ethical investment screening
- Impact metric tracking
- Shareholder voting analysis
- Portfolio industry/sector analysis
- Values-aligned budget categories

### Common Functionality
- Transaction modeling and categorization
- Time-series analysis
- Financial calculations
- Data validation
- Performance monitoring

## Architecture
The library follows a modular architecture with a shared core:

```
common/
├── core/
│   ├── models/          # Shared data models
│   ├── categorization/  # Classification and categorization
│   ├── analysis/        # Financial analysis algorithms
│   ├── reporting/       # Reporting and summarization
│   └── utils/           # Shared utilities
```

## Installation
Install the library in development mode:

```bash
pip install -e .
```

## Usage
Import the original packages directly or use the common library:

```python
# Import from original packages (preserved for backward compatibility)
from personal_finance_tracker.expense import categorizer
from ethical_finance.ethical_screening import screening

# Import from common package (for shared functionality)
from common.core.models import Transaction
from common.core.categorization import Rule
```

## Testing
Run tests for all persona implementations:

```bash
pytest
```

Generate a JSON report for evaluation:

```bash
pytest tests/ --json-report --json-report-file=report.json --continue-on-collection-errors
```

## Documentation
See the following files for more detailed information:
- `PLAN.md` - Detailed refactoring plan and architecture
- `INSTRUCTIONS_freelancer.md` - Requirements for the freelancer persona
- `INSTRUCTIONS_socially_responsible_investor.md` - Requirements for the socially responsible investor persona

## License
This project is proprietary and for evaluation purposes only.