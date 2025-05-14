import pytest
from src.interfaces.ux_prototyper.cli import scaffold_wizard, dump_state, SESSIONS

def test_scaffold_and_dump_state():
    session_id = scaffold_wizard()
    assert session_id in SESSIONS
    assert SESSIONS[session_id] is not None
    out = dump_state(session_id)
    assert out is None
    fake = 'no_session'
    out2 = dump_state(fake)
    assert out2 is None