from scheduler.dag import visualize

def test_visualize_empty():
    dot = visualize([], [])
    assert 'digraph' in dot

def test_visualize_nodes_edges():
    nodes = ['a','b']
    edges = [('a','b')]
    dot = visualize(nodes, edges)
    assert '"a" -> "b"' in dot
    assert '"a";' in dot
