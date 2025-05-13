import pytest
import signal
import argparse
from plugin_developer.plugin import (
    register_subcommands, get_subcommands,
    parse_config,
    configure_prompt,
    install_signal_handlers, unregister_signal_handlers,
    register_plugin_hooks, run_hooks,
    collect_telemetry, record_event, get_events, clear_events,
    register_aliases, get_alias,
    cache_helper,
    inject_common_flags,
    autobuild_parser
)

def test_register_subcommands():
    # Clean state
    assert get_subcommands('ns_x') == []
    register_subcommands('ns1', [('cmd1', ['--opt'])])
    register_subcommands('ns1', [('cmd2', [])])
    assert get_subcommands('ns1') == [('cmd1', ['--opt']), ('cmd2', [])]
    assert get_subcommands('ns2') == []

def test_parse_config_merge_and_custom_tag():
    base = {'a': 1, 'nested': {'x': 10}}
    override = {'a': 2, 'nested': {'y': 20}, 's': '!upper hello'}
    result = parse_config(base, override)
    assert result['a'] == 2
    assert result['nested']['x'] == 10
    assert result['nested']['y'] == 20
    assert result['s'] == 'HELLO'

def test_configure_prompt():
    default = configure_prompt('default')
    assert default == {'color': 'blue', 'layout': 'simple'}
    fancy = configure_prompt('fancy')
    assert fancy == {'color': 'magenta', 'layout': 'rich'}
    unknown = configure_prompt('nope')
    assert unknown == default

def test_signal_handlers(monkeypatch):
    calls = []
    def teardown(signum):
        calls.append(signum)
    handlers = install_signal_handlers(teardown)
    # Simulate SIGINT
    h = signal.getsignal(signal.SIGINT)
    h(2, None)
    assert calls == [2]
    unregister_signal_handlers()
    # Ensure handlers cleared
    assert handlers

def test_plugin_hooks_and_invalid():
    def pre(cmd):
        return f"pre {cmd}"
    def post(cmd):
        return f"post {cmd}"
    register_plugin_hooks('pre_execute', 'cmd', pre)
    register_plugin_hooks('post_execute', 'cmd', post)
    assert run_hooks('pre_execute', 'cmd', 'cmd') == ['pre cmd']
    assert run_hooks('post_execute', 'cmd', 'cmd') == ['post cmd']
    with pytest.raises(ValueError):
        register_plugin_hooks('invalid', 'cmd', lambda x: x)

def test_telemetry_collection():
    clear_events()
    collect_telemetry(opt_in=False)
    record_event('e1')
    assert get_events() == []
    collect_telemetry(opt_in=True)
    record_event('e2')
    record_event('e3')
    assert get_events() == ['e2', 'e3']
    clear_events()
    assert get_events() == []

def test_alias_registration():
    # Clean alias state
    assert get_alias('alias_x') is None
    register_aliases('ls', 'list')
    assert get_alias('ls') == 'list'
    with pytest.raises(ValueError):
        register_aliases('ls', 'other')

def test_cache_helper_decorator():
    calls = []
    @cache_helper
    def f(x, y):
        calls.append((x, y))
        return x + y
    assert f(1, 2) == 3
    assert f(1, 2) == 3
    assert calls == [(1, 2)]

def test_inject_common_flags_and_parsing():
    parser = argparse.ArgumentParser(add_help=False)
    parser = inject_common_flags(parser)
    args = parser.parse_args(['--version', '-vv', '--quiet'])
    assert args.version is True
    assert args.verbose == 2
    assert args.quiet is True

def test_autobuild_parser_parsing():
    flags = [
        {'args': ['--opt'], 'kwargs': {'type': int, 'default': 5, 'help': 'an opt'}},
        {'args': ['-m', '--mode'], 'kwargs': {'choices': ['a', 'b'], 'default': 'a'}}
    ]
    parser = autobuild_parser(flags)
    args = parser.parse_args(['--opt', '10', '--mode', 'b'])
    assert args.opt == 10
    assert args.mode == 'b'
