"""Utility functions shared across implementations."""

from common.core.utils.date_utils import (
    DateRangeType,
    get_date_range,
    get_first_day_of_month,
    get_last_day_of_month,
    get_first_day_of_quarter,
    get_last_day_of_quarter,
    get_first_day_of_year,
    get_last_day_of_year,
    date_range,
    month_range,
    quarter_range,
    year_range,
    is_same_month,
    is_same_quarter,
    is_same_year,
    get_fiscal_year,
)

from common.core.utils.cache_utils import (
    Cache,
    memoize,
    memoize_with_expiry,
)

from common.core.utils.performance import (
    Timer,
    PerformanceMonitor,
    time_it,
    monitor_performance,
    global_monitor,
    global_timer,
)

from common.core.utils.validation import (
    validate_non_negative,
    validate_positive,
    validate_percentage,
    validate_decimal_percentage,
    validate_date_not_future,
    validate_date_range,
    validate_string_not_empty,
    validate_string_length,
    validate_string_pattern,
    validate_email,
    validate_in_set,
    validate_list_not_empty,
    validate_list_length,
    add_validator,
)

__all__ = [
    # Date utilities
    "DateRangeType",
    "get_date_range",
    "get_first_day_of_month",
    "get_last_day_of_month", 
    "get_first_day_of_quarter",
    "get_last_day_of_quarter",
    "get_first_day_of_year",
    "get_last_day_of_year",
    "date_range",
    "month_range",
    "quarter_range",
    "year_range",
    "is_same_month",
    "is_same_quarter",
    "is_same_year",
    "get_fiscal_year",
    
    # Cache utilities
    "Cache",
    "memoize",
    "memoize_with_expiry",
    
    # Performance utilities
    "Timer",
    "PerformanceMonitor",
    "time_it",
    "monitor_performance",
    "global_monitor",
    "global_timer",
    
    # Validation utilities
    "validate_non_negative",
    "validate_positive",
    "validate_percentage",
    "validate_decimal_percentage",
    "validate_date_not_future",
    "validate_date_range",
    "validate_string_not_empty",
    "validate_string_length",
    "validate_string_pattern",
    "validate_email",
    "validate_in_set",
    "validate_list_not_empty",
    "validate_list_length",
    "add_validator",
]