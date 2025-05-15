"""
CLI for UX Prototyper adapter
"""
from .wizard_engine import WizardEngine

SESSIONS = {}

def scaffold_wizard():
    session_id = len(SESSIONS) + 1
    SESSIONS[session_id] = WizardEngine()
    return session_id

def dump_state(session_id):
    session = SESSIONS.get(session_id)
    if session is None:
        return None
    return session.current_state