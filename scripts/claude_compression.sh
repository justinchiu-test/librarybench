#!/bin/bash
# must be run from the unified project directory

if [ $# -ne 1 ]; then
    echo "Usage: $0 <directory_name>"
    echo "Example: $0 projects/text_editor/unified"
    exit 1
fi

directory="$1"

if [ ! -d "$directory" ]; then
    echo "Error: Directory '$directory' does not exist"
    exit 1
fi

echo "Starting refactoring for $directory..."

# Push into the directory
pushd "$directory"

echo "Following the instructions in $(pwd)/REFACTOR.md..."
# Run Claude Code and tell it to follow instructions
time claude --dangerously-skip-permissions -p "Follow the instructions in $(pwd)/REFACTOR.md"

# Pop back to the original directory
popd

echo "Done!"
