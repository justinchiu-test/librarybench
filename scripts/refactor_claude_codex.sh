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

echo "Following the instructions in $(pwd)/REFACTOR_INSTRUCTIONS.md..."

# Claude plan
claude --dangerously-skip-permissions -p "Follow the instructions in $(pwd)/REFACTOR_INSTRUCTIONS.md. Only implement PLAN.md. Give the file structure. Do not implement any code."

# Codex implement
CODEX_QUIET_MODE=1 codex --approval-mode full-auto "Read the instructions in $(pwd)/REFACTOR_INSTRUCTIONS.md. Follow the implementation plan in PLAN.md."

# Pop back to the original directory
popd

# Run scoring script
echo "Running scoring script..."
python score.py --directory "$directory/unified"

echo "Done!"
