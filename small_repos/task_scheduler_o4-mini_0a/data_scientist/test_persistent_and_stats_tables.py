import sqlite3
import pytest
from pipeline_manager import PipelineManager

def test_tables_exist_and_initially_empty(tmp_path):
    dbfile = tmp_path / "my.db"
    mgr = PipelineManager(db_path=str(dbfile))
    conn = sqlite3.connect(str(dbfile))
    c = conn.cursor()
    # Check tables
    tables = {row[0] for row in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    expected = {'jobs', 'job_stats', 'tags', 'locks'}
    assert expected.issubset(tables)
    # Check empty
    for t in expected:
        cnt = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        assert cnt == 0
    conn.close()
