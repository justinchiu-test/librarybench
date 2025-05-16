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

## Refactoring Implementation
The unified library has been successfully refactored to extract common functionality while maintaining backward compatibility for both personas:

### Implementation Approach
- **Inheritance**: Most persona-specific models extend base classes from the common library
- **Composition**: Complex systems use composition to leverage common components
- **Type Compatibility**: Union types are used where needed to ensure compatibility with existing APIs

### Key Migration Patterns
1. **Model Migration**: Domain models (Transaction, Investment, etc.) migrated to common.core.models
2. **Categorization**: Rule-based categorization system unified in common.core.categorization
3. **Analysis**: Time series and portfolio analysis extracted to common.core.analysis
4. **Performance**: Common Timer utility for consistent performance tracking

### Specialized Extensions
Each persona implementation extends the common library with specialized functionality:
- **Freelancer**: Extends Transaction model with specific fields for project tracking
- **Investor**: Extends Investment model with ESG (Environmental, Social, Governance) attributes

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

# Example of extending common functionality
from common.core.analysis.analyzer import BaseAnalyzer

class MyCustomAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__()
        # Custom initialization
        
    def analyze(self, data):
        with self.timer.measure("custom_analysis"):
            # Custom implementation
            return result
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
- `REFACTOR.md` - Original refactoring instructions and requirements

## License
This project is proprietary and for evaluation purposes only.