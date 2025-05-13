import os
import tempfile
import time
import pytest
import yaml
from templating_engine import TemplateEngine, engine
from jinja2.exceptions import TemplateNotFound, SecurityError

def test_escape_shell():
    value = "foo; rm -rf /"
    escaped = engine.escape_shell(value)
    assert "'" in escaped
    assert "rm -rf" in escaped

def test_dot_lookup_success():
    ctx = {'services': {'web': {'port': 8080}}}
    assert engine.dot_lookup(ctx, 'services.web.port') == 8080

def test_dot_lookup_missing():
    ctx = {'a': {'b': 1}}
    with pytest.raises(KeyError):
        engine.dot_lookup(ctx, 'a.b.c')

def test_default_filter_none():
    tpl = TemplateEngine(searchpath='.').env.from_string("{{ none_val|default('xyz') }}")
    assert tpl.render(none_val=None) == 'xyz'

def test_default_filter_empty_string():
    tpl = TemplateEngine(searchpath='.').env.from_string("{{ ''|default('fallback') }}")
    assert tpl.render() == 'fallback'

def test_minify():
    content = """
    # comment line
    line1

    line2  # inline comment
    # another comment
    """
    minified = engine.minify(content)
    assert "line1" in minified
    assert "line2" in minified
    assert '#' not in minified.splitlines()[0]

def test_include(tmp_path):
    # create base and include templates
    base = tmp_path / "base.tpl"
    inc = tmp_path / "common.tpl"
    inc.write_text("Hello from include: {{ name }}")
    base.write_text("Start-{{ include('common.tpl') }}-End")
    eng = TemplateEngine(searchpath=str(tmp_path))
    result = eng.render("base.tpl", {'name': 'Alice'})
    assert "Hello from include: Alice" in result
    assert result.startswith("Start-")
    assert result.endswith("-End")

def test_cache_template_and_collision(tmp_path):
    tpl_file = tmp_path / "t.tpl"
    tpl_file.write_text("Value: {{ x }}")
    eng = TemplateEngine(searchpath=str(tmp_path))
    # first compile should create cache
    tpl1 = eng.cache_template("t.tpl")
    cache_dir = tmp_path / ".template_cache"
    assert cache_dir.exists()
    # change content and re-cache, different hash leads to new file
    tpl_file.write_text("Value: {{ y }}")
    tpl2 = eng.cache_template("t.tpl")
    # cached templates should be instances but not the same rendered result
    assert tpl1 is not tpl2
    rendered1 = tpl1.render(x=1)
    rendered2 = tpl2.render(y=2)
    assert "1" in rendered1
    assert "2" in rendered2

def test_render_stream():
    eng = TemplateEngine(searchpath='.')
    # create a temporary template in current dir
    name = "stream_test.tpl"
    with open(name, "w") as f:
        f.write("{% for i in range(3) %}{{ i }}-{% endfor %}")
    try:
        gen = eng.render_stream(name, {})
        out = ''.join(list(gen))
        assert out == "0-1-2-"
    finally:
        os.remove(name)

def test_add_filter(tmp_path):
    eng = TemplateEngine(searchpath=str(tmp_path))
    # write template that uses custom filter
    tpl = tmp_path / "f.tpl"
    tpl.write_text("{{ data|to_yaml }}")
    def to_yaml(val):
        return yaml.safe_dump(val).strip()
    eng.add_filter('to_yaml', to_yaml)
    result = eng.render("f.tpl", {'data': {'a': 1}})
    assert "a:" in result

def test_profile_render(tmp_path):
    tpl = tmp_path / "pr.tpl"
    tpl.write_text("Value: {{ v }}")
    eng = TemplateEngine(searchpath=str(tmp_path))
    pr = eng.profile_render("pr.tpl", {'v': 42})
    assert 'rendered' in pr and 'time' in pr
    assert pr['rendered'] == "Value: 42"
    assert isinstance(pr['time'], float)
    assert pr['time'] >= 0

def test_sandbox_mode_blocks_import():
    tpl = engine.env.from_string("{{ __import__('os').system('echo hacked') }}")
    result = tpl.render()
    # sandbox should prevent __import__, result should be empty or undefined
    assert result.strip() == ""

def test_template_not_found():
    eng = TemplateEngine(searchpath='.')
    with pytest.raises(TemplateNotFound):
        eng.render("nonexistent.tpl", {})
