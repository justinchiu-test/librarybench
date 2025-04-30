import pytest
from automation.notifier import Notifier

def test_notifier_collects_messages():
    n = Notifier()
    assert n.notifications == []
    n.notify("Hello")
    n.notify("World")
    assert n.notifications == ["Hello", "World"]
