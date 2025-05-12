"""
Documentation generator for open-source maintainers.
"""
def generate_docs(cmds):
    # cmds: list of command names
    docs = {}
    # Markdown
    md = '\n'.join(f"- {cmd}" for cmd in cmds)
    docs['md'] = md
    # reST
    rst = '\n'.join(f"- {cmd}" for cmd in cmds)
    docs['rst'] = rst
    # HTML
    html = ''.join(f"<p>{cmd}</p>" for cmd in cmds)
    docs['html'] = html
    # man page stub
    docs['man'] = 'COMMANDS'
    return docs