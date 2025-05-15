"""
Procedural state machine for Robotics Engineer adapter
"""
import sys
import types
import json
from . import yaml

# Internal state
TRANSITIONS = []
STATE = None
GLOBAL_HOOKS = {'before': [], 'after': []}
ENTRY_HOOKS = {}
UNDO_STACK = []
REDO_STACK = []
HISTORY_MODES = {}

# Expose a STATE_MACHINE for compatibility (import only)
STATE_MACHINE = types.SimpleNamespace(transitions=TRANSITIONS)

def reset_machine():
    global STATE, GLOBAL_HOOKS, ENTRY_HOOKS, UNDO_STACK, REDO_STACK, HISTORY_MODES
    TRANSITIONS.clear()
    STATE = None
    GLOBAL_HOOKS = {'before': [], 'after': []}
    ENTRY_HOOKS.clear()
    UNDO_STACK.clear()
    REDO_STACK.clear()
    HISTORY_MODES.clear()

def define_transition(name, src, dst, trigger):
    TRANSITIONS.append({'name': name, 'src': src, 'dst': dst, 'trigger': trigger})

def compose_guards(*args, operator=None):
    """
    Compose multiple guard functions with a logical operator.
    Can be called as compose_guards(g1, g2, operator='AND') or compose_guards(g1, g2, 'AND').
    """
    # Determine operator and guards list based on arguments
    if operator is None:
        if len(args) < 2:
            raise ValueError("Operator must be specified with at least one guard")
        *guards, operator = args
    else:
        guards = list(args)
    op = operator.upper()
    if op == 'AND':
        def guard_func(*gargs):
            return all(g(*gargs) for g in guards)
    elif op == 'OR':
        def guard_func(*gargs):
            return any(g(*gargs) for g in guards)
    elif op == 'NOT':
        if len(guards) != 1:
            raise ValueError("NOT operator requires exactly one guard")
        def guard_func(*gargs):
            return not guards[0](*gargs)
    else:
        raise ValueError(f"Unknown operator: {operator}")
    return guard_func

def on_enter(state, callback):
    ENTRY_HOOKS.setdefault(state, []).append(callback)

def add_global_hook(when, callback):
    if when not in GLOBAL_HOOKS:
        raise ValueError(f"Unknown hook type: {when}")
    GLOBAL_HOOKS[when].append(callback)

def export_machine():
    data = {}
    # collect states in order
    states = []
    for t in TRANSITIONS:
        if t['src'] not in states:
            states.append(t['src'])
        if t['dst'] not in states:
            states.append(t['dst'])
    data['states'] = states
    data['transitions'] = list(TRANSITIONS)
    data['current_state'] = STATE
    return yaml.dump(data)

def load_machine(yaml_str):
    data = yaml.safe_load(yaml_str)
    reset_machine()
    for t in data.get('transitions', []):
        define_transition(t.get('name'), t.get('src'), t.get('dst'), t.get('trigger'))
    # restore state
    global STATE
    STATE = data.get('current_state')

def push_undo(ev):
    UNDO_STACK.append(ev)

def pop_redo():
    return REDO_STACK.pop() if REDO_STACK else None

def get_undo_stack():
    return UNDO_STACK

def get_redo_stack():
    return REDO_STACK

def enable_history(name, mode):
    HISTORY_MODES[name] = mode
    return HISTORY_MODES

def get_history_modes():
    return HISTORY_MODES

def simulate_sequence(seq):
    global STATE
    for ev in seq:
        # find matching transition
        found = None
        for t in TRANSITIONS:
            if t['trigger'] == ev and t['src'] == STATE:
                found = t
                break
            if t['trigger'] == ev and t['src'] is None and STATE is None:
                found = t
                break
        if not found:
            raise Exception(f"No transition for event {ev}")
        # before hooks
        for cb in GLOBAL_HOOKS['before']:
            cb(ev, found['src'], found['dst'])
        # apply transition
        STATE = found['dst']
        # entry hooks
        for cb in ENTRY_HOOKS.get(STATE, []):
            cb(ev, STATE)
        # after hooks
        for cb in GLOBAL_HOOKS.get('after', []):
            cb(ev, found['src'], found['dst'])
    return STATE

def export_visualization(format="dot"):
    if format != "dot":
        raise ValueError("Unsupported format")
    lines = ["digraph {"]
    for t in TRANSITIONS:
        lines.append(f'    "{t["src"]}" -> "{t["dst"]}" [label="{t["trigger"]}"];')
    lines.append("}")
    return "\n".join(lines)

def set_initial(state):
    global STATE
    STATE = state

def cli():
    args = sys.argv
    if len(args) < 2:
        return
    cmd = args[1]
    if cmd == 'scaffold':
        if len(args) < 3:
            return
        tpl = args[2]
        print(f"# Template: {tpl}")
        data = {'template': tpl, 'states': [], 'transitions': []}
        # Output JSON mapping for compatibility
        print(json.dumps(data))
    elif cmd == 'run':
        if len(args) < 3:
            return
        path = args[2]
        # Load machine definition from file
        with open(path) as f:
            content = f.read()
        data = yaml.safe_load(content)
        # Reset internal machine and populate with loaded transitions
        reset_machine()
        for t in data.get('transitions', []):
            define_transition(t.get('name'), t.get('src'), t.get('dst'), t.get('trigger'))
        # Report loaded machine
        states = data.get('states', [])
        transitions = data.get('transitions', [])
        print(f"Machine loaded with {len(states)} states and {len(transitions)} transitions")