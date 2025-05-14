import pytest
from template_engine import TemplateEngine

def test_trans_tag(tmp_path):
    tpl = tmp_path / "trans.html"
    tpl.write_text("{% trans %}Hello World{% endtrans %}")
    engine = TemplateEngine(str(tmp_path))
    out = engine.render("trans.html")
    assert "Hello World" in out
