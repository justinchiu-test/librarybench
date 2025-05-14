import os
import sys
from filewatcher.cli import main as cli_main

def test_cli_simulate(tmp_path, capsys):
    cwd = os.getcwd()
    os.chdir(tmp_path)
    sys_argv = sys.argv
    sys.argv = ['prog','simulate','--type','created','--path','test.txt']
    try:
        cli_main()
    finally:
        sys.argv = sys_argv
        os.chdir(cwd)
    captured = capsys.readouterr()
    assert 'Event' in captured.out
