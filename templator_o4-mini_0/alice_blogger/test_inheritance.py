import pytest
from template_engine import TemplateEngine

def test_extends_and_block(tmp_path):
    base = tmp_path / "base.html"
    base.write_text("""<html><head><title>{% block title %}Base{% endblock %}</title></head>
<body>{% block content %}Base Content{% endblock %}</body></html>""")
    child = tmp_path / "child.html"
    child.write_text("""{% extends 'base.html' %}{% block title %}Child{% endblock %}
{% block content %}Hello {{ name }}{% endblock %}""")
    engine = TemplateEngine(str(tmp_path))
    out = engine.render("child.html", name="World")
    assert "<title>Child</title>" in out
    assert "Hello World" in out
