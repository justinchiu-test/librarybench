from config_manager.visualization import ConfigVisualization

def test_visual_tree():
    data = {"x": {"y": {"z": 0}}, "m": 1}
    viz = ConfigVisualization(data).render()
    lines = viz.splitlines()
    assert "x" in lines
    assert "  y" in lines
    assert "    z" in lines
    assert "m" in lines
