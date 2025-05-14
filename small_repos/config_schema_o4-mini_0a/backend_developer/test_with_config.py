from configmanager import ConfigManager, with_config
def test_with_config_function(tmp_path):
    # prepare config
    ConfigManager._config = {"db": {"host": "localhost"}}
    @with_config("db")
    def fn(db):
        return db["host"]
    assert fn() == "localhost"

def test_with_config_method(tmp_path):
    ConfigManager._config = {"s": 5}
    class A:
        @with_config("s")
        def get(self, s):
            return s
    a = A()
    assert a.get() == 5
