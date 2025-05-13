import asyncio

def guard_function(predicate):
    def wrapper(context):
        res = predicate(context)
        if asyncio.iscoroutine(res):
            return res
        return res
    return wrapper

def compose_guard_set_and(*guards):
    async def _and(context):
        for g in guards:
            res = g(context)
            if asyncio.iscoroutine(res):
                res = await res
            if not res:
                return False
        return True
    return _and

def compose_guard_set_or(*guards):
    async def _or(context):
        for g in guards:
            res = g(context)
            if asyncio.iscoroutine(res):
                res = await res
            if res:
                return True
        return False
    return _or

def compose_guard_set_not(guard):
    async def _not(context):
        res = guard(context)
        if asyncio.iscoroutine(res):
            res = await res
        return not res
    return _not

def run_if(predicate, fn):
    async def runner(context):
        res = predicate(context)
        if asyncio.iscoroutine(res):
            res = await res
        if res:
            out = fn(context)
            if asyncio.iscoroutine(out):
                await out
    return runner

def simulate_and_assert(machine, events, expected_state, context=None):
    loop = asyncio.get_event_loop()
    async def _run():
        for e in events:
            await machine.handle_event(e, context)
        assert machine.current_state == expected_state
    loop.run_until_complete(_run())
