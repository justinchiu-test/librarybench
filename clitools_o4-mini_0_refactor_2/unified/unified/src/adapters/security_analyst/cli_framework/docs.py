"""
Documentation generator for Security Analyst CLI.
"""
def generate_docs(cmds):
    lines = ['SECURITY']
    for k, v in cmds.items():
        lines.append(f"{k}\t{v}")
    return '\n'.join(lines)