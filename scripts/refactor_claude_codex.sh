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

# Setup testing environment
pushd unified >/dev/null
uv venv
source .venv/bin/activate
uv pip install -e .
popd >/dev/null

echo "Running codex impl"
# Codex implement
CODEX_QUIET_MODE=1 time codex --approval-mode full-auto \
  "Read the instructions in $base_dir/REFACTOR_INSTRUCTIONS.md. Follow the implementation plan in unified/PLAN.md to re-write source code into a sinfle unified codebase with shared abstracted utils functions. IMPORTANT: Create and modify files ONLY in unified/ and nowhere else. ALL source code MUST be in unified/src/. Do NOT import from any other subdirectories in $new_directory except for what is in unified/. Implement ALL code and update ALL test file imports until the whole unified/ folder is a functional standalone repository. Do not stop to ask for confirmation; keep going until the final implementation passes all unified/tests using pytest unified/tests/."
# TODO why is codex still sometimes asking for confirmation to keep going?
# TODO how to automatically exit codex when it's done?

# Now that it's been refactored, remove all original persona subdirs
echo "Cleaning up persona directories..."
for d in */; do
  dir=${d%/}
  if [[ "$dir" != "unified" ]]; then
    echo "  → Removing '$dir'"
    rm -rf "$dir"
  fi
done

# TODO maybe a more elgegant way that discourages this failure mode because its expensive
pytest unified/tests/ --json-report --json-report-file=report.json --continue-on-collection-errors > test_output.txt 2>&1

echo "Running final-check codex impl"
# Codex implement
CODEX_QUIET_MODE=1 time codex --approval-mode full-auto \
  "Read the pytest results in test_output.txt. If they indicate failures in the unified/ subdirectory, fix them. Try to stick to the implementation plan in unified/PLAN.md. IMPORTANT: Create and modify files ONLY in unified/ and nowhere else. ALL source code MUST be in unified/src/. Do NOT import from any other subdirectories in $new_directory except for what is in unified/. Implement ALL code and update ALL test file imports until the whole unified/ folder is a functional standalone repository. Do not stop to ask for confirmation; keep going until the final implementation passes all unified/tests using pytest unified/tests/. If there are no errors, exit."

deactivate

# Return to original directory
popd >/dev/null

# Run scoring script
echo "Running scoring script..."
python score.py --directory "$new_directory/unified"

echo "Done!"
