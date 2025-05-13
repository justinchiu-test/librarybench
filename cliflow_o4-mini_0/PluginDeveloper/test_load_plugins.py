import os
import tempfile
from plugin_framework.plugin_loader import load_plugins

def test_load_plugins(tmp_path):
    # create a plugin file
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    p = plugin_dir / "plugin1.py"
    p.write_text("def load():\n    return 'ok'")
    results = load_plugins(str(plugin_dir))
    assert 'plugin1' in results
    assert results['plugin1'] == 'ok'
