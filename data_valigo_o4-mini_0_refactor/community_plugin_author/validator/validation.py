import inspect
import asyncio

class AsyncValidationError(Exception):
    pass

class Validator:
    def __init__(self, profile: str = None):
        self.profile = profile

    async def _run_rule(self, rule_fn, value, context):
        if inspect.iscoroutinefunction(rule_fn):
            return await rule_fn(value, context)
        else:
            return rule_fn(value, context)

    def validate(self, name: str, value, context=None):
        context = context or {}
        context['profile'] = self.profile
        from .plugins import get_rule
        rule_fn = get_rule(name, self.profile)
        if not rule_fn:
            raise AsyncValidationError(f"No rule registered: {name}")
        result = rule_fn(value, context)
        if inspect.isawaitable(result):
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(result)
        return result

    async def validate_async(self, name: str, value, context=None):
        context = context or {}
        context['profile'] = self.profile
        from .plugins import get_rule
        rule_fn = get_rule(name, self.profile)
        if not rule_fn:
            raise AsyncValidationError(f"No rule registered: {name}")
        return await self._run_rule(rule_fn, value, context)
