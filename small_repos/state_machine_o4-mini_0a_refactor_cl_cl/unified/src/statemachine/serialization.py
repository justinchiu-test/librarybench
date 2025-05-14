import json
from typing import Any, Dict, List, Optional, Set, Union


class SerializationManager:
    """
    Manages serialization and deserialization of state machine data.
    
    Supports various formats: dict, JSON, YAML
    """

    @staticmethod
    def to_dict(states: Set[str], transitions: List[Dict[str, Any]], 
               current_state: Optional[str], history_modes: Dict[str, str]) -> Dict[str, Any]:
        """
        Convert state machine data to a dictionary representation.

        Args:
            states: Set of state names
            transitions: List of transition dictionaries
            current_state: The current state of the machine
            history_modes: Dictionary of history tracking modes

        Returns:
            A dictionary representation of the state machine
        """
        return {
            "states": list(states),
            "transitions": transitions,
            "current_state": current_state,
            "history_settings": history_modes
        }

    @staticmethod
    def to_json(data: Dict[str, Any]) -> str:
        """
        Convert a dictionary to a JSON string.

        Args:
            data: The dictionary to convert

        Returns:
            A JSON string representation
        """
        return json.dumps(data, indent=2)

    @staticmethod
    def from_json(json_str: str) -> Dict[str, Any]:
        """
        Convert a JSON string to a dictionary.

        Args:
            json_str: The JSON string to parse

        Returns:
            A dictionary parsed from the JSON string
        """
        return json.loads(json_str)

    @staticmethod
    def to_yaml(data: Dict[str, Any]) -> str:
        """
        Convert a dictionary to a YAML string.
        
        This is a basic implementation using indentation to create YAML,
        without external dependencies.

        Args:
            data: The dictionary to convert

        Returns:
            A YAML string representation
        """
        def _dict_to_yaml(d, indent=0):
            yaml_str = ""
            if isinstance(d, dict):
                if not d:
                    return "{}\n"
                for key, value in d.items():
                    yaml_str += ' ' * indent + f"{key}:"
                    if isinstance(value, dict):
                        yaml_str += "\n" + _dict_to_yaml(value, indent + 2)
                    elif isinstance(value, list):
                        if not value:
                            yaml_str += " []\n"
                        else:
                            yaml_str += "\n"
                            for item in value:
                                if isinstance(item, dict):
                                    yaml_str += ' ' * (indent + 2) + "- "
                                    first_key = True
                                    for k, v in item.items():
                                        if first_key:
                                            yaml_str += f"{k}: {v}\n"
                                            first_key = False
                                        else:
                                            yaml_str += ' ' * (indent + 4) + f"{k}: {v}\n"
                                else:
                                    yaml_str += ' ' * (indent + 2) + f"- {item}\n"
                    else:
                        yaml_str += f" {value}\n"
            return yaml_str

        return _dict_to_yaml(data)

    @staticmethod
    def from_yaml(yaml_str: str) -> Dict[str, Any]:
        """
        Parse a YAML string into a dictionary.
        
        This implementation is minimal and doesn't handle all YAML features.
        In a real implementation, we might use PyYAML, but for simplicity
        and to avoid dependencies, we use a custom YAML parser.

        Args:
            yaml_str: The YAML string to parse

        Returns:
            A dictionary parsed from the YAML string
        """
        # For simplicity, convert YAML to JSON-like structure
        # This is a very basic implementation and doesn't handle all YAML features
        lines = yaml_str.split("\n")
        result = {}
        
        def parse_yaml_lines(lines, indent=0):
            result = {}
            i = 0
            while i < len(lines):
                line = lines[i].rstrip()
                if not line or line.lstrip().startswith("#"):
                    i += 1
                    continue
                
                # Skip lines with less indentation than current level
                current_indent = len(line) - len(line.lstrip())
                if current_indent < indent:
                    break
                
                if current_indent > indent:
                    i += 1
                    continue
                
                # Parse key-value pair
                parts = line[indent:].split(":", 1)
                if len(parts) == 2:
                    key, value = parts[0].strip(), parts[1].strip()
                    if not value:  # Nested structure
                        nested = {}
                        j = i + 1
                        while j < len(lines):
                            next_line = lines[j].rstrip()
                            if not next_line:
                                j += 1
                                continue
                            next_indent = len(next_line) - len(next_line.lstrip())
                            if next_indent <= indent:
                                break
                            j += 1
                        
                        # If the next line is indented, parse nested structure
                        if j > i + 1:
                            nested_lines = lines[i+1:j]
                            result[key] = parse_yaml_lines(nested_lines, indent + 2)
                            i = j - 1
                        else:
                            result[key] = {}
                    elif value.startswith("[") and value.endswith("]"):  # List notation
                        items = value[1:-1].split(",")
                        result[key] = [item.strip() for item in items if item.strip()]
                    else:
                        try:
                            # Try to convert to appropriate type
                            if value.lower() == "true":
                                result[key] = True
                            elif value.lower() == "false":
                                result[key] = False
                            elif value.lower() == "null" or value.lower() == "none":
                                result[key] = None
                            elif value.isdigit():
                                result[key] = int(value)
                            elif value.replace(".", "", 1).isdigit() and value.count(".") == 1:
                                result[key] = float(value)
                            else:
                                result[key] = value
                        except (ValueError, TypeError):
                            result[key] = value
                i += 1
            return result
        
        return parse_yaml_lines(lines)