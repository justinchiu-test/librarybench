import pytest
from template_engine import TemplateEngine
import json, yaml

def test_json_filters(tmp_path):
    tpl = tmp_path / "j.html"
    tpl.write_text("{{ data|to_json }}")
    engine = TemplateEngine(str(tmp_path))
    data = {"a": 1, "b": [2, 3]}
    out = engine.render("j.html", data=data)
    assert json.loads(out) == data

    tpl2 = tmp_path / "j2.html"
    tpl2.write_text("{% set x = data|to_json %}{{ x|from_json.a }}")
    out2 = engine.render("j2.html", data=data)
    assert out2.strip() == "1"

def test_yaml_filters(tmp_path):
    tpl = tmp_path / "y.html"
    tpl.write_text("{{ data|to_yaml }}")
    engine = TemplateEngine(str(tmp_path))
    data = {"x": "y", "nums": [1,2]}
    out = engine.render("y.html", data=data)
    assert yaml.safe_load(out) == data

    tpl2 = tmp_path / "y2.html"
    tpl2.write_text("{% set x = data|to_yaml %}{{ x|from_yaml.nums[1] }}")
    out2 = engine.render("y2.html", data=data)
    assert out2.strip() == "2"
