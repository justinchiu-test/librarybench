import sys
import fsm.cli as cli

def run_args(args):
    old = sys.argv
    sys.argv = ['prog'] + args
    try:
        from io import StringIO
        import sys as _sys
        buf = StringIO()
        _sys_stdout = _sys.stdout
        _sys.stdout = buf
        cli.cli()
        _sys.stdout = _sys_stdout
        return buf.getvalue()
    finally:
        sys.argv = old

def test_build():
    out = run_args(['build', 'wf1'])
    assert 'Building workflow wf1' in out

def test_simulate():
    out = run_args(['simulate', 'wf2'])
    assert 'Simulating workflow wf2' in out

def test_visualize():
    out = run_args(['visualize', 'wf3'])
    assert 'Visualizing workflow wf3' in out
