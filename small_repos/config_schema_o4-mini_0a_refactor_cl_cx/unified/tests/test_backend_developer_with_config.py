import json
from configschema import with_config

def test_with_config_function(tmp_path):
    # prepare config file
    data = {"db": {"host": "localhost"}}
    p = tmp_path / "conf.json"
    p.write_text(json.dumps(data))
    @with_config(str(p))
    def fn(db):
        return db["host"]
    assert fn() == "localhost"

def test_with_config_method(tmp_path):
    # prepare config file
    data = {"s": 5}
    p = tmp_path / "conf.json"
    p.write_text(json.dumps(data))
    class A:
        @with_config(str(p))
        def get(self, s):
            return s
    a = A()
    assert a.get() == 5
