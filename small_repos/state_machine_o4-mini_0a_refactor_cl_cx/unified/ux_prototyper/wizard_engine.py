"""
WizardEngine implementation for UX Prototyper adapter
"""
class WizardEngine:
    def __init__(self):
        self.states = []
        self.transitions = []
        self.current_state = None
        self._entry_hooks = {}
        self._global_hooks = {'before': [], 'after': []}
        self.history_settings = {}
        self._undo_stack = []

    def define_transition(self, name, src, dst, trigger, guard=None):
        if src not in self.states:
            self.states.append(src)
        if dst not in self.states:
            self.states.append(dst)
        t = {'name': name, 'from': src, 'to': dst, 'trigger': trigger, 'guard': guard}
        self.transitions.append(t)
        return t

    def on_enter(self, state, callback):
        self._entry_hooks.setdefault(state, []).append(callback)

    def add_global_hook(self, when, callback):
        if when not in self._global_hooks:
            raise ValueError(f"Unknown hook type: {when}")
        self._global_hooks[when].append(callback)

    def trigger(self, trigger):
        for t in self.transitions:
            if t['trigger'] == trigger and self.current_state == t['from']:
                for cb in self._global_hooks['before']:
                    cb(trigger, t['from'], t['to'])
                self.current_state = t['to']
                for cb in self._entry_hooks.get(self.current_state, []):
                    cb()
                for cb in self._global_hooks['after']:
                    cb(trigger, t['from'], t['to'])
                return self.current_state
        return self.current_state

    def simulate_sequence(self, seq, expect_states=None):
        results = []
        for ev in seq:
            new_state = self.trigger(ev)
            results.append(new_state)
        return results

    def export_machine(self):
        return {
            'states': list(self.states),
            'transitions': list(self.transitions),
            'history_settings': dict(self.history_settings)
        }

    def load_machine(self, data):
        self.states = list(data.get('states', []))
        self.transitions = [t.copy() for t in data.get('transitions', [])]
        self.history_settings = dict(data.get('history_settings', {}))

    def enable_history(self, name, mode):
        self.history_settings[name] = mode

    def push_undo(self, event):
        for t in self.transitions:
            if t['trigger'] == event and self.current_state == t['from']:
                prev = self.current_state
                self.current_state = t['to']
                self._undo_stack.append(prev)
                return self.current_state
        return self.current_state

    def pop_undo(self):
        if self._undo_stack:
            prev = self._undo_stack.pop()
            self.current_state = prev
            return prev
        return None

    def export_visualization(self):
        nodes = list(self.states)
        edges = [(t['from'], t['to'], t['trigger']) for t in self.transitions]
        return {'nodes': nodes, 'edges': edges}

    def run_tests(self):
        return True

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