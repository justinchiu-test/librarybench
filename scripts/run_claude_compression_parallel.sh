#!/bin/bash
# Script to run claude_compression.sh in parallel for all unified project directories

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Find all unified directories
unified_dirs=$(find "$REPO_ROOT/projects" -type d -name unified -not -path "*/\.*" | sort)

# Number of parallel processes to run
MAX_PARALLEL=10
running=0

# Create a temporary directory for logs
LOG_DIR="$REPO_ROOT/claude_compression_logs"
mkdir -p "$LOG_DIR"

# Process each unified directory
for unified_dir in $unified_dirs; do
    # Extract the project name from the path
    project_path=$(dirname "$unified_dir")
    project_name=$(basename "$project_path")
    
    echo "Scheduling compression for $project_name/unified..."
    
    # Run claude_compression.sh for this unified directory in background
    (
        echo "Starting compression for $project_name/unified at $(date)" > "$LOG_DIR/$project_name.log"
        "$SCRIPT_DIR/claude_compression.sh" "$unified_dir" >> "$LOG_DIR/$project_name.log" 2>&1
        echo "Completed compression for $project_name/unified at $(date)" >> "$LOG_DIR/$project_name.log"
        echo "Completed: $project_name/unified"
    ) &
    
    # Increment the running count
    running=$((running + 1))
    
    # If we've hit the max parallel processes, wait for one to finish
    if [ $running -ge $MAX_PARALLEL ]; then
        wait -n
        running=$((running - 1))
    fi
done

# Wait for any remaining processes to finish
wait

echo "All projects have been processed."
echo "Logs are available in $LOG_DIR"
