import json
import os
import configparser

def parse_config_files(file_paths):
    """
    Parse configuration files in various formats.
    
    Args:
        file_paths: List of paths to configuration files
        
    Returns:
        dict: Merged configuration from all parsed files
    """
    result = {}
    
    for file_path in file_paths:
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.json':
            with open(file_path, 'r') as f:
                config = json.load(f)
                result.update(config)
        elif ext == '.ini':
            config = configparser.ConfigParser()
            config.read(file_path)
            # Convert ConfigParser to dict
            for section in config.sections():
                if section not in result:
                    result[section] = {}
                for key, val in config[section].items():
                    result[section][key] = val
        # Skip unknown file types
        
    return result