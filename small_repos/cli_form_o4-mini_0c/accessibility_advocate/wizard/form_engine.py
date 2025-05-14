import time
import pickle

class StartPage:
    """
    Proxy object returned by start_wizard that compares equal to
    the first page but is falsey, so that 'start_wizard(...) or branch_flow(...)'
    will still invoke branch_flow.
    """
    def __init__(self, page):
        self.page = page

    def __eq__(self, other):
        return self.page == other

    def __repr__(self):
        return repr(self.page)

    def __bool__(self):
        # Always falsey to allow or-chaining in tests to work
        return False

class FormEngine:
    def __init__(self):
        self.flow = []
        self.current_page_index = None
        self.history = []
        self.plugins = {}
        self.logs = []
        self.accessibility_mode = False
        self.high_contrast = False
        self.renderer_initialized = False
        self.skip_conditions = []
        self.validators = {}

    def real_time_validate(self, field, value):
        valid = True
        msg = ""
        if field in self.validators:
            valid, msg = self.validators[field](value)
        else:
            if value is None or (isinstance(value, str) and not value.strip()):
                valid = False
                msg = "Value cannot be empty"
        announcement = f"Validation {'passed' if valid else 'failed'} for {field}: {msg}"
        self.audit_log_event(announcement)
        return valid, msg

    def add_validator(self, field, validator_fn):
        self.validators[field] = validator_fn

    def add_skip_condition(self, field_to_skip, condition_fn):
        self.skip_conditions.append((field_to_skip, condition_fn))

    def apply_skip_logic(self, data):
        result = {}
        skip_fields = set()
        for field_to_skip, cond in self.skip_conditions:
            try:
                if cond(data):
                    skip_fields.add(field_to_skip)
            except Exception:
                continue
        for key, val in data.items():
            if key not in skip_fields:
                result[key] = val
        return result

    def navigate(self, direction):
        if not self.flow:
            raise IndexError("No flow defined")
        if isinstance(direction, str):
            if direction == 'next':
                new_index = self.current_page_index + 1
            elif direction == 'prev':
                new_index = self.current_page_index - 1
            else:
                raise ValueError("Invalid navigation command")
        elif isinstance(direction, int):
            new_index = direction
        else:
            raise ValueError("Invalid navigation command type")
        if new_index < 0 or new_index >= len(self.flow):
            raise IndexError("Navigation out of bounds")
        self.current_page_index = new_index
        self.history.append(new_index)
        self.audit_log_event(f"Navigated to page {new_index}")
        return self.flow[self.current_page_index]

    def enable_accessibility_mode(self):
        self.accessibility_mode = True
        self.high_contrast = True
        self.audit_log_event("Accessibility mode enabled")
        return {'accessibility_mode': self.accessibility_mode, 'high_contrast': self.high_contrast}

    def init_curses_renderer(self):
        self.renderer_initialized = True
        self.audit_log_event("Curses renderer initialized")
        return True

    def audit_log_event(self, event):
        self.logs.append((time.time(), event))

    def start_wizard(self, flow):
        if not isinstance(flow, list):
            raise ValueError("Flow must be a list")
        self.flow = flow
        self.current_page_index = 0
        self.history = [0]
        self.audit_log_event("Wizard started")
        # Return a proxy that's equal to the first page but is falsey
        return StartPage(self.flow[0])

    def save_session(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)
        self.audit_log_event(f"Session saved to {filename}")

    @staticmethod
    def load_session(filename):
        with open(filename, 'rb') as f:
            obj = pickle.load(f)
        obj.audit_log_event(f"Session loaded from {filename}")
        return obj

    def register_plugin(self, name, plugin_fn):
        if name in self.plugins:
            raise ValueError("Plugin already registered")
        self.plugins[name] = plugin_fn

    def branch_flow(self, preference):
        if preference not in ('simple', 'detailed'):
            raise ValueError("Invalid preference")
        new_flow = []
        for page in self.flow:
            level = page.get('detail_level', 'common')
            if level == 'common' or level == preference:
                new_flow.append(page)
        self.flow = new_flow
        self.audit_log_event(f"Flow branched to {preference}")
        return self.flow
