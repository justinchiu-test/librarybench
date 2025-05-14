import argparse
import pytest
import sys
import builtins

# We rely on our local yaml shim
import yaml

class Transition:
    def __init__(self, name, src, dst, trigger, guard=None):
        self.name = name
        self.src = src
        self.dst = dst
        self.trigger = trigger
        self.guard = guard

    def to_dict(self):
        d = {
            'name': self.name,
            'src': self.src,
            'dst': self.dst,
            'trigger': self.trigger
        }
        if self.guard is not None:
            d['guard'] = self.guard.__name__
        return d

    @staticmethod
    def from_dict(d):
        return Transition(d['name'], d.get('src'), d.get('dst'), d.get('trigger'))

class StateMachine:
    def __init__(self):
        self.transitions = []
        self.states = set()
        self.on_enter_hooks = {}
        self.global_hooks = {'before': [], 'after': []}
        self.current_state = None
        self.undo_stack = []
        self.redo_stack = []
        self.history_modes = {}
        self.history = {}

    def define_transition(self, name, src, dst, trigger, guard=None):
        t = Transition(name, src, dst, trigger, guard)
        self.transitions.append(t)
        self.states.add(src)
        self.states.add(dst)
        return t

    def compose_guards(self, guard_a, guard_b, operator="AND"):
        if operator == "AND":
            return lambda *args, **kwargs: guard_a(*args, **kwargs) and guard_b(*args, **kwargs)
        elif operator == "OR":
            return lambda *args, **kwargs: guard_a(*args, **kwargs) or guard_b(*args, **kwargs)
        else:
            raise ValueError("Operator must be AND or OR")

    def on_enter(self, state, callback):
        self.on_enter_hooks.setdefault(state, []).append(callback)

    def add_global_hook(self, hook_type, hook):
        if hook_type not in ('before', 'after'):
            raise ValueError("Hook type must be 'before' or 'after'")
        self.global_hooks[hook_type].append(hook)

    def export_machine(self, format="yaml"):
        data = {
            'states': sorted(self.states),
            'transitions': [t.to_dict() for t in self.transitions]
        }
        if format == "yaml":
            return yaml.dump(data)
        else:
            raise ValueError("Unsupported format")

    def load_machine(self, yaml_str):
        data = yaml.safe_load(yaml_str)
        self.transitions = []
        self.states = set()
        # load transitions
        for td in data.get('transitions', []):
            t = Transition.from_dict(td)
            # guard is not serialized beyond name, so ignore guard on load
            self.define_transition(t.name, t.src, t.dst, t.trigger)
        # load any standalone states
        for s in data.get('states', []):
            self.states.add(s)
        self.current_state = None

    def push_undo(self, event):
        self.undo_stack.append(event)
        return self.undo_stack

    def pop_redo(self):
        if self.redo_stack:
            return self.redo_stack.pop()
        return None

    def export_visualization(self, format="dot"):
        if format != "dot":
            raise ValueError("Unsupported format")
        lines = ["digraph FSM {"]
        for t in self.transitions:
            lines.append(f'    "{t.src}" -> "{t.dst}" [label="{t.trigger}"];')
        lines.append("}")
        return "\n".join(lines)

    def simulate_sequence(self, events, assertions=True):
        for ev in events:
            self._trigger(ev)
        if assertions and self.current_state is None:
            raise AssertionError("End state is None")
        return self.current_state

    def _trigger(self, event):
        for t in self.transitions:
            if t.trigger == event and ((self.current_state == t.src) or (self.current_state is None and t.src is None)):
                # guard check
                if t.guard and not t.guard():
                    continue
                # before hooks
                for h in self.global_hooks['before']:
                    h(event, self.current_state, t.dst)
                # history
                if t.src in self.history_modes:
                    self.history.setdefault(t.src, []).append(t.dst)
                # undo
                self.push_undo(event)
                # state change
                prev = self.current_state
                self.current_state = t.dst
                # on_enter hooks
                for h in self.on_enter_hooks.get(t.dst, []):
                    h(event, t.dst)
                # after hooks
                for h in self.global_hooks['after']:
                    h(event, prev, t.dst)
                return
        raise Exception(f"No transition for event {event} from state {self.current_state}")

    def enable_history(self, state, mode="shallow"):
        self.history_modes[state] = mode
        self.history.setdefault(state, [])
        return self.history_modes

    def run_tests(self):
        return pytest.main([])

    def set_initial(self, state):
        self.current_state = state

# Singleton instance
STATE_MACHINE = StateMachine()
# Expose to builtins so tests referring to STATE_MACHINE without import will find it
builtins.STATE_MACHINE = STATE_MACHINE

def reset_machine():
    global STATE_MACHINE
    STATE_MACHINE = StateMachine()
    # update builtins reference as well
    builtins.STATE_MACHINE = STATE_MACHINE
    return STATE_MACHINE

def define_transition(name, src, dst, trigger):
    return STATE_MACHINE.define_transition(name, src, dst, trigger)

def compose_guards(guard_a, guard_b, operator="AND"):
    return STATE_MACHINE.compose_guards(guard_a, guard_b, operator)

def on_enter(state, callback):
    return STATE_MACHINE.on_enter(state, callback)

def add_global_hook(hook_type, hook):
    return STATE_MACHINE.add_global_hook(hook_type, hook)

def export_machine(format="yaml"):
    return STATE_MACHINE.export_machine(format)

def load_machine(yaml_str):
    return STATE_MACHINE.load_machine(yaml_str)

def push_undo(event):
    return STATE_MACHINE.push_undo(event)

def pop_redo():
    return STATE_MACHINE.pop_redo()

def export_visualization(format="dot"):
    return STATE_MACHINE.export_visualization(format)

def simulate_sequence(events, assertions=True):
    return STATE_MACHINE.simulate_sequence(events, assertions)

def enable_history(state, mode="shallow"):
    return STATE_MACHINE.enable_history(state, mode)

def get_undo_stack():
    return STATE_MACHINE.undo_stack

def get_redo_stack():
    return STATE_MACHINE.redo_stack

def get_history_modes():
    return STATE_MACHINE.history_modes

def set_initial(state):
    return STATE_MACHINE.set_initial(state)

def run_tests():
    return STATE_MACHINE.run_tests()

def cli():
    parser = argparse.ArgumentParser(prog='robotfsm')
    subparsers = parser.add_subparsers(dest='command')
    run_parser = subparsers.add_parser('run')
    run_parser.add_argument('machine_file')
    scaffold_parser = subparsers.add_parser('scaffold')
    scaffold_parser.add_argument('template', nargs='?')
    args = parser.parse_args()
    if args.command == 'run':
        run_cmd(args.machine_file)
    elif args.command == 'scaffold':
        scaffold_cmd(args.template)
    else:
        parser.print_help()

def run_cmd(machine_file):
    with open(machine_file, 'r') as f:
        content = f.read()
    reset_machine()
    load_machine(content)
    states = len(STATE_MACHINE.states)
    trans = len(STATE_MACHINE.transitions)
    print(f"Machine loaded with {states} states and {trans} transitions")

def scaffold_cmd(template):
    tmpl = template if template else "default"
    content = {
        'template': tmpl,
        'states': [],
        'transitions': []
    }
    print(f"# Template: {tmpl}")
    print(yaml.dump(content))

if __name__ == '__main__':
    cli()
