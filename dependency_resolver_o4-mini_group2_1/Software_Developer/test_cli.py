import os
import sys
import json
import tempfile
import subprocess
import pytest

# Point to our local cli.py
CLI = [sys.executable, os.path.abspath("cli.py")]

def run(args, input=None):
    proc = subprocess.run(CLI + args, capture_output=True, text=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr

def test_env_commands(tmp_path):
    # use a fresh env directory
    envs = tmp_path / "envs"
    cfg = tmp_path / "e.json"
    json.dump({"name":"env1"}, open(cfg, "w"))
    # monkeypatch cwd by running in tmp_path
    cwd = os.getcwd()
    os.chdir(str(tmp_path))
    try:
        # import
        code, out, err = run(["env", "import", str(cfg)])
        assert code==0
        assert out=="env1"
        # list
        code, out, err = run(["env","list"])
        assert code==0
        arr = json.loads(out)
        assert arr==["env1"]
        # delete
        code, out, err = run(["env","delete","env1"])
        assert code==0
        # list again
        code, out, err = run(["env","list"])
        assert json.loads(out)==[]
    finally:
        os.chdir(cwd)

def test_repo_and_solve(tmp_path):
    cwd = os.getcwd()
    os.chdir(str(tmp_path))
    try:
        # add repo
        packages = {"x":["1.0","2.0"],"y":["0.5"]}
        code,out,err = run(["repo","add","myr",json.dumps(packages)])
        assert code==0
        # list repo
        code,out,err = run(["repo","list"])
        assert code==0
        listed = json.loads(out)
        assert "myr" in listed and listed["myr"]==packages
        # solve constraints
        constraints = {"x":">=1.5","y":"==0.5"}
        code,out,err = run(["solve", json.dumps(constraints)])
        assert code==0
        sol = json.loads(out)
        assert sol=={"x":"2.0","y":"0.5"}
    finally:
        os.chdir(cwd)
