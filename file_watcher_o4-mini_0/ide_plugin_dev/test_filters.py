from filewatcher.filters import FilterRules

def test_filter_no_rules():
    f = FilterRules()
    assert f.match('foo.txt')
    assert f.match('dir/bar')

def test_include_patterns():
    f = FilterRules()
    f.add_include('*.py')
    assert f.match('test.py')
    assert not f.match('test.txt')

def test_exclude_patterns():
    f = FilterRules()
    f.add_exclude('*.tmp')
    assert not f.match('foo.tmp')
    assert f.match('foo.txt')

def test_include_exclude():
    f = FilterRules()
    f.add_include('*.py')
    f.add_exclude('test_*.py')
    assert f.match('main.py')
    assert not f.match('test_main.py')
