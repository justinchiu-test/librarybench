from .registry import workflow_steps, register_workflow_step

def export_workflow(format='md'):
    # support decorator usage @export_workflow
    if callable(format):
        register_workflow_step(format)
        return format

    # "format" is expected to be a string now
    lines = []
    if format == 'md':
        for step in workflow_steps:
            lines.append(f"## {step['name']}")
            lines.append(step['doc'])
            lines.append('')
        return '\n'.join(lines)
    elif format == 'html':
        parts = []
        for step in workflow_steps:
            parts.append(f"<h2>{step['name']}</h2>")
            parts.append(f"<p>{step['doc']}</p>")
        return ''.join(parts)
    else:
        raise ValueError(f'Unknown format: {format}')
