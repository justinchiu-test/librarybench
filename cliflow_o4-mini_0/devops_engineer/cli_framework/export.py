class Flow:
    def __init__(self, name):
        self.name = name
        self.steps = []
    def add_step(self, name, description):
        self.steps.append((name, description))

def export_docs(flow, format='md'):
    if format == 'md':
        lines = [f"# Flow: {flow.name}", ""]
        for name, desc in flow.steps:
            lines.append(f"## Step: {name}")
            lines.append(desc)
            lines.append("")
        return "\n".join(lines)
    elif format == 'html':
        html = [f"<h1>Flow: {flow.name}</h1>"]
        for name, desc in flow.steps:
            html.append(f"<h2>Step: {name}</h2><p>{desc}</p>")
        return "".join(html)
    else:
        raise ValueError("Unsupported format")
