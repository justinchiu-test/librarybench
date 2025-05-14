import datetime
import re

class CoercerRegistry:
    def __init__(self):
        self._registry = {}
        self._init_defaults()

    def _init_defaults(self):
        self.register('semver', self._semver)
        self.register('date', self._date_iso)

    def register(self, name, func):
        self._registry[name] = func

    def coerce(self, name, value):
        if name not in self._registry:
            raise KeyError(f"No coercer for {name}")
        return self._registry[name](value)

    def _semver(self, v):
        parts = v.strip().split('.')
        try:
            return tuple(int(p) for p in parts)
        except:
            raise ValueError(f"Invalid semver: {v}")

    def _date_iso(self, v):
        return datetime.datetime.strptime(v, '%Y-%m-%d').date()
