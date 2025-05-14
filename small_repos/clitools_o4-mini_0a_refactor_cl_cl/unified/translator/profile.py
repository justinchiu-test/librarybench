"""
Profiling utilities for translator CLI tools.
"""

import time
from typing import Dict, Any, Callable, Tuple, List


def profile_command(*steps: Tuple[str, Callable]) -> Dict[str, float]:
    """
    Profile the execution time of a sequence of steps.
    
    Args:
        *steps: Variable number of (name, function) tuples.
        
    Returns:
        Dict[str, float]: Dictionary mapping step names to execution times.
    """
    results = {}
    
    for name, func in steps:
        start_time = time.time()
        func()
        end_time = time.time()
        
        results[name] = end_time - start_time
    
    return results