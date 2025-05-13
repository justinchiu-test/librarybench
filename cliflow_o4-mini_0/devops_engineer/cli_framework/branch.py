def branch_flow(context, condition, on_true, on_false, *args, **kwargs):
    if callable(condition):
        res = condition()
    else:
        res = bool(condition)
    if res:
        return on_true(context, *args, **kwargs)
    else:
        return on_false(context, *args, **kwargs)
