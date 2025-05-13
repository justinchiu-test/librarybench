"""
Documentation generator for DevOps Engineer CLI.
"""
def generate_docs(spec, formats=None):
    if formats is None:
        formats = []
    output = {}
    for fmt in formats:
        if fmt == 'md':
            lines = []
            for k, v in spec.items():
                lines.append(f"## {k}\n")
                lines.append(v)
            output['md'] = '\n'.join(lines)
        elif fmt == 'rst':
            lines = [f"- {k}: {v}" for k, v in spec.items()]
            output['rst'] = '\n'.join(lines)
        elif fmt == 'html':
            items = ''.join(f"<li><strong>{k}</strong>: {v}</li>" for k, v in spec.items())
            output['html'] = f"<ul>{items}</ul>"
        elif fmt == 'man':
            man = ['.TH CLI 1']
            man.append('.SH COMMANDS')
            for k, v in spec.items():
                man.append(f".TP\n{ k } - { v }")
            output['man'] = '\n'.join(man)
    return output