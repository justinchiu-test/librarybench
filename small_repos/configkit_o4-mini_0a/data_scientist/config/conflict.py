def report_conflicts(experiments):
    path_map = {}
    for exp in experiments:
        out = exp.get('output_path')
        if not out:
            continue
        if out in path_map:
            raise ValueError(f"Conflict detected: {out} used in multiple experiments")
        path_map[out] = exp
    return False
