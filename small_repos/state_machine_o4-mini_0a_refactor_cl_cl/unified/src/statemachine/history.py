from typing import Any, Dict, List, Optional, Set, Union


class HistoryManager:
    """
    Manages history tracking, undo/redo operations for a state machine.
    
    Supports different history modes:
    - shallow: Tracks only the most recent state
    - deep: Tracks the full history of states
    """

    def __init__(self):
        # Undo and redo stacks
        self.undo_stack: List[Any] = []
        self.redo_stack: List[Any] = []
        
        # History tracking settings
        self.history_modes: Dict[str, str] = {}  # Group name -> mode
        self.history_states: Dict[str, Dict[str, Any]] = {}  # Group name -> state history

    def enable_history(self, group_name: str, mode: str = "shallow") -> Dict[str, str]:
        """
        Enable history tracking for a named group of states.

        Args:
            group_name: The name of the state group to track
            mode: The history tracking mode ('shallow' or 'deep')

        Returns:
            The updated history modes dictionary
        """
        if mode not in ["shallow", "deep", "full"]:
            raise ValueError(f"Unsupported history mode: {mode}")
        
        self.history_modes[group_name] = mode
        self.history_states[group_name] = {}
        
        return self.history_modes

    def get_history_modes(self) -> Dict[str, str]:
        """
        Get all history tracking modes.
        
        Returns:
            A dictionary mapping group names to history modes
        """
        return self.history_modes

    def push_undo(self, event: Any) -> None:
        """
        Push an event onto the undo stack.

        Args:
            event: The event to push onto the stack
        """
        self.undo_stack.append(event)
        # Clear redo stack when a new action is performed
        self.redo_stack.clear()

    def pop_undo(self) -> Optional[Any]:
        """
        Pop the most recent event from the undo stack and add it to the redo stack.

        Returns:
            The most recent event, or None if the undo stack is empty
        """
        if not self.undo_stack:
            return None
        
        event = self.undo_stack.pop()
        self.redo_stack.append(event)
        return event

    def pop_redo(self) -> Optional[Any]:
        """
        Pop the most recent event from the redo stack and add it to the undo stack.

        Returns:
            The most recent event, or None if the redo stack is empty
        """
        if not self.redo_stack:
            return None
        
        event = self.redo_stack.pop()
        self.undo_stack.append(event)
        return event

    def get_undo_stack(self) -> List[Any]:
        """
        Get the current undo stack.

        Returns:
            The current undo stack
        """
        return self.undo_stack

    def get_redo_stack(self) -> List[Any]:
        """
        Get the current redo stack.

        Returns:
            The current redo stack
        """
        return self.redo_stack

    def to_dict(self) -> Dict[str, Any]:
        """
        Create a dictionary representation of the history manager.

        Returns:
            A dictionary containing history settings
        """
        return {
            "history_modes": self.history_modes.copy(),
            "undo_stack_size": len(self.undo_stack),
            "redo_stack_size": len(self.redo_stack)
        }