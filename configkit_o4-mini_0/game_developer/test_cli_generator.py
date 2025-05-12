from config.cli import CLIConfigGenerator

def test_cli_generator():
    cfg = {
        'graphics': {'shadow': 'high'},
        'level': 3
    }
    cmds = CLIConfigGenerator.generate(cfg)
    assert "gamectl set graphics.shadow high" in cmds
    assert "gamectl set level 3" in cmds
