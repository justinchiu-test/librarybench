#!/bin/bash

# Set maximum number of parallel processes
MAX_PARALLEL=6

# Function to process an instruction file
process_instruction() {
    local instruction_path=$1
    local project_dir=$(dirname "$instruction_path")
    local project_name=$(basename "$project_dir" | cut -d'_' -f1)
    local persona=$(basename "$project_dir" | cut -d'_' -f2-)
    
    echo "Implementing: $project_name for persona: $persona"
    
    # Create test directory if it doesn't exist
    mkdir -p "$project_dir/tests"
    
    # Run claude to implement the solution and tests
    claude --dangerously-skip-permissions -p "Follow the instructions in prompts/code_tests.txt.
    
    The INSTRUCTIONS.md file is located at: $instruction_path
    The project directory is: $project_dir
    The project is: $project_name
    The persona is: $persona
    
    Implement the solution and tests according to the instructions."
}

# Find all INSTRUCTIONS.md files
find projects -path "*/projects/*/*/*/INSTRUCTIONS.md" | while read instruction_file; do
    # Check if we have reached max parallel processes
    while [ $(jobs -p | wc -l) -ge $MAX_PARALLEL ]; do
        # Wait for any job to finish
        sleep 1
    done
    
    # Process this instruction file in the background
    process_instruction "$instruction_file" &
done

# Wait for all remaining processes to complete
echo "Waiting for all implementations to complete..."
wait

echo "All projects implemented with tests."
