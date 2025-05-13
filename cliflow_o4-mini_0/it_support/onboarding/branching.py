def branch_flow(context, branches, default=None):
    """
    branches: dict mapping key to function
    context: dict-like with 'department' or 'os'
    """
    key = context.get('department') or context.get('os')
    func = branches.get(key, default)
    if func is None:
        raise KeyError(f"No branch for key: {key}")
    return func(context)
