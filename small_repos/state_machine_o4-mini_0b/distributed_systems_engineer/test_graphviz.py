from fsm.fsm import FSM
from fsm.graphviz import generate_dot

def test_generate_dot():
    fsm = FSM('s')
    fsm.add_transition('s', 'e', 't')
    dot = generate_dot(fsm)
    assert '"s" -> "t" [label="e"];' in dot
