from typing import Any, Callable, Dict, List, Optional, Union


class Transition:
    """
    Represents a transition between states in a state machine.

    Attributes:
        name: A unique identifier for the transition
        from_state: The source state of the transition
        to_state: The destination state of the transition
        trigger: The event that triggers the transition
        guard: Optional conditional function that must return True for the transition to be valid
    """

    def __init__(
        self,
        name: str,
        from_state: Optional[str],
        to_state: str,
        trigger: Optional[str] = None,
        guard: Optional[Callable[..., bool]] = None,
    ):
        self.name = name
        self.from_state = from_state
        self.to_state = to_state
        self.trigger = trigger
        self.guard = guard

    def can_transition(self, *args, **kwargs) -> bool:
        """
        Check if the transition can be executed.

        Returns:
            True if the guard condition passes (or if there is no guard),
            False otherwise.
        """
        if self.guard is None:
            return True
        return self.guard(*args, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the transition to a dictionary representation.

        Returns:
            A dictionary representation of the transition.
        """
        return {
            "name": self.name,
            "from": self.from_state,
            "to": self.to_state,
            "trigger": self.trigger,
            "guard": None,  # Cannot serialize function objects
        }


def compose_guards(*guards: Callable[..., bool], operator: str = "AND") -> Callable[..., bool]:
    """
    Compose multiple guard functions into a single guard function.

    Args:
        *guards: One or more guard functions to compose
        operator: The logical operator to use for composition ('AND', 'OR', or 'NOT')

    Returns:
        A new guard function that combines the results of the input guards
        according to the specified operator.

    Raises:
        ValueError: If an unsupported operator is provided
    """
    if operator == "AND":
        def and_guard(*args, **kwargs):
            return all(guard(*args, **kwargs) for guard in guards)
        return and_guard
    elif operator == "OR":
        def or_guard(*args, **kwargs):
            return any(guard(*args, **kwargs) for guard in guards)
        return or_guard
    elif operator == "NOT":
        if len(guards) != 1:
            raise ValueError("NOT operator requires exactly one guard function")
        guard = guards[0]
        def not_guard(*args, **kwargs):
            return not guard(*args, **kwargs)
        return not_guard
    else:
        raise ValueError(f"Unsupported operator: {operator}. Use 'AND', 'OR', or 'NOT'")