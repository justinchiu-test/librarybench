import pytest
from template_engine import TemplateEngine, add, sub, mul, div, is_even, is_odd

def test_add_sub_mul_div():
    assert add(2, 3) == 5
    assert sub(10, 4) == 6
    assert mul(3, 5) == 15
    assert div(14, 2) == 7

def test_is_even_odd():
    assert is_even(4) is True
    assert is_even(5) is False
    assert is_odd(5) is True
    assert is_odd(6) is False

def test_filters_in_template(tmp_path):
    tpl = tmp_path / "filt.html"
    tpl.write_text("Sum: {{ 2|add(3) }}, Even? {{ 4|is_even }}, Odd? {{ 5|is_odd }}")
    engine = TemplateEngine(str(tmp_path))
    out = engine.render("filt.html")
    assert "Sum: 5" in out
    assert "Even? True" in out
    assert "Odd? True" in out
