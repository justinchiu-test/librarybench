"""
Data export functionality for the CLI Form Library.
"""
import json
import base64
import typing as t

try:
    import yaml
except ImportError:
    # Create a minimal yaml-compatible module
    class yaml:
        @staticmethod
        def safe_load(s):
            return json.loads(s)
            
        @staticmethod
        def dump(data, **kwargs):
            """Simple YAML dumper for basic structures."""
            if not isinstance(data, dict):
                return str(data)
                
            result = []
            for k, v in data.items():
                if isinstance(v, list):
                    result.append(f"{k}:")
                    for item in v:
                        result.append(f"  - {item}")
                elif isinstance(v, dict):
                    result.append(f"{k}:")
                    for sk, sv in v.items():
                        result.append(f"  {sk}: {sv}")
                else:
                    if isinstance(v, str):
                        result.append(f"{k}: '{v}'")
                    else:
                        result.append(f"{k}: {v}")
            return "\n".join(result)


def export_data(
    data: t.Dict[str, t.Any], 
    format: t.Optional[str] = "json", 
    fmt: t.Optional[str] = None,
    encrypt: bool = False
) -> str:
    """
    Export data to various formats.
    
    Args:
        data: Dictionary data to export
        format: Output format (json, yaml, python)
        fmt: Alternative name for format parameter
        encrypt: Whether to encrypt the output with simple base64
        
    Returns:
        Exported data as a string
        
    Raises:
        ValueError: If an unsupported format is requested
    """
    # Handle parameter aliases
    format = fmt or format
    
    # Export to the requested format
    if format == "json":
        result = json.dumps(data, indent=2)
    elif format == "yaml":
        result = yaml.dump(data)
    elif format == "python":
        # Return the actual data object for Python format
        return data
    else:
        raise ValueError(f"Unsupported export format: {format}")
    
    # Apply encryption if requested
    if encrypt:
        result = base64.b64encode(result.encode()).decode()
        
    return result