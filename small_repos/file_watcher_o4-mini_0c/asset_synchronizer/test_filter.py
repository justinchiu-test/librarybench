import os
from sync_tool.filter import FilterRules

def write_gitignore(tmp_path, patterns):
    f = tmp_path / '.gitignore'
    f.write_text('\n'.join(patterns))
    return str(f)

def test_default_allows_nonhidden():
    fr = FilterRules()
    assert fr.is_allowed('file.jpg')
    assert not fr.is_allowed('.hidden')

def test_hidden_allowed_if_opted():
    fr = FilterRules(hidden=True)
    assert fr.is_allowed('.hidden')

def test_include_exclude():
    fr = FilterRules(include=['*.jpg'], exclude=['bad.jpg'])
    assert fr.is_allowed('good.jpg')
    assert not fr.is_allowed('good.png')
    assert not fr.is_allowed('bad.jpg')

def test_gitignore(tmp_path):
    git = write_gitignore(tmp_path, ['ignored.*', 'subdir/*'])
    fr = FilterRules(gitignore_path=git)
    assert fr.is_ignored_by_gitignore('ignored.txt')
    assert fr.is_ignored_by_gitignore(os.path.join('subdir','file.txt'))
    assert not fr.is_allowed('ignored.txt')
