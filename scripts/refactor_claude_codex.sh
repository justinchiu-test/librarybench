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

# remember where we started
base_dir="$PWD"

echo "Starting refactoring for $directory..."

# Push into the target directory
pushd "$directory" >/dev/null

echo "Following the instructions in $base_dir/REFACTOR_INSTRUCTIONS.md..."

echo "Running claude planner"
# Claude plan
time claude --dangerously-skip-permissions \
  -p "Follow the instructions in $base_dir/REFACTOR_INSTRUCTIONS.md. Only implement PLAN.md. Give the file structure. Do not implement any code."

echo "Running codex impl"
# Codex implement
CODEX_QUIET_MODE=1 time codex --approval-mode full-auto \
  "Read the instructions in $base_dir/REFACTOR_INSTRUCTIONS.md. Follow the implementation plan in PLAN.md."

# Return to original directory
popd >/dev/null

# Run scoring script
echo "Running scoring script..."
python score.py --directory "$directory/unified"

echo "Done!"
