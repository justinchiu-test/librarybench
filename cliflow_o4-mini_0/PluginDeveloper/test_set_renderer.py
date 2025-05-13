import pytest
from plugin_framework.decorators import set_renderer
from plugin_framework.registry import renderers

def test_set_renderer():
    @set_renderer('json')
    def render_json(data):
        return '{"ok": true}'
    assert 'json' in renderers
    assert renderers['json'] is render_json
