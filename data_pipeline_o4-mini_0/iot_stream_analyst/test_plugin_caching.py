import pytest
from streamkit.plugin import PluginSystem
from streamkit.caching import CachingStage

def test_plugin_system():
    ps = PluginSystem()
    ps.register('echo', lambda x: x)
    assert ps.adapt('echo', 5) == 5
    with pytest.raises(KeyError):
        ps.adapt('none', 1)

def test_caching_stage():
    cs = CachingStage()
    cs.set('k1', {'val':1})
    rec = {'id': 'k1'}
    enriched = cs.enrich(rec.copy(), key_fn=lambda r: r['id'])
    assert enriched['meta'] == {'val':1}
    assert cs.get('k1') == {'val':1}
