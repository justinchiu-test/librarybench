import os
import tempfile
import yaml
import pytest
from configsystem.yaml_loader import YAMLLoader
from configsystem.utils import DotNotationAccess, NestedMerge, VariableInterpolation
from configsystem.coercer import CustomCoercers
from configsystem.config import ConfigManager

def write_yaml(data):
    fd, path = tempfile.mkstemp(suffix='.yml')
    with os.fdopen(fd, 'w') as f:
        yaml.safe_dump(data, f)
    return path

def test_yaml_loader_and_dotnotation():
    data = {'a': {'b': {'c': 1}}}
    path = write_yaml(data)
    loaded = YAMLLoader.load(path)
    assert loaded == data
    assert DotNotationAccess.get(loaded, 'a.b.c') == 1
    assert DotNotationAccess.get(loaded, 'a.b.x', 'def') == 'def'
    DotNotationAccess.set(loaded, 'a.b.d', 2)
    assert loaded['a']['b']['d'] == 2

def test_nested_merge_and_conflict():
    a = {'x': 1, 'y': [1,2], 'z': {'u':1}}
    b = {'x': 2, 'y': [3], 'z': {'v':2}, 'w':3}
    conflicts = []
    m = NestedMerge.merge(a, b, conflicts)
    assert m['x'] == 2
    assert m['y'] == [1,2,3]
    assert m['z']['u'] == 1 and m['z']['v'] == 2
    assert m['w'] == 3
    assert 'x' in conflicts

def test_variable_interpolation_and_circular():
    cfg = {'a': 'Value', 'b': '${a} World', 'c': '${b}!'}
    interp = VariableInterpolation.interpolate(cfg)
    assert interp['b'] == 'Value World'
    assert interp['c'] == 'Value World!'
    cfg2 = {'x': '${y}', 'y': '${x}'}
    with pytest.raises(ValueError):
        VariableInterpolation.interpolate(cfg2)

def test_custom_coercers():
    cfg = {'spell': {'cooldown_s': '1.5', 'chance_pct': '30'}}
    def to_sec(v): return float(v)
    def to_frac(v): return float(v)/100
    cc = CustomCoercers()
    cc.register('_s', to_sec)
    cc.register('_pct', to_frac)
    cc.apply(cfg)
    assert isinstance(cfg['spell']['cooldown_s'], float)
    assert abs(cfg['spell']['chance_pct'] - 0.3) < 1e-6

def test_config_manager_basic():
    base = {
        'weapons': {'sword': {'damage': 10}},
        'profiles': {'dev': {'weapons': {'sword': {'damage': 5}}}}
    }
    mods = [
        {'weapons': {'sword': {'damage': 12}}},
        {'zones': {'ice': {'spawn_rate': 2}}}
    ]
    base_path = write_yaml(base)
    mod1 = write_yaml(mods[0])
    mod2 = write_yaml(mods[1])
    cm = ConfigManager()
    cm.load_base(base_path)
    cm.add_mod(mod1)
    cm.add_mod(mod2)
    # default profile
    assert cm.get('weapons.sword.damage') == 12
    cm.set_profile('dev')
    assert cm.get('weapons.sword.damage') == 12  # mod overrides profile
    # defaults
    cm.set_defaults({'zones': {'ice': {'ai_state': 'idle'}}})
    assert cm.get('zones.ice.ai_state') == 'idle'
    # coercers
    cm.register_coercer('_rate', lambda v: v*10)
    # apply coercer on spawn_rate
    val = cm.get('zones.ice.spawn_rate')
    assert val == 20
    # watch
    events = []
    cm.watch_path('weapons.sword.damage', lambda p,v: events.append((p,v)))
    cm.set('weapons.sword.damage', 7)
    assert events == [('weapons.sword.damage', 7)]
    # conflicts
    conf = cm.get_conflicts()
    assert 'weapons' in conf or 'sword' in conf

def test_visualization():
    cm = ConfigManager()
    cm.base = {'a': 1}
    cm.mods = [{'b': {'x':2}}]
    viz = cm.visualize()
    assert 'base' in viz and 'mod0' in viz
    assert 'a' in viz['base']
    assert 'b.x' in viz['mod0']
