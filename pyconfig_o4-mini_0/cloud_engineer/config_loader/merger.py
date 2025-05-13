# config_merger and list_merge_strategies
from copy import deepcopy

def merge_configs(configs: list, list_strategy: str = 'replace') -> dict:
    """
    Merge a list of configuration dicts.
    Precedence: later dicts override earlier ones.
    list_strategy: 'append', 'replace', 'unique'
    """
    result = {}
    for cfg in configs:
        for k, v in cfg.items():
            if isinstance(v, list) and k in result and isinstance(result[k], list):
                if list_strategy == 'append':
                    result[k] = result[k] + v
                elif list_strategy == 'unique':
                    result[k] = list(dict.fromkeys(result[k] + v))
                else:  # replace
                    result[k] = deepcopy(v)
            elif isinstance(v, dict) and k in result and isinstance(result[k], dict):
                result[k] = merge_configs([result[k], v], list_strategy)
            else:
                result[k] = deepcopy(v)
    return result
