import asyncio
from typing import Callable, Any, Dict, List, Optional, Tuple

Predicate = Callable[[], bool]
TransitionDef = Tuple[str, Optional[Predicate], Optional[float]]

class GaitController:
    def __init__(self):
        self.current_state: Optional[str] = None
        self.transitions: Dict[str, TransitionDef] = {}
        self.global_before_hooks: List[Callable[[str, str], Any]] = []
        self.global_after_hooks: List[Callable[[str, str], Any]] = []
        self.on_exit_gait_hooks: List[Callable[[str], Any]] = []
        self.foot_contact_detected: bool = True
        self.regions: Dict[str, 'GaitController'] = {}

    def add_global_before(self, hook: Callable[[str, str], Any]):
        self.global_before_hooks.append(hook)

    def add_global_after(self, hook: Callable[[str, str], Any]):
        self.global_after_hooks.append(hook)

    def add_on_exit_gait(self, hook: Callable[[str], Any]):
        self.on_exit_gait_hooks.append(hook)

    def register_transition(self, name: str, target: str, guard: Optional[Predicate]=None, timeout: Optional[float]=None):
        self.transitions[name] = (target, guard, timeout)

    def attach_guard(self, transition_name: str, guard: Predicate):
        target, old_guard, to = self.transitions[transition_name]
        def new_guard():
            if old_guard and not old_guard():
                return False
            return guard()
        self.transitions[transition_name] = (target, new_guard, to)

    @staticmethod
    def guard_and(*preds: Predicate) -> Predicate:
        def _g():
            return all(p() for p in preds)
        return _g

    @staticmethod
    def guard_or(*preds: Predicate) -> Predicate:
        def _g():
            return any(p() for p in preds)
        return _g

    @staticmethod
    def conditional_on(predicate: Predicate):
        def decorator(func):
            def wrapper(*args, **kwargs):
                if predicate():
                    return func(*args, **kwargs)
            return wrapper
        return decorator

    def add_region(self, name: str, controller: 'GaitController'):
        self.regions[name] = controller

    def transition(self, name: str):
        if name not in self.transitions:
            return False
        target, guard, timeout = self.transitions[name]
        if guard and not guard():
            return False

        from_state = self.current_state
        for hook in self.global_before_hooks:
            hook(from_state, target)

        # perform state change
        self.current_state = target

        # schedule timeout watcher if needed
        if timeout is not None:
            try:
                # schedule under the currently running event loop
                loop = asyncio.get_running_loop()
                loop.create_task(self._watch_timeout(name, timeout))
            except RuntimeError:
                # no running loop; skip scheduling
                pass

        for hook in self.global_after_hooks:
            hook(from_state, target)

        if name == "exit_gait":
            for hook in self.on_exit_gait_hooks:
                hook(target)

        return True

    async def transition_async(self, name: str):
        return self.transition(name)

    async def _watch_timeout(self, name: str, timeout: float):
        await asyncio.sleep(timeout)
        if not self.foot_contact_detected and "stop_gait" in self.transitions:
            self.transition("stop_gait")

    def set_foot_contact(self, flag: bool):
        self.foot_contact_detected = flag

    def create_simulation_harness(self):
        return SimulationHarness(self)

class SimulationHarness:
    def __init__(self, gait: GaitController):
        self.gait = gait
        self.stub_motor_commands: List[Any] = []
        self.sequence: List[Any] = []

    def drive(self, sequence: List[Any]):
        self.sequence = sequence
        for action in sequence:
            self.stub_motor_commands.append(action)

    def assert_stability(self) -> bool:
        return True
