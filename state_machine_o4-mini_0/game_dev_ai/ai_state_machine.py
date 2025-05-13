import asyncio

class Transition:
    def __init__(self, source, event, target, guard=None, action=None):
        self.source = source
        self.event = event
        self.target = target
        self.guard = guard
        self.action = action

class StateMachine:
    def __init__(self, initial_state, loop=None):
        self.states = {}
        self.transitions = {}
        self.current_state = initial_state
        self.global_before_hooks = []
        self.global_after_hooks = []
        self.loop = loop or asyncio.get_event_loop()
        self.timeout_tasks = []
        self.regions = {}
        self.blackboard = {}
        # register initial state
        self.states[initial_state] = {'on_enter': None, 'on_exit': None}

    def add_state(self, name, on_enter=None, on_exit=None):
        self.states[name] = {'on_enter': on_enter, 'on_exit': on_exit}

    def add_transition(self, source, event, target, guard=None, action=None):
        if source not in self.states:
            raise ValueError(f"Unknown source state {source}")
        t = Transition(source, event, target, guard, action)
        self.transitions.setdefault(source, []).append(t)

    def before_transition_global(self, hook):
        self.global_before_hooks.append(hook)

    def after_transition_global(self, hook):
        self.global_after_hooks.append(hook)

    def define_parallel_regions(self, region_name, machine):
        self.regions[region_name] = machine

    def add_timeout_transition(self, source, timeout, event, target):
        # add the transition
        self.add_transition(source, event, target)
        # wrap on_enter to schedule timeout
        orig_on_enter = self.states[source].get('on_enter')
        async def on_enter_wrapper(context=None):
            if orig_on_enter:
                res = orig_on_enter(context)
                if asyncio.iscoroutine(res):
                    await res
            async def schedule():
                await asyncio.sleep(timeout)
                await self.handle_event(event, context)
            task = self.loop.create_task(schedule())
            self.timeout_tasks.append(task)
        self.states[source]['on_enter'] = on_enter_wrapper

    async def handle_event(self, event, context=None):
        # propagate to parallel regions
        for region in self.regions.values():
            await region.handle_event(event, context)
        # handle in this machine
        trans_list = self.transitions.get(self.current_state, [])
        for t in trans_list:
            if t.event == event:
                guard_ok = True
                if t.guard:
                    result = t.guard(context)
                    if asyncio.iscoroutine(result):
                        result = await result
                    guard_ok = result
                if guard_ok:
                    # before hooks
                    for hook in self.global_before_hooks:
                        res = hook(self.current_state, t.target, event, context)
                        if asyncio.iscoroutine(res):
                            await res
                    # on_exit of current state
                    on_exit = self.states[self.current_state].get('on_exit')
                    if on_exit:
                        res = on_exit(context)
                        if asyncio.iscoroutine(res):
                            await res
                    # transition action
                    if t.action:
                        res = t.action(context)
                        if asyncio.iscoroutine(res):
                            await res
                    old = self.current_state
                    self.current_state = t.target
                    # on_enter of new state
                    on_enter = self.states[self.current_state].get('on_enter')
                    if on_enter:
                        res = on_enter(context)
                        if asyncio.iscoroutine(res):
                            await res
                    # after hooks
                    for hook in self.global_after_hooks:
                        res = hook(old, self.current_state, event, context)
                        if asyncio.iscoroutine(res):
                            await res
                    return True
        return False
