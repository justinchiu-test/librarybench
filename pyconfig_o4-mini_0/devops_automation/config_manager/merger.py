from .merge_strategies import get_strategy

class Merger:
    def __init__(self, list_strategy="append"):
        self.list_strategy = list_strategy

    def merge(self, default, repo_conf, env_conf):
        return self._deep_merge(default, repo_conf, env_conf)

    def _deep_merge(self, base, override, env):
        # Dicts: merge each key recursively
        if isinstance(base, dict) and isinstance(override, dict) and isinstance(env, dict):
            result = {}
            keys = set(base) | set(override) | set(env)
            for key in keys:
                val_base = base.get(key)
                val_override = override.get(key)
                val_env = env.get(key)
                result[key] = self._deep_merge(val_base, val_override, val_env)
            return result
        # Lists: apply strategy
        if isinstance(base, list) or isinstance(override, list) or isinstance(env, list):
            strat = get_strategy(self.list_strategy)
            if self.list_strategy == "replace":
                # priority: env > override > base
                if env is not None:
                    return list(env)
                if override is not None:
                    return list(override)
                if base is not None:
                    return list(base)
                return []
            else:
                # for append and other strategies, combine override + env as "new"
                existing = base or []
                new = (override or []) + (env or [])
                return strat(existing, new)
        # Scalars: env overrides override overrides base
        if env is not None:
            return env
        if override is not None:
            return override
        return base
