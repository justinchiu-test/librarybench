import os
import tempfile
import importlib.util
import pytest
from static_site_engine import define_macro, call_macro, precompile_templates

def test_define_and_call_macro():
    define_macro("b", lambda s: f"<b>{s}</b>")
    out = call_macro("b", "text")
    assert out == "<b>text</b>"
    with pytest.raises(KeyError):
        call_macro("undefined")

def test_precompile_templates(tmp_path):
    tpl = "Value: {v}"
    out_file = tmp_path / "mod.py"
    precompile_templates(tpl, str(out_file))
    # load module
    spec = importlib.util.spec_from_file_location("mod", str(out_file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert hasattr(mod, "render")
    result = mod.render(v=123)
    assert result == "Value: 123"
