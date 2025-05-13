renderers = {}
tasks = {}
workflow_steps = []

def register_renderer(name, func):
    renderers[name] = func

def register_task(name, func):
    tasks[name] = func

def register_workflow_step(func):
    workflow_steps.append({
        'name': func.__name__,
        'doc': func.__doc__ or ''
    })
