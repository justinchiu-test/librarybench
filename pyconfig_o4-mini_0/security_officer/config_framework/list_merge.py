def merge_list(default_list, override_list, unique=True):
    if override_list is None:
        return default_list
    if unique:
        combined = default_list + override_list
        return list(dict.fromkeys(combined))
    return override_list
