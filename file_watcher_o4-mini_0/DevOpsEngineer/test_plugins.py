import pytest
from file_watcher.core import JenkinsPlugin, GitHubActionsPlugin, GitLabCIPlugin, Event

@pytest.mark.parametrize("plugin_cls", [JenkinsPlugin, GitHubActionsPlugin, GitLabCIPlugin])
def test_plugin_fire_non_dry(plugin_cls):
    plugin = plugin_cls()
    e = Event('p', 't')
    plugin.fire(e, dry_run=False)
    assert plugin.triggered == [e]

@pytest.mark.parametrize("plugin_cls", [JenkinsPlugin, GitHubActionsPlugin, GitLabCIPlugin])
def test_plugin_fire_dry(plugin_cls):
    plugin = plugin_cls()
    e = Event('p', 't')
    plugin.fire(e, dry_run=True)
    assert plugin.triggered == [('dry', e)]
