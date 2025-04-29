#!/bin/bash

# Set to exit on error
set -e

# List of tasks to process
tasks=(document_editor workflow_orchestration data_encoder dependency_resolver)

# Default model to use
MODEL="o4-mini"

# Function to print usage instructions
function usage {
  echo "Usage: $0 [options]"
  echo "Options:"
  echo "  -m, --model MODEL    Specify model (default: o4-mini)"
  echo "  -t, --task TASK      Process only specified task"
  echo "  -p, --personas       Generate personas for tasks"
  echo "  -i, --implement      Implement solutions for all personas"
  echo "  --iterative          Implement iteratively until successful (default: true)"
  echo "  --no-iterative       Disable iterative implementation"
  echo "  --suffixes SUFFIXES  Suffixes for new repo versions (comma-separated list)"
  echo "  -h, --help           Show this help message"
  exit 1
}

# Default options
GEN_PERSONAS=false
IMPLEMENT=false
ITERATIVE=true
SPECIFIC_TASK=""
SUFFIXES="_0"

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -m|--model)
      MODEL="$2"
      shift 2
      ;;
    -t|--task)
      SPECIFIC_TASK="$2"
      shift 2
      ;;
    -p|--personas)
      GEN_PERSONAS=true
      shift
      ;;
    -i|--implement)
      IMPLEMENT=true
      shift
      ;;
    --iterative)
      # No parameter needed since it's a boolean flag
      ITERATIVE=true
      shift
      ;;
    --no-iterative)
      ITERATIVE=false
      shift
      ;;
    --suffixes)
      SUFFIXES="$2"
      shift 2
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo "Unknown option: $1"
      usage
      ;;
  esac
done

# Filter tasks if specific task is provided
if [ ! -z "$SPECIFIC_TASK" ]; then
  if [[ " ${tasks[@]} " =~ " ${SPECIFIC_TASK} " ]]; then
    tasks=("$SPECIFIC_TASK")
  else
    echo "Error: Task '$SPECIFIC_TASK' not found. Available tasks: ${tasks[@]}"
    exit 1
  fi
fi

# Process each task
for task in "${tasks[@]}"; do
  echo "Processing task: $task"
  
  # Generate personas if requested
  if [ "$GEN_PERSONAS" = true ]; then
    echo "Generating personas for $task..."
    python llm_repo_refactor.py --model "$MODEL" --task make_personas --starter-repo-path "$task"
  fi
  
  # Implement solutions if requested
  if [ "$IMPLEMENT" = true ]; then
    echo "Finding persona directories for $task..."
    
    # Get list of persona directories using bash glob
    persona_dirs=("${task}"_*)
    
    for persona_dir in "${persona_dirs[@]}"; do
      # Skip directories with model names in them (they are implementation directories)
      if [[ "$persona_dir" == *"${MODEL}"* ]]; then
        continue
      fi
      
      # Skip if not a directory
      if [ ! -d "$persona_dir" ]; then
        continue
      fi
      
      echo "Implementing solution for persona: $persona_dir"
      
      # If iterative is true, do iterative implementation
      if [ "$ITERATIVE" = true ]; then
        echo "Performing iterative implementation for $persona_dir..."
        python llm_repo_refactor.py --model "$MODEL" --task implement --suffixes "_iterative" --iterative --starter-repo-path "$persona_dir"
      fi
    done
  fi
done

echo "All tasks completed!"


# The generate.sh script will:
#   1. Optionally generate personas for each task
#   2. Find all persona directories for implementation
#   3. Run one-pass implementation for each persona
#   4. Optionally run iterative implementation to improve solutions

#   You can now use it like:
#   # Generate personas and implement for all tasks with default model
#   ./generate.sh

#   # Generate only personas using Claude
#   ./generate.sh -p -m "claude-3-7-sonnet-20250219"

#   # Implement solutions only for a specific task
#   ./generate.sh -i -t document_editor

#   # Full control with custom suffixes and iterative implementation
#   ./generate.sh -m "o4-mini" -t workflow_orchestration --suffixes "_v1,_v2,_v3" --iterative
#   
#   # Disable iterative implementation
#   ./generate.sh --no-iterative