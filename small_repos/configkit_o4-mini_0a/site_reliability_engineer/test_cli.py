import pytest
from srectl.cli import CLIConfigGenerator

def test_cli_config_generator():
    config = {'a': {'b': 1}, 'c': 2}
    gen = CLIConfigGenerator(config)
    parser = gen.get_parser()
    args = parser.parse_args(['--a.b', '5', '--c', '10'])
    assert hasattr(args, 'a_b')
    assert args.a_b == '5'
    assert args.c == '10'
