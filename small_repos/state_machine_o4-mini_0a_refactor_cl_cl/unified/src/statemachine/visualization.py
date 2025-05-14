import os
from typing import Any, Dict, List, Optional, Set, Tuple, Union


class VisualizationManager:
    """
    Manages visualization exports for state machines.
    
    Supports various formats:
    - DOT (GraphViz)
    - Interactive (JSON-based)
    """

    @staticmethod
    def to_dot(states: Set[str], transitions: List[Dict[str, Any]], 
              current_state: Optional[str] = None) -> str:
        """
        Generate a DOT format representation of the state machine.

        Args:
            states: Set of state names
            transitions: List of transition dictionaries
            current_state: The current state of the machine (highlighted if provided)

        Returns:
            A DOT format string representation of the state machine
        """
        dot = ["digraph StateMachine {"]
        dot.append("  rankdir=LR;")
        dot.append("  node [shape=circle];")
        
        # Add states
        for state in states:
            attrs = []
            if state == current_state:
                attrs.append('style=filled')
                attrs.append('fillcolor=lightblue')
            
            attr_str = ", ".join(attrs) if attrs else ""
            dot.append(f'  "{state}" [{attr_str}];')
        
        # Add transitions
        for t in transitions:
            if t["from"] is not None and t["to"] is not None:
                label = t["trigger"] if t["trigger"] else t["name"]
                dot.append(f'  "{t["from"]}" -> "{t["to"]}" [label="{label}"];')
        
        dot.append("}")
        return "\n".join(dot)

    @staticmethod
    def to_interactive(states: Set[str], transitions: List[Dict[str, Any]], 
                      current_state: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate an interactive visualization representation of the state machine.

        Args:
            states: Set of state names
            transitions: List of transition dictionaries
            current_state: The current state of the machine

        Returns:
            A dictionary that can be used for interactive visualization
        """
        nodes = []
        edges = []
        
        for state in states:
            nodes.append({
                "id": state,
                "label": state,
                "current": state == current_state
            })
        
        for t in transitions:
            if t["from"] is not None and t["to"] is not None:
                trigger = t["trigger"] if t["trigger"] else t["name"]
                edges.append((t["from"], t["to"], trigger))
        
        return {
            "nodes": nodes,
            "edges": edges
        }

    @staticmethod
    def export_to_file(content: str, file_path: str) -> str:
        """
        Export visualization content to a file.

        Args:
            content: The visualization content
            file_path: The path to save the file to

        Returns:
            The absolute path to the saved file
        """
        dir_path = os.path.dirname(file_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
            
        with open(file_path, 'w') as f:
            f.write(content)
            
        return os.path.abspath(file_path)