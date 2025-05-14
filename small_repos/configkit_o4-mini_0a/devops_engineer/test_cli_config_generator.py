from config_framework.cli_config_generator import CLIConfigGenerator

def test_generate():
    schema = {'timeout': 30, 'feature_gate': True}
    gen = CLIConfigGenerator(schema)
    opts = gen.generate()
    assert '--timeout=<value>' in opts
    assert '--feature_gate=<value>' in opts
    assert len(opts) == 2
