import subprocess
import sys
import shlex

def test_cli_help():
    out = subprocess.run([sys.executable, "cli.py", "--help"], capture_output=True, text=True)
    assert "Payment CLI" in out.stdout

def test_cli_test_transaction(tmp_path):
    # Run test_transaction command
    cmd = f"{sys.executable} cli.py test_transaction --tenant t1 --merchant m1 --customer c1 --amount 5 --type card"
    proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    assert "Transaction processed" in proc.stdout

def test_cli_queue_health():
    cmd = f"{sys.executable} cli.py queue_health"
    proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    assert "failed_tasks" in proc.stdout

def test_cli_replay_failed():
    cmd = f"{sys.executable} cli.py replay_failed"
    proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    assert "Replayed" in proc.stdout
