import pytest
import sys
import io
from cli_tools import *

def test_generate_completion():
    assert generate_completion("bash") == "complete -C 'cli' cli"
    assert "cli --help" in generate_completion("fish")
    assert generate_completion("unknown") == ""

def test_export_workflow_docs_md():
    wf = {"build": "Compile code", "test": "Run tests"}
    md = export_workflow_docs(wf, "md")
    assert "## build" in md
    assert "Compile code" in md

def test_export_workflow_docs_html():
    wf = {"deploy": "Send to prod"}
    html = export_workflow_docs(wf, "html")
    assert "<h2>deploy</h2>" in html
    assert "<p>Send to prod</p>" in html

def test_export_workflow_docs_invalid():
    with pytest.raises(ValueError):
        export_workflow_docs({}, "txt")

def test_discover_plugins():
    plugins = ["safe_plugin", "unsafe_plugin", "another"]
    cert = discover_plugins(plugins)
    assert "safe_plugin" in cert
    assert "another" in cert
    assert "unsafe_plugin" not in cert

def test_redirect_io():
    buf_out = io.StringIO()
    buf_err = io.StringIO()
    with redirect_io(stdout=buf_out, stderr=buf_err):
        print("hello")
        print("error", file=sys.stderr)
    assert buf_out.getvalue().strip() == "hello"
    assert buf_err.getvalue().strip() == "error"

def test_use_profile_default():
    dev = use_profile("dev")
    assert dev["debug"] is True
    assert dev["optimizations"] is False
    unknown = use_profile("none")
    assert unknown == {}

def test_use_profile_custom():
    profiles = {"custom": {"opt": 1}}
    assert use_profile("custom", profiles) == {"opt": 1}

def test_serialize_data_json():
    data = {"a":1}
    s = serialize_data(data, "json")
    assert '"a": 1' in s

def test_serialize_data_yaml():
    data = {"k":"v","x":10}
    y = serialize_data(data, "yaml")
    lines = y.splitlines()
    assert "k: v" in lines
    assert "x: 10" in lines

def test_serialize_data_yaml_invalid():
    with pytest.raises(ValueError):
        serialize_data([1,2,3], "yaml")

def test_serialize_data_csv():
    data = [{"a":1,"b":2}, {"a":3,"b":4}]
    csv_s = serialize_data(data, "csv")
    lines = csv_s.splitlines()
    assert lines[0] == "a,b"
    assert "1,2" in lines[1]
    assert "3,4" in lines[2]

def test_serialize_data_csv_invalid():
    with pytest.raises(ValueError):
        serialize_data("not", "csv")

def test_check_version():
    assert check_version("1.2.3", "1.2.0")
    assert not check_version("1.0.0", "1.0.1")

def test_manage_marketplace():
    plugins = [{"name":"p1","rating":5},{"name":"p2","rating":3}]
    sorted_p = manage_marketplace(plugins)
    assert sorted_p[0]["name"] == "p1"

def test_register_hooks():
    def f1(): pass
    def f2(): pass
    reg = register_hooks({"start":[f1], "end":[f2]})
    assert "start" in reg
    assert f1 in reg["start"]
    reg2 = register_hooks({"start":[f2]})
    assert f2 in reg2["start"]

def test_run_tests_all_pass():
    specs = [
        {"func": lambda x: x*2, "args":(2,), "expected":4},
        {"func": lambda x,y=1: x+y, "args":(2,), "kwargs":{"y":3}, "expected":5}
    ]
    res = run_tests(specs)
    assert res["passed"] == 2
    assert res["failed"] == 0

def test_run_tests_some_fail():
    specs = [
        {"func": lambda x: x+1, "args":(1,), "expected":3}
    ]
    res = run_tests(specs)
    assert res["passed"] == 0
    assert res["failed"] == 1
    assert res["details"][0]["got"] == 2
