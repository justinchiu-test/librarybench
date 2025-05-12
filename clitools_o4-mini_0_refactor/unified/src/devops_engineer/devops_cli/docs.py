"""
Generate documentation in various formats for devops engineers.
"""
def generate_docs(spec, formats=None):
    if formats is None:
        formats = ['md']
    output = {}
    for fmt in formats:
        if fmt == 'md':
            # Markdown header for commands
            lines = [f"## {cmd}" for cmd in spec.keys()]
            output['md'] = '\n'.join(lines)
        elif fmt == 'rst':
            # simple reStructuredText
            lines = [f"{cmd}" for cmd in spec.keys()]
            output['rst'] = '\n'.join(lines)
        elif fmt == 'html':
            # HTML list
            items = ''.join([f"<li><strong>{cmd}</strong> {desc}</li>" for cmd, desc in spec.items()])
            output['html'] = f"<ul>{items}</ul>"
        elif fmt == 'man':
            # man page stub
            output['man'] = '.TH CLI 1'
        else:
            raise ValueError(f"Unknown format: {fmt}")
    return output