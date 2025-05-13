def merge_configs(*configs):
    result = {}
    for cfg in configs:
        if not isinstance(cfg, dict):
            continue
        for k, v in cfg.items():
            if (k in result and isinstance(result[k], dict)
                    and isinstance(v, dict)):
                result[k] = merge_configs(result[k], v)
            else:
                result[k] = v
    return result
