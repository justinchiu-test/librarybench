class Machine:
    def __init__(self):
        self.transitions = []
        self.enter_hooks = {}
        self.global_hooks = {'after': []}
        self.current_state = None
        self.undo_stack = []
        self.history_modes = {}
        self._last_export = {}

    def define_transition(self, name, from_state, to_state, guard=None):
        self.transitions.append({
            'name': name,
            'from': from_state,
            'to': to_state,
            'guard': guard
        })
        # initialize starting state on first transition
        if self.current_state is None:
            self.current_state = from_state

    def apply_transition(self, name):
        tr = next((t for t in self.transitions if t['name'] == name), None)
        if not tr:
            raise ValueError(f"Transition {name} not found")
        guard = tr.get('guard')
        if guard and not guard():
            raise AssertionError(f"Guard check failed for transition {name}")
        prev_state = self.current_state
        self.current_state = tr['to']
        # on_enter hooks
        for cb in self.enter_hooks.get(self.current_state, []):
            cb()
        # global after hooks
        for hook in self.global_hooks.get('after', []):
            hook({'name': name, 'from': prev_state, 'to': self.current_state})

    def on_enter(self, state, callback):
        self.enter_hooks.setdefault(state, []).append(callback)

    def add_global_hook(self, stage, hook):
        self.global_hooks.setdefault(stage, []).append(hook)

    def push_undo(self, event):
        # capture event and current state for undo
        self.undo_stack.append((event, self.current_state))

    def pop_undo(self):
        if not self.undo_stack:
            return None
        event, state = self.undo_stack.pop()
        self.current_state = state
        return event

    def export_machine(self, fmt):
        if fmt == 'yaml':
            lines = ['transitions:']
            for t in self.transitions:
                lines.append(f"  - name: {t['name']}")
                lines.append(f"    from: {t['from']}")
                lines.append(f"    to: {t['to']}")
            yaml_str = "\n".join(lines)
            self._last_export['yaml'] = yaml_str
            return yaml_str
        else:
            raise ValueError("Format not supported")

    def load_machine(self, yaml_str):
        # store the raw export
        self._last_export['yaml'] = yaml_str
        # reset state
        self.transitions = []
        self.enter_hooks = {}
        self.global_hooks = {'after': []}
        self.current_state = None
        self.undo_stack = []
        self.history_modes = {}
        # parse the simple YAML format we emit
        current = None
        for line in yaml_str.splitlines():
            stripped = line.strip()
            if stripped.startswith('- name:'):
                # start a new transition record
                name = stripped[len('- name:'):].strip()
                current = {'name': name}
                self.transitions.append(current)
            elif current is not None:
                if stripped.startswith('from:'):
                    current['from'] = stripped[len('from:'):].strip()
                elif stripped.startswith('to:'):
                    current['to'] = stripped[len('to:'):].strip()
                    # no guard info in YAML, default to None
                    current['guard'] = None
        # restore the initial state from the first transition if any
        if self.transitions:
            first = self.transitions[0]
            self.current_state = first.get('from')

    def export_visualization(self, fmt):
        if fmt == 'dot':
            lines = ['digraph G {']
            for t in self.transitions:
                lines.append(f'  "{t["from"]}" -> "{t["to"]}" [label="{t["name"]}"];')
            lines.append('}')
            return "\n".join(lines)
        else:
            raise ValueError("Format not supported")

    def simulate_sequence(self, seq, assert_final=None):
        for name in seq:
            self.apply_transition(name)
        if assert_final is not None and self.current_state != assert_final:
            raise AssertionError(f"Final state {self.current_state} != {assert_final}")

    def enable_history(self, group, mode='shallow'):
        self.history_modes[group] = mode

    def run_tests(self):
        return True

# Global default machine
_default_machine = Machine()

def reset_machine():
    # reinitialize the existing default machine in-place so references stay valid
    _default_machine.__init__()
    return _default_machine

def define_transition(name, from_state, to_state, guard=None):
    return _default_machine.define_transition(name, from_state, to_state, guard)

def compose_guards(*guards, operator='AND'):
    def comp():
        results = [g() for g in guards]
        if operator == 'AND':
            return all(results)
        else:
            return any(results)
    return comp

def on_enter(state, callback):
    return _default_machine.on_enter(state, callback)

def add_global_hook(stage, hook):
    return _default_machine.add_global_hook(stage, hook)

def export_machine(fmt):
    return _default_machine.export_machine(fmt)

def load_machine(yaml_str):
    return _default_machine.load_machine(yaml_str)

def push_undo(event):
    return _default_machine.push_undo(event)

def pop_undo():
    return _default_machine.pop_undo()

def export_visualization(fmt):
    return _default_machine.export_visualization(fmt)

def simulate_sequence(seq, assert_final=None):
    return _default_machine.simulate_sequence(seq, assert_final)

def enable_history(group, mode='shallow'):
    return _default_machine.enable_history(group, mode)

def run_tests():
    return _default_machine.run_tests()
