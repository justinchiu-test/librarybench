#!/bin/bash

# Script to clean up implementation and test folders from all projects

# Function to cleanup a specific project
cleanup_project() {
    local dir=$1
    local project_name=$(basename "$dir")
    
    echo "Cleaning up $project_name..."
    
    # Remove tests directory
    if [ -d "$dir/tests" ]; then
        echo "  Removing tests directory"
        rm -rf "$dir/tests"
    fi
    
    # Remove implementation files (Python files) but keep INSTRUCTIONS.md
    find "$dir" -type f -not -name "INSTRUCTIONS.md" -not -name "README.md" | while read file; do
        echo "  Removing $file"
        rm "$file"
    done
    
    # Remove any JSON report files
    if [ -f "$dir/pytest_results.json" ]; then
        echo "  Removing pytest_results.json"
        rm "$dir/pytest_results.json"
    fi
    
    # Remove any __pycache__ directories
    find "$dir" -name "__pycache__" -type d | while read cache_dir; do
        echo "  Removing $cache_dir"
        rm -rf "$cache_dir"
    done
    
    echo "  Done cleaning $project_name"
}

# Check for arguments
if [ "$1" = "--all" ]; then
    # Clean all projects
    echo "Cleaning all projects..."
    find /Users/justinchiu/code/librarybench/projects -mindepth 2 -type d | while read project_dir; do
        cleanup_project "$project_dir"
    done
elif [ "$1" = "--project" ] && [ -n "$2" ]; then
    # Clean a specific project
    echo "Cleaning project $2..."
    find /Users/justinchiu/code/librarybench/projects -path "*/$2*" -type d | while read project_dir; do
        cleanup_project "$project_dir"
    done
else
    # Show usage
    echo "Usage:"
    echo "  $0 --all                  # Clean all projects"
    echo "  $0 --project PROJECT_NAME # Clean a specific project (partial name match)"
    echo ""
    echo "Examples:"
    echo "  $0 --all"
    echo "  $0 --project personal_knowledge_management"
    echo "  $0 --project text_editor_writer"
    exit 1
fi

echo "Cleanup complete!"