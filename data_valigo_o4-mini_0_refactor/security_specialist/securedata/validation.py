import asyncio

class Rule:
    def __init__(self, name):
        self.name = name

    def validate(self, value):
        raise NotImplementedError()

class AsyncRule(Rule):
    async def validate_async(self, value):
        raise NotImplementedError()

class ValidationEngine:
    def __init__(self):
        self.profiles = {}
        self.current = None

    def register_rule(self, profile: str, rule):
        self.profiles.setdefault(profile, []).append(rule)

    def set_profile(self, profile: str):
        self.current = profile

    def validate(self, value):
        results = []
        for rule in self.profiles.get(self.current, []):
            res = rule.validate(value)
            results.append((rule.name, res))
        return results

    async def validate_async(self, value):
        results = []
        for rule in self.profiles.get(self.current, []):
            if isinstance(rule, AsyncRule):
                res = await rule.validate_async(value)
            else:
                res = rule.validate(value)
            results.append((rule.name, res))
        return results
