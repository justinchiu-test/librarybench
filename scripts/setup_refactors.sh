#!/bin/bash
# Script to setup refactoring for all projects

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Find all project directories
project_dirs=$(find "$SCRIPT_DIR/../projects" -maxdepth 1 -mindepth 1 -type d)

# Process each project directory
for project_dir in $project_dirs; do
    # Extract the library name from the path
    library_name=$(basename "$project_dir")
    
    echo "Processing $library_name..."
    
    # Run the setup_refactor.py script for this project
    python "$SCRIPT_DIR/setup_refactor.py" "$library_name"
    
    echo "Completed setup for $library_name"
    echo "------------------------------"
done

echo "All projects have been processed."