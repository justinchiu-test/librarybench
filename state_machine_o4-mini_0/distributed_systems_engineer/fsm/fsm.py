import asyncio

class FSM:
    def __init__(self, initial_state):
        self.state = initial_state
        self.transitions = {}  # (from_state, event): {to, guard, callback}
        self.global_before = []
        self.global_after = []
        self.exit_callbacks = {}
        self.timeout_configs = {}  # state: (timeout, timeout_event, to_state)
        self.timeout_tasks = {}
        self.regions = {}
        self.context = {}

    def add_transition(self, from_state, event, to_state, guard=None, callback=None):
        self.transitions[(from_state, event)] = {
            'to': to_state,
            'guard': guard,
            'callback': callback
        }

    def add_guard_function(self, from_state, event, guard):
        tr = self.transitions.get((from_state, event))
        if tr:
            tr['guard'] = guard

    def register_global_before(self, callback):
        self.global_before.append(callback)

    def register_global_after(self, callback):
        self.global_after.append(callback)

    def exit_callback(self, state, callback):
        self.exit_callbacks.setdefault(state, []).append(callback)

    def timeout_transition(self, state, timeout, event, to_state):
        self.timeout_configs[state] = (timeout, event, to_state)

    def add_region(self, name, fsm):
        self.regions[name] = fsm

    def compose_guards_logic(self, logic, *guards):
        async def _guard(ctx):
            results = []
            for g in guards:
                r = g(ctx)
                if asyncio.iscoroutine(r):
                    r = await r
                results.append(r)
            if logic == 'AND':
                return all(results)
            if logic == 'OR':
                return any(results)
            if logic == 'NOT':
                return not results[0]
            raise ValueError("Unknown logic")
        return _guard

    def conditional_callback(self, key, callback):
        async def _wrapped(ctx):
            if ctx.get(key):
                r = callback(ctx)
                if asyncio.iscoroutine(r):
                    await r
        return _wrapped

    async def _run_timeout(self, state):
        timeout, event, to_state = self.timeout_configs[state]
        await asyncio.sleep(timeout)
        if self.state == state:
            await self.trigger(event, forced_to=to_state)

    async def trigger(self, event, forced_to=None):
        # propagate to regions
        for region in self.regions.values():
            await region.trigger(event)
        key = (self.state, event)
        tr = self.transitions.get(key)
        if not tr and not forced_to:
            return False
        to_state = forced_to or tr['to']
        guard = tr.get('guard') if tr else (lambda ctx: True)
        callback = tr.get('callback') if tr else None
        # check guard
        ok = True
        if guard:
            res = guard(self.context)
            if asyncio.iscoroutine(res):
                ok = await res
            else:
                ok = res
        if not ok:
            return False
        # global before
        for cb in self.global_before:
            r = cb(self.context)
            if asyncio.iscoroutine(r):
                await r
        # exit callbacks
        for cb in self.exit_callbacks.get(self.state, []):
            r = cb(self.context)
            if asyncio.iscoroutine(r):
                await r
        old_state = self.state
        self.state = to_state
        # cancel old timeout
        task = self.timeout_tasks.pop(old_state, None)
        if task:
            task.cancel()
        # schedule timeout for new state
        if to_state in self.timeout_configs:
            task = asyncio.create_task(self._run_timeout(to_state))
            self.timeout_tasks[to_state] = task
        # transition callback
        if callback:
            r = callback(self.context)
            if asyncio.iscoroutine(r):
                await r
        # global after
        for cb in self.global_after:
            r = cb(self.context)
            if asyncio.iscoroutine(r):
                await r
        return True
