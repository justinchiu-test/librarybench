"""
Shared utility functions for version handling, file I/O, and GUI text formatting.
This file must work when imported by different modules in different directories.
"""

import os
import json

def parse_version(v):
    """Convert semantic version string to a tuple of ints."""
    return tuple(int(x) for x in v.split('.'))

def compare_versions(v1, v2):
    """
    Compare two semantic version strings.
    Returns -1 if v1 < v2, 0 if equal, +1 if v1 > v2.
    """
    p1 = list(parse_version(v1))
    p2 = list(parse_version(v2))
    length = max(len(p1), len(p2))
    p1 += [0] * (length - len(p1))
    p2 += [0] * (length - len(p2))
    if p1 < p2:
        return -1
    if p1 > p2:
        return 1
    return 0

def parse_spec_multi(spec):
    """
    Parse a spec like "pkg>=1.0,<2.0" or "pkg==1.0" or "pkg".
    Returns (name, [(op, version), ...]).
    """
    name = ''
    i = 0
    while i < len(spec) and (spec[i].isalnum() or spec[i] in ('_', '-')):
        name += spec[i]
        i += 1
    raw = spec[i:].strip()
    constraints = []
    if not raw:
        return name, constraints
    for part in raw.split(','):
        part = part.strip()
        if not part:
            continue
        for op in ('>=', '<=', '==', '>', '<'):
            if part.startswith(op):
                constraints.append((op, part[len(op):]))
                break
        else:
            raise ValueError(f"Invalid constraint '{part}'")
    return name, constraints

def satisfies_constraints(version, constraints):
    """Check if a version satisfies all (op, version) constraints."""
    for op, ver in constraints:
        cmp = compare_versions(version, ver)
        if op == '==' and cmp != 0:
            return False
        if op == '>=' and cmp < 0:
            return False
        if op == '<=' and cmp > 0:
            return False
        if op == '>' and cmp <= 0:
            return False
        if op == '<' and cmp >= 0:
            return False
    return True

def load_json_file(path):
    """Load and return JSON data from a file, error if missing."""
    if not os.path.exists(path):
        raise ValueError(f"File {path} not found")
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(path, data, indent=2):
    """Save data as JSON to path."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent)

def read_lines(path):
    """Read all lines from a text file, stripped."""
    with open(path, 'r', encoding='utf-8') as f:
        return [line.rstrip('\n') for line in f]

def write_lines(path, lines):
    """Write lines to a text file (no trailing newline)."""
    with open(path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

def parse_pin_line(line):
    """Parse a pin line 'name==version' or raise ValueError."""
    if '==' not in line:
        raise ValueError(f"Invalid pin format: '{line}'")
    name, ver = line.split('==', 1)
    return name, ver

# GUI formatting helpers
def format_pkg_display(package):
    """Format a Package instance for display: 'name==version'."""
    return f"{package.name}=={package.metadata.version}"

def split_pkg_text(text):
    """Split a display string 'name==version' into (name, version)."""
    return text.split('==', 1)

def get_selected_pkg(listbox):
    """
    Return (name, version) for the selected item in a Tk Listbox,
    or (None, None) if no selection.
    """
    sel = listbox.curselection()
    if not sel:
        return None, None
    return split_pkg_text(listbox.get(sel[0]))

def build_metadata_text(name, metadata):
    """Build the multiline metadata info for display."""
    lines = [f"Name: {name}", f"Version: {metadata.version}", "Dependencies:"]
    for d in metadata.dependencies:
        lines.append(f"  - {d}")
    return "\n".join(lines)
