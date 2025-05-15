"""
Data lineage tracking for data transformations.
"""

# Global store for lineage tracking
lineage_store = {}

def track_lineage(record_or_func, step_name=None):
    """
    Track data lineage through transformations.
    
    This function has two modes:
    - Compliance Officer: Decorator that updates lineage for record with 'id' field
    - Social Media Analyst: Direct function that adds _lineage field to record
    
    Args:
        record_or_func: Record to track or function to wrap
        step_name: Name of the processing step (used in Social Media Analyst mode)
        
    Returns:
        Updated record or decorated function
    """
    # Social Media Analyst mode - direct function call
    if not callable(record_or_func) and isinstance(record_or_func, dict):
        record = record_or_func
        lineage = record.get('_lineage', [])
        lineage.append(step_name)
        return {**record, '_lineage': lineage}
    
    # Compliance Officer mode - decorator
    def decorator(func):
        def wrapper(record, *args, **kwargs):
            result = func(record, *args, **kwargs)
            if result and isinstance(result, dict) and 'id' in result:
                record_id = result['id']
                if record_id not in lineage_store:
                    lineage_store[record_id] = []
                lineage_store[record_id].append(func.__name__)
            return result
        
        return wrapper
    
    if callable(record_or_func):
        return decorator(record_or_func)
    
    return None