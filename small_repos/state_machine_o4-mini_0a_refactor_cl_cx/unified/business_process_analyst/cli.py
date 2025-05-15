"""
CLI for Business Process Analyst adapter
"""
from .process_engine import _default_machine

SESSIONS = {}

def scaffold_process():
    pid = len(SESSIONS) + 1
    SESSIONS[pid] = _default_machine
    return pid

def dump_state(pid):
    if pid not in SESSIONS:
        raise ValueError(f"No such session {pid}")
    session = SESSIONS[pid]
    return session.current_state