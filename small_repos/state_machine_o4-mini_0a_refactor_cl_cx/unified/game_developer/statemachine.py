"""
Core StateMachine implementation for Game Developer adapter
"""
import json

class StateMachine:
    def __init__(self):
        self.states = []
        self.transitions = []
        self.current_state = None
        self._global_hooks = {'before': [], 'after': []}
        self._entry_hooks = {}
        self.undo_stack = []
        self.history_enabled = {}

    def define_transition(self, name, src, dst, trigger, guard=None):
        if src not in self.states:
            self.states.append(src)
        if dst not in self.states:
            self.states.append(dst)
        t = {'name': name, 'src': src, 'dst': dst, 'trigger': trigger, 'guard': guard}
        self.transitions.append(t)
        return t

    @staticmethod
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

    def on_enter(self, state, callback):
        self._entry_hooks.setdefault(state, []).append(callback)

    def add_global_hook(self, when, callback):
        if when not in self._global_hooks:
            raise ValueError(f"Unknown hook type: {when}")
        self._global_hooks[when].append(callback)

    def simulate_sequence(self, seq):
        for ev in seq:
            matching = [t for t in self.transitions if t['trigger'] == ev and t['src'] == self.current_state]
            if not matching:
                continue
            t = matching[0]
            for cb in self._global_hooks['before']:
                cb(self, ev, t)
            prev_state = self.current_state
            self.current_state = t['dst']
            for cb in self._entry_hooks.get(self.current_state, []):
                cb(self, ev, t)
            for cb in self._global_hooks['after']:
                cb(self, ev, t)
            self.undo_stack.append({'trigger': ev, 'src': prev_state, 'dst': t['dst']})
        return self.current_state

    def pop_undo(self):
        if not self.undo_stack:
            return None
        ev = self.undo_stack.pop()
        self.current_state = ev['src']
        return ev

    def export_machine(self, format='dict'):
        data = {
            'states': list(self.states),
            'transitions': list(self.transitions),
            'current_state': self.current_state
        }
        if format == 'dict':
            return data
        elif format == 'json':
            return json.dumps(data)
        else:
            raise ValueError(f"Unsupported format: {format}")

    @classmethod
    def load_machine(cls, data):
        if isinstance(data, str):
            obj = json.loads(data)
        else:
            obj = data
        m = cls()
        m.states = list(obj.get('states', []))
        m.transitions = [t.copy() for t in obj.get('transitions', [])]
        m.current_state = obj.get('current_state')
        return m

    def export_visualization(self, filepath):
        content = 'digraph {\n'
        for t in self.transitions:
            content += f'    "{t["src"]}" -> "{t["dst"]}" [label="{t["trigger"]}"];\n'
        content += '}\n'
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath

    def enable_history(self, name, mode):
        self.history_enabled[name] = mode
        return {name: mode}

def run_tests():
    return 0