import pytest
import os
import asyncio
from watcher.watcher import Watcher

@pytest.mark.asyncio
async def test_symlink_follow(tmp_path):
    dir1 = tmp_path / 'd'
    dir1.mkdir()
    target = dir1 / 'a.txt'
    target.write_text('1')
    link = tmp_path / 'link.txt'
    os.symlink(str(target), str(link))
    # follow symlinks
    w1 = Watcher(paths=[str(tmp_path)], poll_interval=0.01, debounce_interval=0,
                 follow_symlinks=True)
    snap = w1._take_snapshot()
    assert any(p.endswith('link.txt') for p in snap)
    # do not follow
    w2 = Watcher(paths=[str(tmp_path)], poll_interval=0.01, debounce_interval=0,
                 follow_symlinks=False)
    snap2 = w2._take_snapshot()
    # symlink path still appears but target metadata not followed; stat may fail
    assert any('link.txt' in p for p in snap2)
