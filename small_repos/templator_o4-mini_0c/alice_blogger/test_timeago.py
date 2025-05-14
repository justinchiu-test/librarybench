from datetime import datetime, timedelta
import re
import pytest
from template_engine import TemplateEngine

def test_timeago_filter(tmp_path):
    tpl = tmp_path / "t.html"
    tpl.write_text("{{ ts|timeago }}")
    engine = TemplateEngine(str(tmp_path))
    past = datetime.utcnow() - timedelta(hours=3, minutes=15)
    out = engine.render("t.html", ts=past)
    assert re.match(r"3 hours ago", out)

def test_date_strftime_filters(tmp_path):
    tpl = tmp_path / "d.html"
    tpl.write_text("{{ dt|date('%Y') }}-{{ dt|strftime('%m') }}")
    engine = TemplateEngine(str(tmp_path))
    now = datetime(2020, 5, 17, 12, 0)
    out = engine.render("d.html", dt=now)
    assert out == "2020-05"
