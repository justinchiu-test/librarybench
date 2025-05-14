from typing import Any, Callable, Dict, List, Optional, Union


class HookManager:
    """
    Manages hooks (callbacks) for state machine events.

    Hooks can be registered for:
    - Global events (before/after transitions)
    - State entry/exit events
    """

    def __init__(self):
        # Initialize empty hook dictionaries
        self.global_hooks: Dict[str, List[Callable]] = {
            "before": [],  # Called before a transition
            "after": [],   # Called after a transition
        }
        self.state_hooks: Dict[str, Dict[str, List[Callable]]] = {
            "enter": {},   # Called when entering a state
            "exit": {},    # Called when exiting a state
        }

    def add_global_hook(self, hook_type: str, callback: Callable) -> None:
        """
        Register a global hook callback.

        Args:
            hook_type: The type of hook ('before' or 'after')
            callback: The function to call when the hook is triggered

        Raises:
            ValueError: If hook_type is not supported
        """
        if hook_type not in self.global_hooks:
            raise ValueError(f"Unsupported global hook type: {hook_type}")
        self.global_hooks[hook_type].append(callback)

    def add_state_hook(self, hook_type: str, state: str, callback: Callable) -> None:
        """
        Register a state-specific hook callback.

        Args:
            hook_type: The type of hook ('enter' or 'exit')
            state: The state to hook into
            callback: The function to call when the hook is triggered

        Raises:
            ValueError: If hook_type is not supported
        """
        if hook_type not in self.state_hooks:
            raise ValueError(f"Unsupported state hook type: {hook_type}")
        
        if state not in self.state_hooks[hook_type]:
            self.state_hooks[hook_type][state] = []
        
        self.state_hooks[hook_type][state].append(callback)

    def trigger_global_hook(self, hook_type: str, transition_info: Dict[str, Any]) -> None:
        """
        Trigger all global hooks of a specific type.

        Args:
            hook_type: The type of hook to trigger
            transition_info: Information about the transition to pass to callbacks
        """
        if hook_type in self.global_hooks:
            for callback in self.global_hooks[hook_type]:
                # Try different parameter combinations based on the callback's expected signature
                try:
                    # Try passing just the transition info
                    callback(transition_info)
                except TypeError:
                    try:
                        # Try unpacking the trigger, from_state, and to_state
                        callback(transition_info.get("trigger"), 
                                transition_info.get("from"), 
                                transition_info.get("to"))
                    except TypeError:
                        try:
                            # Try passing machine, event, transition_info (game_developer style)
                            callback(None, transition_info.get("trigger"), transition_info)
                        except TypeError:
                            # Fallback: just call without parameters
                            callback()

    def trigger_state_hook(self, hook_type: str, state: str, transition_info: Dict[str, Any]) -> None:
        """
        Trigger all state hooks of a specific type for a specific state.

        Args:
            hook_type: The type of hook to trigger
            state: The state whose hooks to trigger
            transition_info: Information about the transition to pass to callbacks
        """
        if hook_type in self.state_hooks and state in self.state_hooks[hook_type]:
            for callback in self.state_hooks[hook_type][state]:
                # Try different parameter combinations based on the callback's expected signature
                try:
                    # Try with no arguments (ux_prototyper style)
                    callback()
                except TypeError:
                    try:
                        # Try passing just the transition info
                        callback(transition_info)
                    except TypeError:
                        try:
                            # Try passing event and state
                            callback(transition_info.get("trigger"), state)
                        except TypeError:
                            try:
                                # Try passing machine, event, transition info (game_developer style)
                                callback(None, transition_info.get("trigger"), transition_info)
                            except TypeError:
                                # Last resort: try with empty params
                                callback()

    def to_dict(self) -> Dict[str, Any]:
        """
        Create a dictionary representation of the hooks configuration.

        Returns:
            A dictionary containing hook counts (functions cannot be serialized)
        """
        result = {
            "global_hooks": {
                hook_type: len(hooks) for hook_type, hooks in self.global_hooks.items()
            },
            "state_hooks": {
                hook_type: {
                    state: len(callbacks)
                    for state, callbacks in states.items()
                }
                for hook_type, states in self.state_hooks.items()
            }
        }
        return result