import difflib

def generate_diff(old, new, fromfile='old', tofile='new'):
    old_lines = old.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    diff = difflib.unified_diff(old_lines, new_lines, fromfile=fromfile, tofile=tofile)
    return ''.join(diff)
