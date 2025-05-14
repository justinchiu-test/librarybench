from config.loaders import ArgvLoader

def test_argv_loader():
    loader = ArgvLoader(['--level=2', '--difficulty=hard', '--unusedflag'])
    cfg = loader.load()
    assert cfg['level'] == '2'
    assert cfg['difficulty'] == 'hard'
    assert 'unusedflag' not in cfg
