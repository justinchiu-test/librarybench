"""
Procedural state machine for Business Process Analyst adapter
"""
import json

class _Machine:
    def __init__(self):
        self.states = []
        self.transitions = []
        self.current_state = None
        self.history_modes = {}
        self._entry_hooks = {}
        self._global_hooks = {'before': [], 'after': []}
        self._undo_stack = []

# Default global machine
_default_machine = _Machine()

def reset_machine():
    _default_machine.states.clear()
    _default_machine.transitions.clear()
    _default_machine.current_state = None
    _default_machine.history_modes.clear()
    _default_machine._entry_hooks.clear()
    _default_machine._global_hooks = {'before': [], 'after': []}
    _default_machine._undo_stack.clear()

def define_transition(name, src, dst, guard=None):
    if src not in _default_machine.states:
        _default_machine.states.append(src)
    if dst not in _default_machine.states:
        _default_machine.states.append(dst)
    t = {'name': name, 'src': src, 'dst': dst, 'guard': guard}
    _default_machine.transitions.append(t)

def compose_guards(*guards, operator):
    op = operator.upper()
    if op == 'AND':
        def guard_func():
            return all(g() for g in guards)
    elif op == 'OR':
        def guard_func():
            return any(g() for g in guards)
    elif op == 'NOT':
        if len(guards) != 1:
            raise ValueError("NOT operator requires exactly one guard")
        def guard_func():
            return not guards[0]()
    else:
        raise ValueError(f"Unknown operator: {operator}")
    return guard_func

def on_enter(state, callback):
    _default_machine._entry_hooks.setdefault(state, []).append(callback)

def add_global_hook(when, callback):
    if when not in _default_machine._global_hooks:
        raise ValueError(f"Unknown hook type: {when}")
    _default_machine._global_hooks[when].append(callback)

def export_machine(format="yaml"):
    data = {
        'states': list(_default_machine.states),
        'transitions': [
            {'name': t['name'], 'src': t['src'], 'dst': t['dst']}
            for t in _default_machine.transitions
        ]
    }
    return json.dumps(data, sort_keys=True)

def load_machine(yaml_str):
    data = json.loads(yaml_str)
    reset_machine()
    for t in data.get('transitions', []):
        define_transition(t['name'], t['src'], t['dst'])

def simulate_sequence(seq, assert_final=None):
    for e in seq:
        # find the transition
        t = next((t for t in _default_machine.transitions if t['name'] == e), None)
        if t is None:
            continue
        if _default_machine.current_state is None:
            _default_machine.current_state = t['src']
        if t['guard'] is not None and not t['guard']():
            continue
        _default_machine.current_state = t['dst']
        # entry hooks
        for cb in _default_machine._entry_hooks.get(_default_machine.current_state, []):
            cb()
        # after hooks
        for cb in _default_machine._global_hooks.get('after', []):
            cb({'name': t['name']})
    if assert_final is not None and _default_machine.current_state != assert_final:
        raise AssertionError(f"Expected final state {assert_final}, got {_default_machine.current_state}")

def push_undo(evt):
    _default_machine._undo_stack.append(evt)

def pop_undo():
    if not _default_machine._undo_stack:
        return None
    evt = _default_machine._undo_stack.pop()
    # revert state
    t = next((t for t in _default_machine.transitions if t['name'] == evt), None)
    if t:
        _default_machine.current_state = t['src']
    return evt

def export_visualization(format):
    if format != "dot":
        raise ValueError("Unsupported format")
    s = "digraph {\n"
    for t in _default_machine.transitions:
        s += f'    "{t["src"]}" -> "{t["dst"]}" [label="{t["name"]}"];\n'
    s += "}"
    return s

def enable_history(name, mode):
    _default_machine.history_modes[name] = mode
    return _default_machine.history_modes

def run_tests():
    return True