from datapipeline_cli.help_formatter import format_help

def test_format_help_md():
    hd = {'cmd': 'desc'}
    out = format_help(hd, mode='md')
    assert '### `cmd`' in out
    assert 'desc' in out

def test_format_help_color():
    hd = {'cmd': 'desc'}
    out = format_help(hd, mode='color')
    assert '\033[94mcmd\033[0m' in out
    assert 'desc' in out

def test_format_help_invalid():
    from pytest import raises
    with raises(ValueError):
        format_help({}, mode='unknown')
