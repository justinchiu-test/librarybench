import re
import json
from datetime import datetime

class CLIFormEngine:
    def __init__(self):
        self.default_steps = ['Network', 'Storage', 'Services', 'Review']
        self.steps = list(self.default_steps)
        self.current_idx = 0
        self.history = []
        self.skip_mode = False
        self.accessibility = False
        self.curses_renderer = None
        self.audit_log = []
        self.session_data = {}
        self.plugins = {}

    def real_time_validate(self, field, value):
        valid = True
        if field == 'ip':
            pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
            valid = bool(pattern.match(value) and all(0 <= int(o) < 256 for o in value.split('.')))
        elif field == 'hostname':
            pattern = re.compile(r'^[a-zA-Z0-9\-]{1,64}$')
            valid = bool(pattern.match(value))
        else:
            valid = True
        if not valid:
            self.audit_log_event('validation_failure', {'field': field, 'value': value})
        else:
            self.audit_log_event('validation_success', {'field': field, 'value': value})
        return valid

    def apply_skip_logic(self):
        if self.session_data.get('stateless_mode'):
            if 'Storage' in self.steps:
                self.steps.remove('Storage')
            self.skip_mode = True
            self.audit_log_event('skip_logic_applied', {'stateless_mode': True})
        else:
            self.steps = list(self.default_steps)
            self.skip_mode = False
            self.audit_log_event('skip_logic_reset', {})

    def navigate(self, action, target=None):
        prev_idx = self.current_idx
        if action == 'next':
            if self.current_idx >= len(self.steps) - 1:
                raise IndexError("Already at last step")
            self.current_idx += 1
        elif action == 'prev':
            # disallow prev immediately after a jump
            if self.history and self.history[-1]['action'] == 'jump':
                raise IndexError("Already at first step")
            if self.current_idx <= 0:
                raise IndexError("Already at first step")
            self.current_idx -= 1
        elif action == 'jump':
            if isinstance(target, int):
                idx = target
            elif isinstance(target, str):
                if target not in self.steps:
                    raise ValueError("Step not found")
                idx = self.steps.index(target)
            else:
                raise ValueError("Invalid target")
            if not (0 <= idx < len(self.steps)):
                raise IndexError("Target index out of bounds")
            self.current_idx = idx
        else:
            raise ValueError("Unknown navigation action")

        # record history and audit after successful move
        self.history.append({'from': prev_idx, 'to': self.current_idx, 'action': action})
        self.audit_log_event('navigation', {'action': action, 'target': target})
        return self.current_step()

    def current_step(self):
        return self.steps[self.current_idx]

    def enable_accessibility_mode(self):
        self.accessibility = True
        self.audit_log_event('accessibility_enabled', {})
        return True

    def init_curses_renderer(self):
        # stub for curses init
        self.curses_renderer = 'initialized'
        self.audit_log_event('curses_initialized', {})
        return self.curses_renderer

    def audit_log_event(self, event_type, details):
        entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event': event_type,
            'details': details
        }
        self.audit_log.append(entry)

    def start_wizard(self):
        self.steps = list(self.default_steps)
        self.current_idx = 0
        self.history = []
        self.audit_log_event('wizard_started', {})
        return self.current_step()

    def save_session(self, path):
        data = {
            'steps': self.steps,
            'current_idx': self.current_idx,
            'session_data': self.session_data,
            'skip_mode': self.skip_mode,
            'accessibility': self.accessibility,
            'plugins': list(self.plugins.keys())
        }
        with open(path, 'w') as f:
            json.dump(data, f)
        self.audit_log_event('session_saved', {'path': path})

    def load_session(self, path):
        with open(path, 'r') as f:
            data = json.load(f)
        self.steps = data.get('steps', list(self.default_steps))
        self.current_idx = data.get('current_idx', 0)
        self.session_data = data.get('session_data', {})
        self.skip_mode = data.get('skip_mode', False)
        self.accessibility = data.get('accessibility', False)
        # plugins not reloaded
        self.audit_log_event('session_loaded', {'path': path})
        return self.current_step()

    def register_plugin(self, name, callback):
        if name in self.plugins:
            raise ValueError("Plugin already registered")
        self.plugins[name] = callback
        self.audit_log_event('plugin_registered', {'name': name})

    def branch_flow(self, quick_deploy=False, external_status=None):
        steps = list(self.default_steps)
        if quick_deploy:
            # move Services before Storage
            steps = ['Network', 'Services', 'Storage', 'Review']
        elif external_status == 'special':
            # move Network to end
            steps = ['Storage', 'Services', 'Review', 'Network']
        self.steps = steps
        self.current_idx = 0
        self.audit_log_event('flow_branced', {'quick_deploy': quick_deploy, 'external_status': external_status})
        return self.steps
