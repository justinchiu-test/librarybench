#!/bin/bash
# must be run from repo base directory

if [ $# -ne 1 ]; then
    echo "Usage: $0 <directory_name>"
    echo "Example: $0 workflow_orchestration"
    exit 1
fi

directory="$1"
MODEL="o4-mini"

if [ ! -d "$directory" ]; then
    echo "Error: Directory '$directory' does not exist"
    exit 1
fi

# remember where we started
base_dir="$PWD"


# make a copy to refactor
new_directory="${directory}_refactor" 
cp -r $directory $new_directory

# Run scoring script on initial repository
echo "Running scoring script on initial repository..."
python score.py --directory "$directory"

python llm_repo_refactor.py \
  --model "$MODEL" \
  --task setup_for_refactor \
  --starter-repo-path "$new_directory"

echo "Starting refactoring for $directory in $new_directory..."

# Push into the target directory
pushd "$new_directory" >/dev/null
pushd unified >/dev/null

echo "Following the instructions in $base_dir/REFACTOR_INSTRUCTIONS.md..."

echo "Running claude planner"
# Claude plan
time claude --dangerously-skip-permissions \
  -p "Follow the instructions in ../../REFACTOR_INSTRUCTIONS.md. Only write PLAN.md. Give the file structure. Do not implement any code. Do not give example usage code."

# Setup testing environment
uv venv
source .venv/bin/activate
uv pip install -e .

echo "Running codex impl"
# Codex implement
CODEX_QUIET_MODE=1 time codex --approval-mode full-auto \
  "Read the instructions in ../../REFACTOR_INSTRUCTIONS.md. Follow the implementation plan and file structure proposed in PLAN.md. IMPORTANT: Create, modify, and reference files ONLY in this current working subdirectory ($new_directory/unified) and nowhere else. Do NOT import from any other subdirectories in $new_directory except for what is here in unified/. Implement ALL code and update ALL test file imports until this whole subfolder is a functional standalone repository. Do not stop to ask for confirmation; keep going until the final implementation passes all tests using pytest tests/."
# TODO why is codex still sometimes asking for confirmation to keep going?
# TODO how to automatically exit codex when it's done?

popd >/dev/null
# Now that it's been refactored, remove all original persona subdirs
echo "Cleaning up persona directories..."
for d in */; do
  dir=${d%/}
  if [[ "$dir" != "unified" ]]; then
    echo "  → Removing '$dir'"
    rm -rf "$dir"
  fi
done

pushd unified >/dev/null

# TODO maybe a more elgegant way that discourages this failure mode because its expensive
pytest tests/ --json-report --json-report-file=report.json --continue-on-collection-errors > test_output.txt 2>&1

echo "Running final-check codex impl"
# Codex implement
CODEX_QUIET_MODE=1 time codex --approval-mode full-auto \
  "Read the pytest results in test_output.txt. If they indicate pytest failures, fix them. Stick to the implementation plan and file structure proposed in PLAN.md. IMPORTANT: Create and modify files ONLY in this current working subdirectory ($new_directory/unified) and nowhere else. Implement ALL code and update ALL test file imports until this whole subfolder is a functional standalone repository. Do not stop to ask for confirmation; keep going until the final implementation passes all tests using pytest tests/. If there are no errors, exit."

deactivate

# Return to original directory
popd >/dev/null
popd >/dev/null

# Run scoring script
echo "Running scoring script on refactored repository..."
python score.py --directory "$new_directory/unified" --enable_logprobs 

echo "Done!"
