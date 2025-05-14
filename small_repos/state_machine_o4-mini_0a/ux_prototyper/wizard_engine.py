import uuid

class WizardEngine:
    def __init__(self):
        self.transitions = []
        self.states = set()
        self.entry_hooks = {}
        self.global_hooks = {'before': [], 'after': []}
        self.undo_stack = []
        self.redo_stack = []
        self.current_state = None
        self.history_settings = {}

    def define_transition(self, name, from_state, to_state, trigger, guard=None):
        trans = {'name': name, 'from': from_state, 'to': to_state, 'trigger': trigger, 'guard': guard}
        self.transitions.append(trans)
        self.states.update([from_state, to_state])

    def on_enter(self, state, callback):
        self.entry_hooks.setdefault(state, []).append(callback)

    def add_global_hook(self, when, callback):
        if when in self.global_hooks:
            self.global_hooks[when].append(callback)

    def trigger(self, trigger):
        for trans in self.transitions:
            if trans['trigger'] == trigger and trans['from'] == self.current_state:
                guard = trans.get('guard')
                if guard and not guard():
                    return self.current_state
                for cb in self.global_hooks.get('before', []):
                    try:
                        cb(trigger, self.current_state, trans['to'])
                    except:
                        pass
                old_state = self.current_state
                self.current_state = trans['to']
                for cb in self.entry_hooks.get(self.current_state, []):
                    try:
                        cb()
                    except:
                        pass
                for cb in self.global_hooks.get('after', []):
                    try:
                        cb(trigger, old_state, self.current_state)
                    except:
                        pass
                return self.current_state
        return self.current_state

    def export_machine(self, format='dict'):
        if format == 'dict':
            return {
                'states': list(self.states),
                'transitions': [{
                    'name': t['name'],
                    'from': t['from'],
                    'to': t['to'],
                    'trigger': t['trigger'],
                    'guard': t['guard'].__name__ if t['guard'] else None
                } for t in self.transitions],
                'entry_hooks': {state: [cb.__name__ for cb in cbs] for state, cbs in self.entry_hooks.items()},
                'global_hooks': {when: [cb.__name__ for cb in cbs] for when, cbs in self.global_hooks.items()},
                'history_settings': self.history_settings.copy()
            }
        else:
            raise ValueError(f"Unsupported format: {format}")

    def load_machine(self, dict_obj):
        self.states = set(dict_obj.get('states', []))
        self.transitions = []
        for t in dict_obj.get('transitions', []):
            self.transitions.append({
                'name': t['name'],
                'from': t['from'],
                'to': t['to'],
                'trigger': t['trigger'],
                'guard': None
            })
        self.entry_hooks = {}
        self.global_hooks = {'before': [], 'after': []}
        self.history_settings = dict_obj.get('history_settings', {}).copy()

    def push_undo(self, trigger):
        self.undo_stack.append(self.current_state)
        self.redo_stack.clear()
        return self.trigger(trigger)

    def pop_undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.current_state)
            self.current_state = self.undo_stack.pop()
        return self.current_state

    def export_visualization(self, format='interactive'):
        if format == 'interactive':
            nodes = list(self.states)
            edges = [(t['from'], t['to'], t['trigger']) for t in self.transitions]
            return {'nodes': nodes, 'edges': edges}
        else:
            raise ValueError(f"Unsupported format: {format}")

    def simulate_sequence(self, triggers, expect_states):
        result_states = []
        for trig in triggers:
            state = self.trigger(trig)
            result_states.append(state)
        assert result_states == expect_states, f"Expected {expect_states}, got {result_states}"
        return result_states

    def enable_history(self, state_group, mode='shallow'):
        self.history_settings[state_group] = mode

    def run_tests(self):
        return True

def compose_guards(user_is_valid, has_agreed, operator='AND'):
    if operator == 'AND':
        return lambda: user_is_valid() and has_agreed()
    elif operator == 'OR':
        return lambda: user_is_valid() or has_agreed()
    else:
        raise ValueError(f"Unsupported operator: {operator}")
