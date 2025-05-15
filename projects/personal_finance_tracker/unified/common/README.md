# Common Library

This package provides shared functionality for financial applications, including:

## Core Components

### Models
- Base transaction model
- Category interface
- Time entry tracking
- Financial entity models
- Investment and portfolio models
- Tax-related models

### Categorization
- Generic rule engine
- Category mapping and matching
- Confidence scoring
- Audit trail management

### Analysis
- Time-series calculations
- Financial metrics computation
- Projection algorithms
- Scoring and evaluation framework

### Reporting
- Summary generation
- Time-period reporting
- Data aggregation utilities

### Utilities
- Date utilities
- Caching utilities
- Performance monitoring
- Validation helpers

## Usage

Import components from the common library:

```python
# Import specific components
from common.core.models import BaseTransaction, Project
from common.core.categorization import Rule, TransactionCategorizer
from common.core.analysis import TimeSeriesAnalyzer, PortfolioAnalyzer
from common.core.reporting import Report, TransactionSummaryGenerator
from common.core.utils import Timer, validate_percentage, get_date_range

# Or import all functionality
from common import *
```