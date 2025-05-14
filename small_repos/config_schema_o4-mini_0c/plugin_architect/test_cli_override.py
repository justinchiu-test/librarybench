import argparse
from config_manager.api import ConfigManager

def test_override_cli_args():
    cm = ConfigManager(defaults={"a":1, "b":2})
    cm.config = {"a": 10, "b": 20}
    parser = argparse.ArgumentParser()
    parser.add_argument("--a", type=int)
    parser.add_argument("--c", type=int)
    args = parser.parse_args(["--a", "5", "--c", "7"])
    cm.override_cli_args(args)
    assert cm.get("a") == 5
    assert cm.get("b") == 20
    assert cm.get("c") == 7
