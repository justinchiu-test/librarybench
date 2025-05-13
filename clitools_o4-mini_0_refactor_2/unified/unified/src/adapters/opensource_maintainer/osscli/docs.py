"""
Documentation generator for Open Source Maintainer CLI.
"""
def generate_docs(cmds):
    result = {}
    # Markdown
    result['md'] = '\n'.join(f"- {c}" for c in cmds)
    # reStructuredText
    result['rst'] = '\n'.join(f"- {c}" for c in cmds)
    # HTML
    result['html'] = ''.join(f"<p>{c}</p>" for c in cmds)
    # man page
    result['man'] = 'COMMANDS\n' + '\n'.join(cmds)
    return result