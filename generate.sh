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
  echo "  -r, --refactor       Refactor implementations for all personas"
  echo "  --iterative          Implement iteratively until successful (default: true)"
  echo "  --no-iterative       Disable iterative implementation"
  echo "  --suffixes SUFFIXES  Suffixes for new repo versions (space-separated list)"
  echo "  --to_refactor TO_REFACTOR  Repos to group and refactor (space-separated list)"
  echo "  -h, --help           Show this help message"
  exit 1
}

# Default options
GEN_PERSONAS=false
IMPLEMENT=false
REFACTOR=false
ITERATIVE=true
SPECIFIC_TASK=""
SUFFIXES="_0"
TO_REFACTOR=""

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
    -r|--refactor)
      REFACTOR=true
      shift
      ;;
    --iterative)
      ITERATIVE=true
      shift
      ;;
    --no-iterative)
      ITERATIVE=false
      shift
      ;;
    --suffixes)
      shift
      SUFFIXES=()
      while [[ $# -gt 0 && ! $1 =~ ^- ]]; do
        SUFFIXES+=("$1")
        shift
      done
      ;;
    --to_refactor)
      shift
      TO_REFACTOR=()
      while [[ $# -gt 0 && ! $1 =~ ^- ]]; do
        TO_REFACTOR+=("$1")
        shift
      done
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
  
  # Refactor implementations if requested
  if [ "$REFACTOR" = true ]; then
    echo "Refactoring for $task..."
    
    # Build the python command with suffixes
    CMD=(python llm_repo_refactor.py --model "$MODEL" --task refactor --suffixes)
    for suffix in "${SUFFIXES[@]}"; do
      CMD+=( "$suffix")
    done
    CMD+=(--starter-repo-path "$task" --repos_to_refactor)
    for repo_to_refactor in "${TO_REFACTOR[@]}"; do
      CMD+=( "$repo_to_refactor")
    done
    
    echo "Running: ${CMD[*]}"
    "${CMD[@]}"
  fi

done

echo "All tasks completed!"



#   # Implement solutions only for a specific task
#   ./generate.sh -i -t data_encoder --iterative
#   ./generate.sh -r --suffixes _0 _1 --task document_editor --to_refactor document_editor_technical_writer_o4-mini_iterative document_editor_SoftwareDeveloper_o4-mini_iterative document_editor_project_manager_o4-mini_iterative