def export_docs(flow_steps, format='markdown'):
    """
    flow_steps: list of step descriptions
    format: 'markdown' or 'html'
    """
    if format == 'markdown':
        lines = ["# Onboarding Workflow", ""]
        for i, step in enumerate(flow_steps, 1):
            lines.append(f"{i}. {step}")
        return "\n".join(lines)
    elif format == 'html':
        items = "".join(f"<li>{step}</li>" for step in flow_steps)
        return f"<h1>Onboarding Workflow</h1><ol>{items}</ol>"
    else:
        raise ValueError("Unsupported format")
