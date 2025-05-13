import re
import getpass

class CLIForm:
    def __init__(self):
        self.answers = {}
        self.change_hooks = []
        self.cache = {}
        self.theme = {}

    def register_on_change(self, callback):
        self.change_hooks.append(callback)

    def _trigger_on_change(self, key, value):
        for hook in self.change_hooks:
            hook(key, value)

    def ask_text(self, key, prompt, min_length=None, max_length=None, pattern=None, placeholder=None):
        full_prompt = prompt
        if placeholder:
            full_prompt += f" ({placeholder})"
        full_prompt += ": "
        val = input(full_prompt)
        if min_length is not None and len(val) < min_length:
            raise ValueError(f"Input for {key} shorter than minimum length {min_length}")
        if max_length is not None and len(val) > max_length:
            raise ValueError(f"Input for {key} longer than maximum length {max_length}")
        if pattern is not None and not re.match(pattern, val):
            raise ValueError(f"Input for {key} does not match pattern {pattern}")
        self.answers[key] = val
        self._trigger_on_change(key, val)
        return val

    def input_line_fallback(self, key, prompt, **kwargs):
        return self.ask_text(key, prompt, **kwargs)

    def ask_password(self, key, prompt, strength_meter=False):
        full_prompt = prompt + ": "
        val = getpass.getpass(full_prompt)
        if strength_meter:
            strength = "strong" if len(val) >= 8 else "weak"
            result = {"value": val, "strength": strength}
        else:
            result = val
        self.answers[key] = result
        self._trigger_on_change(key, result)
        return result

    def select_choices(self, key, prompt, choices, multi=False):
        for idx, choice in enumerate(choices, 1):
            print(f"{idx}. {choice}")
        selection = input(prompt + ": ")
        if multi:
            indices = [int(i.strip()) for i in selection.split(",") if i.strip()]
            selected = [choices[i - 1] for i in indices]
        else:
            idx = int(selection.strip())
            selected = choices[idx - 1]
        self.answers[key] = selected
        self._trigger_on_change(key, selected)
        return selected

    def branch_flow(self, condition_func, flows):
        if isinstance(flows, dict):
            key = condition_func(self.answers)
            flow = flows.get(key)
            if callable(flow):
                return flow()
            return flow
        elif isinstance(flows, list):
            for cond, flow in flows:
                if cond(self.answers):
                    if callable(flow):
                        return flow()
                    return flow
            raise KeyError("No matching branch")
        else:
            raise TypeError("Flows must be dict or list")

    def load_choices_async(self, key, loader_func):
        if key not in self.cache:
            self.cache[key] = loader_func()
        return self.cache[key]

    def review_submission(self, allow_edit=False):
        if allow_edit:
            for key, val in list(self.answers.items()):
                resp = input(f"Edit {key}? current [{val}] (y/n): ")
                if resp.strip().lower() == "y":
                    new_val = input(f"New value for {key}: ")
                    self.answers[key] = new_val
        return dict(self.answers)

    def set_renderer_theme(self, theme_dict):
        self.theme = theme_dict

    def format_errors(self, errors, field=None):
        if field is not None and isinstance(errors, dict):
            errs = errors.get(field, [])
        elif field is None and isinstance(errors, list):
            errs = errors
        elif field is None and isinstance(errors, dict):
            errs = [f"{k}: {'; '.join(v)}" for k, v in errors.items()]
        else:
            raise ValueError("Invalid errors input")
        return "** " + "; ".join(errs) + " **"
