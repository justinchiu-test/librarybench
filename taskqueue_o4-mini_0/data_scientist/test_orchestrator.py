import time
import os
from ml_pipeline.orchestrator import Orchestrator

def sample_success(x, y):
    return x + y

def sample_fail(x):
    raise ValueError("fail")

def test_orchestrator_success(tmp_path):
    logf = tmp_path / "audit.log"
    backup_dir = tmp_path / "backups"
    dlq_dir = tmp_path / "dlq"
    orch = Orchestrator(log_file=str(logf), backup_dir=str(backup_dir), dlq_dir=str(dlq_dir))
    tid = orch.enqueue_job(sample_success, {"x": 2, "y": 3})
    time.sleep(0.2)
    statuses = orch.list_statuses()
    assert statuses[tid] == "success"
    # backup exists
    assert os.path.exists(str(backup_dir / f"{tid}.pkl"))

def test_orchestrator_failure(tmp_path):
    logf = tmp_path / "audit.log"
    backup_dir = tmp_path / "backups"
    dlq_dir = tmp_path / "dlq"
    orch = Orchestrator(log_file=str(logf), backup_dir=str(backup_dir), dlq_dir=str(dlq_dir))
    tid = orch.enqueue_job(sample_fail, {"x": 1})
    time.sleep(0.2)
    statuses = orch.list_statuses()
    assert statuses[tid] == "failed"
    msgs = orch.dlq.pop_all()
    assert any(m["task_id"] == tid for m in msgs)
