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

# make a copy to refactor
new_directory="${directory}_refactor" 
cp -r $directory $new_directory

echo "Starting refactoring for $directory in $new_directory..."

# Push into the target directory
pushd "$new_directory" >/dev/null

echo "Following the instructions in $base_dir/REFACTOR_INSTRUCTIONS.md..."

echo "Running claude planner"
# Claude plan
time claude --dangerously-skip-permissions \
  -p "Follow the instructions in $base_dir/REFACTOR_INSTRUCTIONS.md. Only write unified/PLAN.md. Give the file structure. Do not implement any code. Do not give example usage code."

echo "Running codex impl"
# Codex implement
CODEX_QUIET_MODE=1 time codex --approval-mode full-auto \
  "Read the instructions in $base_dir/REFACTOR_INSTRUCTIONS.md. Follow the implementation plan in unified/PLAN.md. IMPORTANT: Place ALL implementation code in the unified/src/ directory. Create and modify files ONLY in unified/ and nowhere else. ALL source code MUST be in unified/src/. Implement ALL code and update ALL test file imports until the whole unified/ folder is a functional standalone repository. Do not stop to ask for confirmation; keep going until the final implementation passes all unified/tests."
# TODO why is codex still sometimes asking for confirmation to keep going?
# TODO how to automatically exit codex when it's done?

pytest unified/tests/  --json-report --json-report-file=report.json --continue-on-collection-errors > test_output.txt 2>&1

# Return to original directory
popd >/dev/null

# Run scoring script
echo "Running scoring script..."
python score.py --directory "$new_directory/unified"

echo "Done!"
