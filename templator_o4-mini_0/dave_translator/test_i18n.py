import pytest
import datetime
from i18n import (
    add, sub, mul, div,
    is_even, is_odd,
    date, strftime, timeago,
    to_json, from_json, to_yaml, from_yaml,
    render_stream,
    extends, block, cache_template, trans, gettext, auto_reload, syntax_highlight
)

def test_add_sub_mul_div():
    assert add(1, 2) == 3
    assert sub(5, 3) == 2
    assert mul(4, 2.5) == 10.0
    assert div(7, 2) == 3.5

def test_is_even_is_odd():
    assert is_even(2) is True
    assert is_even(3) is False
    assert is_odd(3) is True
    assert is_odd(4) is False

def test_date_and_strftime():
    dt = datetime.datetime(2000, 1, 2, 15, 30, 45)
    fmt = "%Y-%m-%d %H:%M:%S"
    assert date(fmt, dt) == "2000-01-02 15:30:45"
    assert strftime(fmt, dt) == "2000-01-02 15:30:45"

def test_timeago_seconds():
    now = datetime.datetime.now()
    past = now - datetime.timedelta(seconds=5)
    assert timeago(past, now) == "5 seconds ago"
    assert timeago(0.5, now) == "just now"

def test_timeago_minutes_hours():
    now = datetime.datetime.now()
    past_min = now - datetime.timedelta(minutes=2)
    past_hr = now - datetime.timedelta(hours=3)
    assert timeago(past_min, now) == "2 minutes ago"
    assert timeago(past_hr, now) == "3 hours ago"

def test_json_serialization():
    data = {"a": 1, "b": "text", "c": [1,2,3]}
    json_str = to_json(data)
    loaded = from_json(json_str)
    assert loaded == data

def test_yaml_serialization():
    data = {"a": 1, "b": "text", "c": {"d": 4}}
    yaml_str = to_yaml(data)
    # Expect lines for a, b, c and nested d
    expected_lines = ["a: 1", "b: text", "c:", "  d: 4"]
    for line in expected_lines:
        assert line in yaml_str.splitlines()
    parsed = from_yaml("a: 1\nb: text\nc: 4.5\ne: hello")
    assert parsed == {"a": 1, "b": "text", "c": 4.5, "e": "hello"}

def test_render_stream():
    data = [1,2,3]
    stream = render_stream(data)
    assert list(stream) == [1,2,3]

@pytest.mark.parametrize("func", [extends, block, cache_template, trans, gettext, auto_reload, syntax_highlight])
def test_stubs_raise_not_implemented(func):
    with pytest.raises(NotImplementedError):
        func()
