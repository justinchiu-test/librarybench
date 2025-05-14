import pytest
from template_engine import TemplateEngine
from jinja2 import TemplateSyntaxError

def test_syntax_highlight(tmp_path):
    tpl = tmp_path / "bad.html"
    tpl.write_text("{% if %}broken{% endif %}")
    engine = TemplateEngine(str(tmp_path))
    with pytest.raises(TemplateSyntaxError) as exc:
        engine.render("bad.html")
    msg = str(exc.value)
    assert "broken" not in msg
    assert ">>" in msg
