import tempfile
from watcher.gitignore_parser import GitignoreFilter

def test_gitignore(tmp_path):
    gi = tmp_path / ".gitignore"
    gi.write_text("# comment\n*.log\nbuild/\n")
    gf = GitignoreFilter(str(gi))
    assert gf.ignores("error.log")
    assert gf.ignores("build/main.o")
    assert not gf.ignores("src/file.py")
