#!/usr/bin/env python3
"""
Script to update import paths in test files.
Converts:
- from backend_dev.XXX import YYY -> from src.personas.backend_dev.XXX import YYY
- from data_scientist.XXX import YYY -> from src.personas.data_scientist.XXX import YYY
- from ops_engineer.XXX import YYY -> from src.personas.ops_engineer.XXX import YYY
- from translator.XXX import YYY -> from src.personas.translator.XXX import YYY
- from localization_manager.XXX import YYY -> from src.personas.localization_manager.XXX import YYY
"""

import os
import re
import sys

def update_imports(file_path):
    """Update imports in a file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Define the import patterns to replace
    patterns = [
        # backend_dev imports
        (r'from backend_dev\.([a-zA-Z0-9_.]+) import ([a-zA-Z0-9_, ]+)', 
         r'from src.personas.backend_dev.\1 import \2'),
        (r'import backend_dev\.([a-zA-Z0-9_.]+)', 
         r'import src.personas.backend_dev.\1'),
        
        # data_scientist imports
        (r'from data_scientist\.([a-zA-Z0-9_.]+) import ([a-zA-Z0-9_, ]+)', 
         r'from src.personas.data_scientist.\1 import \2'),
        (r'import data_scientist\.([a-zA-Z0-9_.]+)', 
         r'import src.personas.data_scientist.\1'),
        
        # ops_engineer imports
        (r'from ops_engineer\.([a-zA-Z0-9_.]+) import ([a-zA-Z0-9_, ]+)', 
         r'from src.personas.ops_engineer.\1 import \2'),
        (r'import ops_engineer\.([a-zA-Z0-9_.]+)', 
         r'import src.personas.ops_engineer.\1'),
        
        # translator imports
        (r'from translator\.([a-zA-Z0-9_.]+) import ([a-zA-Z0-9_, ]+)', 
         r'from src.personas.translator.\1 import \2'),
        (r'import translator\.([a-zA-Z0-9_.]+)', 
         r'import src.personas.translator.\1'),
        
        # localization_manager imports
        (r'from localization_manager\.([a-zA-Z0-9_.]+) import ([a-zA-Z0-9_, ]+)', 
         r'from src.personas.localization_manager.\1 import \2'),
        (r'import localization_manager\.([a-zA-Z0-9_.]+)', 
         r'import src.personas.localization_manager.\1'),
    ]
    
    # Apply each pattern
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # Write the updated content back to the file
    with open(file_path, 'w') as f:
        f.write(content)

def main():
    """Main function."""
    test_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    # Get all Python files in the tests directory
    for filename in os.listdir(test_dir):
        if filename.endswith('.py'):
            file_path = os.path.join(test_dir, filename)
            print(f"Updating imports in {filename}...")
            update_imports(file_path)
    
    print("Done!")

if __name__ == '__main__':
    main()