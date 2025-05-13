import pytest
import asyncio
from cicd import CiCdTrigger

@pytest.mark.asyncio
async def test_cicd_trigger(tmp_path):
    # Use echo as a harmless command
    trigger = CiCdTrigger("echo")
    test_file = str(tmp_path / "dummy.txt")
    rc = await trigger.trigger(test_file, "created")
    assert rc == 0
