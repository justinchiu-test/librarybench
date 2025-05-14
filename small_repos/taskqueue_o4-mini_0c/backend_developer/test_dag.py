from background_dispatcher import Dispatcher

def test_dag_visualization():
    dsp = Dispatcher()
    deps = {'A': ['B', 'C'], 'B': ['D']}
    dot = dsp.dag_visualization(deps)
    # check starts with digraph
    assert dot.startswith('digraph G')
    assert 'A->B' in dot and 'A->C' in dot and 'B->D' in dot
