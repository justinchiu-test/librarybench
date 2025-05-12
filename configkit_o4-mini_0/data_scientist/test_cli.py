from config.cli import generate_cli

def test_generate_cli():
    schema = {'lr':0.01, 'epochs':10, 'name':'exp'}
    parser = generate_cli(schema)
    args = parser.parse_args([])
    assert args.lr == 0.01
    assert args.epochs == 10
    assert args.name == 'exp'
    args2 = parser.parse_args(['--lr','0.02','--epochs','20','--name','test'])
    assert args2.lr == 0.02
    assert args2.epochs == 20
    assert args2.name == 'test'
