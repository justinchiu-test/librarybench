# Business Process Analyst CLI
import random
import time

_SESSIONS = {}

def scaffold_process():
    """
    Create a new process ID for tracking.
    
    Returns:
        int: A unique process ID
    """
    # Generate a random process ID
    pid = random.randint(10000, 99999)
    while pid in _SESSIONS:
        pid = random.randint(10000, 99999)
    
    # Store empty state for this process
    _SESSIONS[pid] = None
    return pid

def dump_state(pid):
    """
    Dump the current state of a process.
    
    Args:
        pid: The process ID to dump state for
    
    Returns:
        dict: The current state, or None if not set
        
    Raises:
        ValueError: If the process ID is invalid
    """
    if pid not in _SESSIONS:
        raise ValueError(f"Invalid process ID: {pid}")
    
    return _SESSIONS[pid]