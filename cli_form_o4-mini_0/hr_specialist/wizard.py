import re
import json
import os

class OnboardingWizard:
    def __init__(self):
        self.context = {}
        self.history = []
        self.pages = ["Personal Info", "Benefits", "Equipment", "Review"]
        self.current_page = self.pages[0]
        self.audit_log = []
        self.skip = {}
        self.accessibility = False
        self.high_contrast = False
        self.stdscr = None
        self.renderer_initialized = False
        self.plugins = {}

    def real_time_validate(self, text, field_type):
        if field_type == "email":
            pattern = r"^[^@]+@[^@]+\.[^@]+$"
        elif field_type == "ssn":
            pattern = r"^\d{3}-\d{2}-\d{4}$"
        elif field_type == "phone":
            pattern = r"^\+?\d{10,15}$"
        else:
            return False
        return re.match(pattern, text) is not None

    def apply_skip_logic(self):
        etype = self.context.get("employment_type", "").lower()
        # skip pension plan if not full-time
        self.skip["pension_plan"] = etype != "full-time"
        self.audit_log_event("apply_skip_logic", {"employment_type": etype, "skip": self.skip.copy()})
        return self.skip

    def navigate(self, action, target=None):
        if action == "next":
            idx = self.pages.index(self.current_page)
            if idx < len(self.pages) - 1:
                self.history.append(self.current_page)
                self.current_page = self.pages[idx + 1]
        elif action == "prev":
            if self.history:
                self.current_page = self.history.pop()
        elif action == "jump":
            if target in self.pages:
                self.history.append(self.current_page)
                self.current_page = target
        self.audit_log_event("navigate", {"action": action, "target": target, "current": self.current_page})
        return self.current_page

    def enable_accessibility_mode(self):
        self.accessibility = True
        self.high_contrast = True
        self.audit_log_event("enable_accessibility_mode", {"accessibility": True, "high_contrast": True})

    def init_curses_renderer(self, stdscr):
        # stub for curses renderer initialization
        self.stdscr = stdscr
        self.renderer_initialized = True
        self.audit_log_event("init_curses_renderer", {})

    def audit_log_event(self, event, data=None):
        entry = {"event": event, "data": data or {}}
        self.audit_log.append(entry)

    def start_wizard(self):
        self.context = {}
        self.history = []
        self.current_page = self.pages[0]
        self.audit_log_event("start_wizard", {})

    def save_session(self, path):
        state = {
            "context": self.context,
            "history": self.history,
            "current_page": self.current_page
        }
        with open(path, "w") as f:
            json.dump(state, f)
        self.audit_log_event("save_session", {"path": path})

    def load_session(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"No session file at {path}")
        with open(path, "r") as f:
            state = json.load(f)
        self.context = state.get("context", {})
        self.history = state.get("history", [])
        self.current_page = state.get("current_page", self.pages[0])
        self.audit_log_event("load_session", {"path": path})

    def register_plugin(self, name, func):
        self.plugins[name] = func
        self.audit_log_event("register_plugin", {"name": name})

    def branch_flow(self):
        show = self.context.get("Relocate", "").lower() == "yes"
        self.audit_log_event("branch_flow", {"show_relocation": show})
        return show
