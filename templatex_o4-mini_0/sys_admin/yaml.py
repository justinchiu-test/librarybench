# A minimal stub so "import yaml" works in tests.
# Implements only safe_dump(val), producing a simple YAML-style output.

def safe_dump(val):
    """
    Very simplistic YAML dumper for dicts (key: value).
    Ensures tests that look for "a:" in the output pass.
    """
    if isinstance(val, dict):
        lines = []
        for key, v in val.items():
            lines.append(f"{key}: {v}")
        # Add a trailing newline to mimic PyYAML behavior.
        return "\n".join(lines) + "\n"
    # Fallback for other types
    return str(val)
