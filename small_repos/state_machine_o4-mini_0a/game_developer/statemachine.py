import json
import os

class StateMachine:
    def __init__(self):
        self.states = set()
        self.transitions = []
        self.current_state = None
        self.on_enter_callbacks = {}
        self.global_hooks = {'before': [], 'after': []}
        self.undo_stack = []
        self.redo_stack = []
        self.history_enabled = {}

    def define_transition(self, name, src, dst, trigger, guards=None):
        if guards is None:
            guards = []
        self.states.add(src)
        self.states.add(dst)
        self.transitions.append({
            'name': name,
            'src': src,
            'dst': dst,
            'trigger': trigger,
            'guards': guards
        })

    def compose_guards(self, *guards, operator="AND"):
        def combined(*args, **kwargs):
            results = [g(*args, **kwargs) for g in guards]
            op = operator.upper()
            if op == "AND":
                return all(results)
            if op == "OR":
                return any(results)
            if op == "NOT":
                if len(guards) != 1:
                    raise ValueError("NOT operator requires exactly one guard")
                return not results[0]
            raise ValueError(f"Unknown operator: {operator}")
        return combined

    def on_enter(self, state, callback):
        self.on_enter_callbacks.setdefault(state, []).append(callback)

    def add_global_hook(self, when, hook_fn):
        if when not in ('before', 'after'):
            raise ValueError("when must be 'before' or 'after'")
        self.global_hooks[when].append(hook_fn)

    def push_undo(self, event):
        self.undo_stack.append(event)
        self.redo_stack.clear()

    def pop_undo(self):
        if not self.undo_stack:
            return None
        event = self.undo_stack.pop()
        self.redo_stack.append({
            'trigger': event['trigger'],
            'prev_state': self.current_state
        })
        self.current_state = event['prev_state']
        return event

    def export_machine(self, format="json"):
        data = {
            'states': list(self.states),
            'transitions': self.transitions,
            'current_state': self.current_state,
            'history_enabled': self.history_enabled
        }
        if format == "json":
            return json.dumps(data)
        if format == "dict":
            return data
        raise ValueError(f"Unsupported format: {format}")

    @staticmethod
    def load_machine(serialized):
        if isinstance(serialized, str):
            data = json.loads(serialized)
        elif isinstance(serialized, dict):
            data = serialized
        else:
            raise ValueError("serialized must be dict or JSON string")
        m = StateMachine()
        m.states = set(data.get('states', []))
        m.transitions = data.get('transitions', [])
        m.current_state = data.get('current_state')
        m.history_enabled = data.get('history_enabled', {})
        return m

    def export_visualization(self, path="graph.dot"):
        lines = ["digraph {"]
        for t in self.transitions:
            lines.append(f'    "{t["src"]}" -> "{t["dst"]}" [label="{t["name"]}"];')
        lines.append("}")
        content = "\n".join(lines)
        with open(path, "w") as f:
            f.write(content)
        return path

    def simulate_sequence(self, events):
        for ev in events:
            # find matching transition
            found = None
            for t in self.transitions:
                if t['trigger'] == ev and t['src'] == self.current_state:
                    # check guards
                    ok = all(g() for g in t['guards'])
                    if ok:
                        found = t
                        break
            if not found:
                raise ValueError(f"No valid transition for event {ev} from state {self.current_state}")
            # before hooks
            for hook in self.global_hooks['before']:
                hook(self, ev, found)
            prev = self.current_state
            self.current_state = found['dst']
            # on_enter
            for cb in self.on_enter_callbacks.get(self.current_state, []):
                cb(self, ev, found)
            # after hooks
            for hook in self.global_hooks['after']:
                hook(self, ev, found)
            # record undo
            self.push_undo({'trigger': ev, 'prev_state': prev})
        return self.current_state

    def enable_history(self, state, mode="deep"):
        self.history_enabled[state] = mode

def run_tests():
    import pytest
    return pytest.main([])
