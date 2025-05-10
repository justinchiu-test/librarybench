#!/bin/bash

# Set maximum number of parallel processes
MAX_PARALLEL=10

# Loop through all idea files and process in parallel
for idea_file in ideas/*.txt; do
    # Check if we have reached max parallel processes
    while [ $(jobs -p | wc -l) -ge $MAX_PARALLEL ]; do
        # Wait for any job to finish
        sleep 1
    done
    
    # Extract project name from filename
    project_name=$(basename "$idea_file" .txt)
    echo "Processing project: $project_name"
    
    # Run claude in background
    claude --dangerously-skip-permissions -p "Follow the instructions in prompts/instructions.txt, for any incomplete personas in project ${project_name}." &
done

# Wait for all remaining processes to complete
echo "Waiting for all processes to complete..."
wait

claude --dangerously-skip-permissions -p "Follow the instructions in prompts/instructions.txt for any projects that have not completed."
echo "All projects processed."
