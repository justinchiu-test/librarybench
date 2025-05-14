import pytest
import datetime
import time
import json
try:
    import yaml
except ImportError:
    yaml = None

import docbuilder as db

def test_add_sub_mul():
    assert db.add(2, 3) == 5
    assert db.sub(5, 2) == 3
    assert db.mul("ab", 3) == "ababab"
    assert db.mul([1,2], 2) == [1,2,1,2]

def test_div_even():
    lst = list(range(10))
    parts = db.div(lst, 5)
    assert len(parts) == 5
    assert sum(len(p) for p in parts) == 10
    assert parts[0] == [0,1]
    assert parts[-1] == [8,9]

def test_div_uneven():
    lst = list(range(5))
    parts = db.div(lst, 3)
    assert [len(p) for p in parts] == [2,2,1]
    with pytest.raises(ValueError):
        db.div([1,2,3], 0)

def test_even_odd():
    assert db.is_even(2)
    assert not db.is_even(3)
    assert db.is_odd(3)
    assert not db.is_odd(4)

def test_date_and_strftime():
    fmt = "%Y-%m-%d"
    d = db.date(fmt)
    assert isinstance(d, str)
    dt = datetime.datetime(2020,1,2,3,4,5)
    assert db.strftime(dt, fmt) == "2020-01-02"
    with pytest.raises(TypeError):
        db.strftime("not dt", fmt)

def test_timeago_just_now_and_minutes_hours():
    now = datetime.datetime.now()
    assert db.timeago(now, now) == "just now"
    ten_mins_ago = now - datetime.timedelta(minutes=10)
    assert db.timeago(ten_mins_ago, now) == "10 minutes ago"
    two_hours_ago = now - datetime.timedelta(hours=2)
    assert db.timeago(two_hours_ago, now) == "2 hours ago"

def test_timeago_days():
    now = datetime.datetime.now()
    one_day = now - datetime.timedelta(days=1)
    assert db.timeago(one_day, now) == "1 day ago"
    five_days = now - datetime.timedelta(days=5)
    assert db.timeago(five_days, now) == "5 days ago"
    future = now + datetime.timedelta(days=3)
    assert db.timeago(future, now) == "in 3 days"
    with pytest.raises(TypeError):
        db.timeago("not dt")

def test_json_roundtrip():
    obj = {"a":1, "b":[2,3]}
    s = db.to_json(obj)
    assert isinstance(s, str)
    obj2 = db.from_json(s)
    assert obj2 == obj

def test_yaml_roundtrip():
    if yaml is None:
        pytest.skip("yaml not installed")
    obj = {"x": 10, "y": [1,2,3]}
    s = db.to_yaml(obj)
    obj2 = db.from_yaml(s)
    assert obj2 == obj

def test_render_stream():
    gen = db.render_stream([1,2,3])
    assert list(gen) == [1,2,3]
    # test generator nature
    gen2 = db.render_stream((i*i for i in range(3)))
    assert list(gen2) == [0,1,4]

def test_extends_and_block():
    assert db.extends("base.html") == "<extends base.html>"
    assert db.block("content", "Hello") == "<block content>Hello</block>"

def test_cache_template():
    calls = []
    @db.cache_template
    def f(x, y):
        calls.append((x,y))
        return x+y
    assert f(1,2) == 3
    assert f(1,2) == 3
    assert calls == [(1,2)]  # only one call due to cache

def test_trans_gettext():
    # Without actual .mo files, gettext returns same string
    s = "Hello"
    assert db.trans(s) == s
    assert db.gettext(s) == s

def test_auto_reload_and_syntax_highlight():
    @db.auto_reload
    def foo():
        return "bar"
    assert hasattr(foo, "auto_reload") and foo.auto_reload
    highlighted = db.syntax_highlight("code", "py")
    assert "<pre" in highlighted and "code" in highlighted and "py" in highlighted
