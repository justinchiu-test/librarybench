def add_tag(task, tag):
    """
    task: dict
    tag: str
    """
    task.setdefault("tags", []).append(tag)
    return task
