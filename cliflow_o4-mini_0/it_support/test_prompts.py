import builtins
import getpass
from onboarding.prompting import prompt_interactive
from onboarding.secure_prompt import secure_prompt

def test_prompt_interactive(monkeypatch):
    inputs = iter(["Alice", "IT", "soft1, soft2", "key1, key2"])
    monkeypatch.setattr(builtins, 'input', lambda prompt='': next(inputs))
    res = prompt_interactive()
    assert res['name'] == "Alice"
    assert res['department'] == "IT"
    assert res['software'] == ["soft1", "soft2"]
    assert res['licenses'] == ["key1", "key2"]

def test_secure_prompt(monkeypatch):
    monkeypatch.setattr(getpass, 'getpass', lambda prompt='': "secret")
    val = secure_prompt("Enter pwd: ")
    assert val == "secret"
