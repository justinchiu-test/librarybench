import json
from typing import Callable

class ProtocolMachine:
    def __init__(self):
        self.states = set()
        self.transitions = []
        self.guard_compositions = []
        self.on_enter_hooks = {}
        self.global_hooks = {'before': [], 'after': []}
        self.history = {}
        self.undo_stack = []
        self.redo_stack = []
        self.current_state = None

    def define_transition(self, name, from_state, to_state, action: Callable):
        self.states.add(from_state)
        self.states.add(to_state)
        self.transitions.append({
            'name': name,
            'from': from_state,
            'to': to_state,
            'action': action.__name__
        })
        if self.current_state is None:
            self.current_state = from_state

    def compose_guards(self, fn1, fn2, operator='AND'):
        comp = {
            'guards': [fn1.__name__, fn2.__name__],
            'operator': operator
        }
        self.guard_compositions.append(comp)
        return comp

    def on_enter(self, state, action):
        self.on_enter_hooks.setdefault(state, []).append(action.__name__)

    def add_global_hook(self, timing, hook_fn):
        if timing not in self.global_hooks:
            self.global_hooks[timing] = []
        self.global_hooks[timing].append(hook_fn.__name__)

    def export_machine(self, fmt):
        if fmt != 'json':
            raise ValueError('Unsupported format')
        spec = {
            'states': list(self.states),
            'transitions': self.transitions,
            'guards': self.guard_compositions,
            'on_enter': self.on_enter_hooks,
            'global_hooks': self.global_hooks,
            'history': self.history
        }
        return json.dumps(spec)

    def load_machine(self, json_spec):
        data = json.loads(json_spec)
        self.states = set(data.get('states', []))
        self.transitions = data.get('transitions', [])
        self.guard_compositions = data.get('guards', [])
        self.on_enter_hooks = data.get('on_enter', {})
        self.global_hooks = data.get('global_hooks', {})
        self.history = data.get('history', {})
        self.undo_stack = []
        self.redo_stack = []
        self.current_state = None

    def push_undo(self, event):
        self.undo_stack.append(event)

    def pop_redo(self):
        if self.undo_stack:
            event = self.undo_stack.pop()
            self.redo_stack.append(event)
            return event
        return None

    def export_visualization(self, fmt):
        if fmt != 'graphviz':
            raise ValueError('Unsupported format')
        lines = ['digraph G {']
        for t in self.transitions:
            lines.append(f'    "{t["from"]}" -> "{t["to"]}" [label="{t["name"]}"];')
        lines.append('}')
        return '\n'.join(lines)

    def simulate_sequence(self, event_list, expected=None):
        state = self.current_state
        for event in event_list:
            t = next((t for t in self.transitions if t['name'] == event and t['from'] == state), None)
            if not t:
                return False
            state = t['to']
        self.current_state = state
        if expected:
            return state == expected
        return True

    def enable_history(self, name, mode='shallow'):
        self.history[name] = mode

# Singleton
_machine = ProtocolMachine()

def define_transition(name, from_state, to_state, action):
    return _machine.define_transition(name, from_state, to_state, action)

def compose_guards(fn1, fn2, operator='AND'):
    return _machine.compose_guards(fn1, fn2, operator)

def on_enter(state, action):
    return _machine.on_enter(state, action)

def add_global_hook(timing, hook_fn):
    return _machine.add_global_hook(timing, hook_fn)

def export_machine(fmt):
    return _machine.export_machine(fmt)

def load_machine(json_spec):
    return _machine.load_machine(json_spec)

def push_undo(event):
    return _machine.push_undo(event)

def pop_redo():
    return _machine.pop_redo()

def export_visualization(fmt):
    return _machine.export_visualization(fmt)

def simulate_sequence(event_list, expected=None):
    return _machine.simulate_sequence(event_list, expected)

def enable_history(name, mode='shallow'):
    return _machine.enable_history(name, mode)

def run_tests():
    import pytest
    pytest.main([])
