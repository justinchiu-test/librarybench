"""Date utilities shared across implementations."""

import calendar
from datetime import date, datetime, timedelta
from enum import Enum
from typing import List, Optional, Tuple, Union, Generator


class DateRangeType(str, Enum):
    """Types of date ranges for financial analysis."""
    
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


def get_date_range(
    range_type: DateRangeType,
    start_date: Optional[Union[date, datetime]] = None,
    end_date: Optional[Union[date, datetime]] = None,
    num_periods: Optional[int] = None,
) -> Tuple[Union[date, datetime], Union[date, datetime]]:
    """
    Get a date range based on the specified type.
    
    Args:
        range_type: Type of date range
        start_date: Optional start date (defaults to today if not provided)
        end_date: Optional end date
        num_periods: Optional number of periods for relative ranges
        
    Returns:
        Tuple of (start_date, end_date)
    """
    today = datetime.now().date()
    
    if range_type == DateRangeType.CUSTOM:
        # Use provided dates for custom range
        if start_date is None:
            start_date = today
        if end_date is None:
            end_date = today
        return start_date, end_date
    
    # Set default for num_periods
    if num_periods is None:
        num_periods = 1
    
    # Calculate date range based on type
    if range_type == DateRangeType.DAILY:
        if end_date is None:
            end_date = today
        start_date = end_date - timedelta(days=num_periods - 1)
    
    elif range_type == DateRangeType.WEEKLY:
        if end_date is None:
            # End on the last day of the current week (Sunday)
            days_to_end_of_week = 6 - today.weekday()
            end_date = today + timedelta(days=days_to_end_of_week)
        start_date = end_date - timedelta(weeks=num_periods, days=-1)
    
    elif range_type == DateRangeType.MONTHLY:
        if end_date is None:
            # End on the last day of the current month
            end_date = get_last_day_of_month(today)
        
        # Start on the first day of the month, num_periods months ago
        year = end_date.year
        month = end_date.month - num_periods + 1
        
        while month <= 0:
            year -= 1
            month += 12
        
        start_date = date(year, month, 1)
    
    elif range_type == DateRangeType.QUARTERLY:
        if end_date is None:
            # End on the last day of the current quarter
            quarter_end_month = ((today.month - 1) // 3 + 1) * 3
            end_date = get_last_day_of_month(date(today.year, quarter_end_month, 1))
        
        # Start on the first day of the quarter, num_periods quarters ago
        quarter = ((end_date.month - 1) // 3 + 1)
        year = end_date.year
        quarter_start = quarter - num_periods + 1
        
        while quarter_start <= 0:
            year -= 1
            quarter_start += 4
        
        start_month = (quarter_start - 1) * 3 + 1
        start_date = date(year, start_month, 1)
    
    elif range_type == DateRangeType.YEARLY:
        if end_date is None:
            # End on the last day of the current year
            end_date = date(today.year, 12, 31)
        
        # Start on the first day of the year, num_periods years ago
        start_date = date(end_date.year - num_periods + 1, 1, 1)
    
    else:
        # Default to daily
        if end_date is None:
            end_date = today
        start_date = end_date - timedelta(days=num_periods - 1)
    
    return start_date, end_date


def get_first_day_of_month(dt: Union[date, datetime]) -> date:
    """
    Get the first day of the month for a given date.
    
    Args:
        dt: The input date
        
    Returns:
        Date representing the first day of the month
    """
    return date(dt.year, dt.month, 1)


def get_last_day_of_month(dt: Union[date, datetime]) -> date:
    """
    Get the last day of the month for a given date.
    
    Args:
        dt: The input date
        
    Returns:
        Date representing the last day of the month
    """
    # Get the number of days in the month
    days_in_month = calendar.monthrange(dt.year, dt.month)[1]
    return date(dt.year, dt.month, days_in_month)


def get_first_day_of_quarter(dt: Union[date, datetime]) -> date:
    """
    Get the first day of the quarter for a given date.
    
    Args:
        dt: The input date
        
    Returns:
        Date representing the first day of the quarter
    """
    quarter = (dt.month - 1) // 3
    return date(dt.year, quarter * 3 + 1, 1)


def get_last_day_of_quarter(dt: Union[date, datetime]) -> date:
    """
    Get the last day of the quarter for a given date.
    
    Args:
        dt: The input date
        
    Returns:
        Date representing the last day of the quarter
    """
    quarter = (dt.month - 1) // 3
    month = quarter * 3 + 3
    return get_last_day_of_month(date(dt.year, month, 1))


def get_first_day_of_year(dt: Union[date, datetime]) -> date:
    """
    Get the first day of the year for a given date.
    
    Args:
        dt: The input date
        
    Returns:
        Date representing the first day of the year
    """
    return date(dt.year, 1, 1)


def get_last_day_of_year(dt: Union[date, datetime]) -> date:
    """
    Get the last day of the year for a given date.
    
    Args:
        dt: The input date
        
    Returns:
        Date representing the last day of the year
    """
    return date(dt.year, 12, 31)


def date_range(
    start_date: Union[date, datetime],
    end_date: Union[date, datetime],
    step: timedelta = timedelta(days=1),
) -> Generator[date, None, None]:
    """
    Generate a range of dates.
    
    Args:
        start_date: The start date
        end_date: The end date
        step: The step size (default: 1 day)
        
    Yields:
        Dates in the range
    """
    # Convert to date if datetime
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()
    
    # Generate dates
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += step


def month_range(
    start_date: Union[date, datetime],
    end_date: Union[date, datetime],
) -> Generator[date, None, None]:
    """
    Generate a range of month start dates.
    
    Args:
        start_date: The start date
        end_date: The end date
        
    Yields:
        First day of each month in the range
    """
    # Convert to date if datetime
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()
    
    # Start from the first day of the month
    current_month = get_first_day_of_month(start_date)
    
    # Generate month start dates
    while current_month <= end_date:
        yield current_month
        
        # Move to the next month
        if current_month.month == 12:
            current_month = date(current_month.year + 1, 1, 1)
        else:
            current_month = date(current_month.year, current_month.month + 1, 1)


def quarter_range(
    start_date: Union[date, datetime],
    end_date: Union[date, datetime],
) -> Generator[date, None, None]:
    """
    Generate a range of quarter start dates.
    
    Args:
        start_date: The start date
        end_date: The end date
        
    Yields:
        First day of each quarter in the range
    """
    # Convert to date if datetime
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()
    
    # Start from the first day of the quarter
    current_quarter = get_first_day_of_quarter(start_date)
    
    # Generate quarter start dates
    while current_quarter <= end_date:
        yield current_quarter
        
        # Move to the next quarter
        month = current_quarter.month
        year = current_quarter.year
        
        month += 3
        if month > 12:
            month -= 12
            year += 1
        
        current_quarter = date(year, month, 1)


def year_range(
    start_date: Union[date, datetime],
    end_date: Union[date, datetime],
) -> Generator[date, None, None]:
    """
    Generate a range of year start dates.
    
    Args:
        start_date: The start date
        end_date: The end date
        
    Yields:
        First day of each year in the range
    """
    # Convert to date if datetime
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()
    
    # Start from the first day of the year
    current_year = get_first_day_of_year(start_date)
    
    # Generate year start dates
    while current_year <= end_date:
        yield current_year
        current_year = date(current_year.year + 1, 1, 1)


def is_same_month(date1: Union[date, datetime], date2: Union[date, datetime]) -> bool:
    """
    Check if two dates are in the same month.
    
    Args:
        date1: First date
        date2: Second date
        
    Returns:
        True if dates are in the same month, False otherwise
    """
    return date1.year == date2.year and date1.month == date2.month


def is_same_quarter(date1: Union[date, datetime], date2: Union[date, datetime]) -> bool:
    """
    Check if two dates are in the same quarter.
    
    Args:
        date1: First date
        date2: Second date
        
    Returns:
        True if dates are in the same quarter, False otherwise
    """
    return (
        date1.year == date2.year and
        (date1.month - 1) // 3 == (date2.month - 1) // 3
    )


def is_same_year(date1: Union[date, datetime], date2: Union[date, datetime]) -> bool:
    """
    Check if two dates are in the same year.
    
    Args:
        date1: First date
        date2: Second date
        
    Returns:
        True if dates are in the same year, False otherwise
    """
    return date1.year == date2.year


def get_fiscal_year(
    dt: Union[date, datetime], fiscal_start_month: int = 1
) -> Tuple[int, date, date]:
    """
    Get the fiscal year information for a given date.
    
    Args:
        dt: The input date
        fiscal_start_month: The month when the fiscal year starts (1-12)
        
    Returns:
        Tuple of (fiscal_year, fiscal_year_start, fiscal_year_end)
    """
    # Validate fiscal start month
    if fiscal_start_month < 1 or fiscal_start_month > 12:
        fiscal_start_month = 1
    
    # Determine the fiscal year
    if dt.month < fiscal_start_month:
        fiscal_year = dt.year - 1
    else:
        fiscal_year = dt.year
    
    # Calculate start and end dates
    fiscal_year_start = date(fiscal_year, fiscal_start_month, 1)
    
    if fiscal_start_month == 1:
        fiscal_year_end = date(fiscal_year, 12, 31)
    else:
        next_fiscal_year = fiscal_year + 1
        next_fiscal_month = fiscal_start_month - 1
        if next_fiscal_month == 0:
            next_fiscal_month = 12
            next_fiscal_year -= 1
        
        fiscal_year_end = get_last_day_of_month(date(next_fiscal_year, next_fiscal_month, 1))
    
    return fiscal_year, fiscal_year_start, fiscal_year_end