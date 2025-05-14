from config_framework.argv_loader import ArgvLoader

def test_load():
    argv = ['--foo=bar', 'baz=qux', '--invalid', '--num=42']
    loader = ArgvLoader(argv)
    cfg = loader.load()
    assert cfg == {'foo': 'bar', 'baz': 'qux', 'num': '42'}
