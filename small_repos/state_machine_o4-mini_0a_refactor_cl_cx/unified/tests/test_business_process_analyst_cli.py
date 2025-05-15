import pytest
from business_process_analyst.cli import scaffold_process, dump_state

def test_cli_scaffold_and_dump_state():
    pid = scaffold_process()
    assert isinstance(pid, int)
    state = dump_state(pid)
    assert state is None
    with pytest.raises(ValueError):
        dump_state(pid + 1)
