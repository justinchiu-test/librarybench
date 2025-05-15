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

uv venv
source .venv/bin/activate

pip install -e .

echo "Following the instructions in $(pwd)/REFACTOR.md..."
# Run Claude Code and tell it to follow instructions
time claude -r "$directory" --dangerously-skip-permissions -p "Follow the instructions in $(pwd)/REFACTOR.md"
time claude -r "$directory" --dangerously-skip-permissions -p "Follow the instructions in $(pwd)/REFACTOR.md. Be sure to complete the migrations."
time claude -r "$directory" --dangerously-skip-permissions -p "Follow the instructions in $(pwd)/REFACTOR.md. Be sure to complete the migrations."

deactivate

# Pop back to the original directory
popd

echo "Done!"
