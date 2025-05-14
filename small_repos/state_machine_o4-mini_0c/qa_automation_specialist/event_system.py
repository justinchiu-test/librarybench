import asyncio
import inspect

class Transition:
    def __init__(self, name, source, target, guard=None, timeout=None, on_enter=None, on_exit=None):
        self.name = name
        self.source = source
        self.target = target
        self.guard = guard
        self.timeout = timeout
        self.on_enter = on_enter
        self.on_exit = on_exit

class StateMachine:
    def __init__(self, initial_state):
        self.initial_state = initial_state
        self.current_state = initial_state
        self.transitions = []
        self.global_before_hooks = []
        self.global_after_hooks = []
        try:
            self._loop = asyncio.get_event_loop()
        except RuntimeError:
            self._loop = None

    def add_transition(self, name, source, target, guard=None, timeout=None, on_enter=None, on_exit=None):
        t = Transition(name, source, target, guard, timeout, on_enter, on_exit)
        self.transitions.append(t)

    def set_global_before_hook(self, hook):
        self.global_before_hooks.append(hook)

    def set_global_after_hook(self, hook):
        self.global_after_hooks.append(hook)

    def apply_guard(self, transition_name, guard):
        for t in self.transitions:
            if t.name == transition_name:
                t.guard = guard

    def define_timeout_event(self, source, target, timeout, name=None):
        name = name or f"{source}_timeout_to_{target}"
        # register the transition with timeout
        self.add_transition(name, source, target, timeout=timeout)
        # schedule an automatic trigger after the timeout
        try:
            loop = self._loop or asyncio.get_event_loop()
            async def _timeout_task():
                await asyncio.sleep(timeout)
                await self.trigger(name)
            loop.create_task(_timeout_task())
        except RuntimeError:
            pass

    def conditional_exec(self, callback, predicate):
        async def wrapper(*args, **kwargs):
            result = predicate(*args, **kwargs)
            if inspect.iscoroutine(result) or inspect.isawaitable(result):
                result = await result
            if result:
                res = callback(*args, **kwargs)
                if inspect.iscoroutine(res) or inspect.isawaitable(res):
                    await res
        return wrapper

    async def trigger(self, event_name):
        for t in self.transitions:
            if t.name == event_name and t.source == self.current_state:
                allow = True
                if t.guard:
                    res = t.guard(self)
                    if inspect.iscoroutine(res) or inspect.isawaitable(res):
                        allow = await res
                    else:
                        allow = res
                if not allow:
                    return False
                for hook in self.global_before_hooks:
                    res = hook(self, t)
                    if inspect.iscoroutine(res) or inspect.isawaitable(res):
                        await res
                if t.on_exit:
                    res = t.on_exit(self)
                    if inspect.iscoroutine(res) or inspect.isawaitable(res):
                        await res
                prev = self.current_state
                self.current_state = t.target
                if t.on_enter:
                    res = t.on_enter(self)
                    if inspect.iscoroutine(res) or inspect.isawaitable(res):
                        await res
                for hook in self.global_after_hooks:
                    res = hook(self, t)
                    if inspect.iscoroutine(res) or inspect.isawaitable(res):
                        await res
                if t.timeout is not None and self._loop:
                    async def timeout_task():
                        await asyncio.sleep(t.timeout)
                        await self.trigger(event_name)
                    self._loop.create_task(timeout_task())
                return True
        return False

def and_guard(*guards):
    async def guard(machine):
        for g in guards:
            res = g(machine)
            if inspect.iscoroutine(res) or inspect.isawaitable(res):
                res = await res
            if not res:
                return False
        return True
    return guard

def or_guard(*guards):
    async def guard(machine):
        for g in guards:
            res = g(machine)
            if inspect.iscoroutine(res) or inspect.isawaitable(res):
                res = await res
            if res:
                return True
        return False
    return guard

def not_guard(guard_func):
    async def guard(machine):
        res = guard_func(machine)
        if inspect.iscoroutine(res) or inspect.isawaitable(res):
            res = await res
        return not res
    return guard
