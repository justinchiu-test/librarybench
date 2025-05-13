import re

class FormEngine:
    def __init__(self):
        self._cache = {}
        self.themes = {}
        self.hooks = {}
        self.last_strength = None

    def ask_text(self, input_str, min_len=0, max_len=100, pattern=None, placeholder=None):
        length = len(input_str)
        if length < min_len or length > max_len:
            raise ValueError(f"Input length must be between {min_len} and {max_len}")
        if pattern:
            if not re.match(pattern, input_str):
                raise ValueError(f"Input does not match pattern {pattern}")
        return input_str

    def branch_flow(self, role_type):
        if role_type == 'engineering':
            return ['coding_skills', 'system_design', 'behavioral']
        elif role_type == 'marketing':
            return ['market_analysis', 'creativity', 'behavioral']
        else:
            return ['general']

    def load_choices_async(self, key, fetch_func):
        if key in self._cache:
            return self._cache[key]
        choices = fetch_func()
        self._cache[key] = choices
        return choices

    def input_line_fallback(self, prompt, input_str):
        return input_str

    def review_submission(self, entries, edit_key=None, new_value=None):
        if edit_key is not None and new_value is not None:
            entries[edit_key] = new_value
        lines = []
        for k, v in entries.items():
            lines.append(f"{k}: {v}")
        return "\n".join(lines)

    def ask_password(self, password_str, show=False):
        strength = 'strong' if len(password_str) >= 8 and re.search(r'\d', password_str) else 'weak'
        self.last_strength = strength
        if show:
            return password_str
        return '*' * len(password_str)

    def select_choices(self, choices, indices, multiple=False):
        if multiple:
            return [choices[i] for i in indices]
        if isinstance(indices, (list, tuple)):
            idx = indices[0]
        else:
            idx = indices
        return choices[idx]

    def set_renderer_theme(self, theme_name, palette):
        self.themes[theme_name] = palette

    def register_on_change(self, field, hook):
        self.hooks.setdefault(field, []).append(hook)

    def trigger_on_change(self, field, value):
        for hook in self.hooks.get(field, []):
            hook(field, value)

    def format_errors(self, errors, theme_name=None):
        lines = []
        for field, msg in errors:
            lines.append(f"[{field}] {msg}")
        return "\n".join(lines)
