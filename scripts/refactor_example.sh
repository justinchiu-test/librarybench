#!/bin/bash
# must be run from repo base directory

if [ $# -ne 1 ]; then
    echo "Usage: $0 <directory_name>"
    echo "Example: $0 workflow_orchestration"
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

# Run Claude Code and tell it to follow instructions
claude --dangerously-skip-permissions -p "Follow the instructions in $(pwd)/REFACTOR_INSTRUCTIONS.md"

# Pop back to the original directory
popd

# Run scoring script
echo "Running scoring script..."
python score.py --directory "$directory/unified"

echo "Done!"
