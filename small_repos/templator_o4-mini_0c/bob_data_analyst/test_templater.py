import pytest
import datetime
from templater import TemplateEngine
from jinja2 import DictLoader

@pytest.fixture
def engine():
    templates = {
        "simple.txt": "Sum: {{ [1,2,3]|add }}; Diff: {{ 10|sub(3) }}; Prod: {{ 2|mul(5) }}; Div: {{ 10|div(2) }}",
        "odd_even.txt": "{% for i in range(5) %}{{ i }} is {% if i is even %}even{% else %}odd{% endif %}; {% endfor %}",
        "dates.txt": "{{ dt|date('%Y') }}-{{ ts|strftime('%m') }}; {{ dt|timeago(now) }}",
        "json_yaml.txt": "{{ data|to_json }}|{{ jsonstr|from_json().key }}; {{ ydata|to_yaml }}|{{ ymlstr|from_yaml().foo }}",
        "stream.txt": "{% for i in items %}{{ i }},{% endfor %}",
        "base.html": "<html><head><title>{% block title %}Base{% endblock %}</title></head>{% block body %}Body{% endblock %}</html>",
        "child.html": "{% extends 'base.html' %}{% block title %}Child{% endblock %}{% block body %}{{ content }}{% endblock %}",
        "cond.txt": "{% if count < 2 %}small{% elif count < 5 %}medium{% else %}large{% endif %}",
        "loop.txt": "{% for item in list %}- {{ item }}\n{% endfor %}",
    }
    loader = DictLoader(templates)
    return TemplateEngine(loader=loader, auto_reload=True)

def test_basic_math(engine):
    out = engine.render("simple.txt")
    assert "Sum: 6" in out
    assert "Diff: 7" in out
    assert "Prod: 10" in out
    assert "Div: 5.0" in out

def test_odd_even(engine):
    out = engine.render("odd_even.txt")
    assert "0 is even" in out
    assert "1 is odd" in out
    assert out.count("even") == 3
    assert out.count("odd") == 2

def test_date_time(engine):
    dt = datetime.datetime(2020,1,1,12,0,0)
    ts = datetime.datetime(2020,1,1,0,0,0).timestamp()
    now = datetime.datetime(2020,1,1,12,0,10)
    out = engine.render("dates.txt", {"dt": dt, "ts": ts, "now": now})
    assert out.startswith("2020-01;01")
    assert "10 seconds ago" in out

def test_json_yaml(engine):
    data = {"key": "value"}
    jsonstr = '{"key":"value"}'
    ydata = {"foo": 123}
    ymlstr = "foo: 123\n"
    out = engine.render("json_yaml.txt", {"data": data, "jsonstr": jsonstr, "ydata": ydata, "ymlstr": ymlstr})
    assert '{"key": "value"}' in out
    assert 'value' in out
    assert 'foo: 123' in out
    assert '123' in out

def test_stream(engine):
    items = list(range(100))
    chunks = list(engine.render_stream("stream.txt", {"items": items}, chunk_size=50))
    joined = "".join(chunks)
    assert joined.startswith("0,1,2,")
    assert joined.endswith("99,")

def test_extends_block(engine):
    out = engine.render("child.html", {"content": "Hello"})
    assert "<title>Child</title>" in out
    assert "Hello" in out
    assert "Base" not in out

@pytest.mark.parametrize("count,expected", [(1,"small"),(3,"medium"),(5,"large")])
def test_conditional(engine, count, expected):
    out = engine.render("cond.txt", {"count": count})
    assert out == expected

def test_loop(engine):
    out = engine.render("loop.txt", {"list": ["a","b","c"]})
    assert "- a" in out and "- b" in out and "- c" in out

def test_syntax_highlight_good(engine):
    assert engine.syntax_highlight("Hello {{ name }}") is None

def test_syntax_highlight_bad(engine):
    msg = engine.syntax_highlight("Hello {{ name ")
    assert "Syntax Error" in msg

def test_cache_template(engine):
    # calling twice should not raise
    engine.cache_template("simple.txt")
    engine.cache_template("simple.txt")

def test_trans_gettext(engine):
    tmpl = engine.render("simple.txt")
    # trans/gettext are no-ops; ensure they exist
    assert engine.env.globals['trans']("test") == "test"
    assert engine.env.globals['gettext']("test") == "test"
