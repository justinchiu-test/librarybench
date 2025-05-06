from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Callable, Tuple, Dict

class TaskState(Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    SUCCESS = 'success'
    FAILURE = 'failure'

@dataclass(order=True)
class Task:
    # For priority queue: higher priority tasks first, so we invert priority in manager
    priority: int
    id: str = field(compare=False)
    func: Callable[..., Any] = field(compare=False)
    args: Tuple[Any, ...] = field(default_factory=tuple, compare=False)
    kwargs: Dict[str, Any] = field(default_factory=dict, compare=False)
    retry_policy: 'RetryPolicy' = field(default=None, compare=False)
    state: TaskState = field(default=TaskState.PENDING, compare=False)
    retries_done: int = field(default=0, compare=False)
    result: Any = field(default=None, compare=False)

@dataclass
class RetryPolicy:
    max_retries: int = 0
    retry_delay_seconds: float = 0.0
