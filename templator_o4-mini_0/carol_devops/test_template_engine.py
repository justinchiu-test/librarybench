import os
import tempfile
import datetime
import json
import yaml
import pytest
from templating.engine import TemplateEngine

# Setup a temporary templates directory with provided templates
@pytest.fixture(scope="module")
def tmpl_dir(tmp_path_factory):
    # Copy the templates directory structure
    base_dir = tmp_path_factory.mktemp("templates")
    src = os.path.join(os.path.dirname(__file__), 'templates')
    # In this test environment, use the installed package's templates
    # Assume they're next to engine.py
    pkg_dir = os.path.join(os.path.dirname(__file__), 'templating', 'engine.py')
    # Instead, use the real templates folder from the repo
    # Here, we manually create templates in base_dir based on known names
    names = ["base.html", "child.html", "logs.html",
             "json_template.html", "yaml_template.html",
             "date_template.html", "timeago_template.html", "strftime_template.html"]
    src_dir = os.path.join(os.path.dirname(__file__), 'templates')
    # Copy from repo templates
    for name in names:
        with open(os.path.join('templates', name), 'r') as fsrc:
            dest = base_dir / name
            dest.write_text(fsrc.read())
    return str(base_dir)

def test_arithmetic_filters(tmpl_dir):
    eng = TemplateEngine(tmpl_dir)
    tmpl = '{{ 5|add(3) }} {{ 10|sub(4) }} {{ 2|mul(4) }} {{ 8|div(2) }}'
    # Create a temporary template
    path = os.path.join(tmpl_dir, 'arith.html')
    with open(path, 'w') as f:
        f.write(tmpl)
    out = eng.render('arith.html')
    assert out.strip() == '8 6 8 4.0'

def test_even_odd_filters(tmpl_dir):
    eng = TemplateEngine(tmpl_dir)
    tmpl = '{% if 3|is_odd %}odd{% else %}even{% endif %} {% if 4|is_even %}even{% else %}odd{% endif %}'
    path = os.path.join(tmpl_dir, 'eo.html')
    with open(path, 'w') as f:
        f.write(tmpl)
    out = eng.render('eo.html')
    assert out.strip() == 'odd even'

def test_date_and_strftime_filters(tmpl_dir):
    eng = TemplateEngine(tmpl_dir)
    now = datetime.datetime.now()
    # date template
    path = os.path.join(tmpl_dir, 'date_template.html')
    out = eng.render('date_template.html')
    assert str(now.year) in out
    # strftime template
    path2 = os.path.join(tmpl_dir, 'strftime_template.html')
    # supply dt in context
    dt = datetime.datetime(2020,1,2)
    out2 = eng.render('strftime_template.html', {'dt': dt})
    assert '2020-01-02' in out2

def test_timeago_filter(tmpl_dir):
    eng = TemplateEngine(tmpl_dir)
    dt = datetime.datetime.now() - datetime.timedelta(minutes=5)
    path = os.path.join(tmpl_dir, 'timeago_template.html')
    out = eng.render('timeago_template.html', {'dt': dt})
    assert 'minutes ago' in out

def test_json_yaml_filters(tmpl_dir):
    eng = TemplateEngine(tmpl_dir)
    data = {'a': 1, 'b': [2,3]}
    # JSON
    path = os.path.join(tmpl_dir, 'json_template.html')
    out = eng.render('json_template.html', {'data': data})
    loaded = json.loads(out)
    assert loaded == data
    # YAML
    path2 = os.path.join(tmpl_dir, 'yaml_template.html')
    out2 = eng.render('yaml_template.html', {'data': data})
    loaded2 = yaml.safe_load(out2)
    assert loaded2 == data

def test_template_inheritance_and_trans(tmpl_dir):
    eng = TemplateEngine(tmpl_dir)
    out = eng.render('child.html', {'uptime': 99.9})
    assert '<title>Service Status</title>' in out
    assert 'Uptime: 99.9%' in out

def test_render_stream(tmpl_dir):
    eng = TemplateEngine(tmpl_dir)
    lines = ['one', 'two', 'three']
    path = os.path.join(tmpl_dir, 'logs.html')
    chunks = list(eng.render_stream('logs.html', {'lines': lines}, chunk_size=10))
    combined = ''.join(chunks)
    # should contain EVEN and ODD markers
    assert 'EVEN: one' in combined
    assert 'ODD: two' in combined

def test_cache_and_auto_reload_flags(tmp_path):
    # production mode
    eng_prod = TemplateEngine('.', production=True)
    assert eng_prod.env.bytecode_cache is not None
    assert eng_prod.env.auto_reload == False
    # staging mode
    eng_stg = TemplateEngine('.', production=False)
    assert eng_stg.env.bytecode_cache is None
    assert eng_stg.env.auto_reload == True

def test_syntax_highlight_filter():
    eng = TemplateEngine('.')
    code = 'def foo():\n    return 1'
    highlighted = eng.env.filters['syntax_highlight'](code)
    assert isinstance(highlighted, str)
    assert 'def foo' in highlighted

def test_div_zero(tmpl_dir):
    eng = TemplateEngine(tmpl_dir)
    tmpl = '{{ 1|div(0) }}'
    path = os.path.join(tmpl_dir, 'div0.html')
    with open(path, 'w') as f:
        f.write(tmpl)
    out = eng.render('div0.html').strip()
    assert out == ''
