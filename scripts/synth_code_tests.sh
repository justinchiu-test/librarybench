#!/bin/bash

# Check if a specific project/persona is provided
SINGLE_TEST=""
QUIT_AFTER_ONE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --single=*)
      SINGLE_TEST="${1#*=}"
      shift
      ;;
    --quit-after-one)
      QUIT_AFTER_ONE=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--single=project_name_persona] [--quit-after-one]"
      exit 1
      ;;
  esac
done

# Set maximum number of parallel processes
MAX_PARALLEL=6

# Save the original directory
ORIGINAL_DIR=$(pwd)

# Function to process an instruction file
process_instruction() {
    local instruction_path=$1
    local project_dir=$(dirname "$instruction_path")
    local full_dir_name=$(basename "$project_dir")
    
    # Extract the project name and persona
    # For example: personal_knowledge_management_academic_researcher -> 
    # project_name=personal_knowledge_management, persona=academic_researcher
    local project_name=""
    local persona=""
    
    # Loop through all projects and find a match
    for project in $(ls /Users/justinchiu/code/librarybench/ideas/*.txt | xargs -n1 basename | cut -d. -f1); do
        if [[ "$full_dir_name" == ${project}_* ]]; then
            project_name=$project
            persona=${full_dir_name#${project}_}
            break
        fi
    done
    
    # Skip if we're running a single test and this isn't it
    if [[ -n "$SINGLE_TEST" && "$full_dir_name" != *"$SINGLE_TEST"* ]]; then
        return 0
    fi
    
    echo "Implementing: $project_name for persona: $persona"
    echo "Directory: $project_dir"
    echo "Instructions: $instruction_path"
    
    # Create test directory if it doesn't exist
    mkdir -p "$project_dir/tests"
    
    # Change to the project directory
    pushd "$project_dir" > /dev/null
    
    echo "Working in directory: $(pwd)"

    uv venv
    source .venv/bin/activate
    
    # Run claude to implement the solution and tests
    claude --dangerously-skip-permissions -p "Follow the instructions in ${ORIGINAL_DIR}/prompts/code_tests.txt.
    
    The INSTRUCTIONS.md file is located at: INSTRUCTIONS.md
    The project directory is: $(pwd)
    The project is: $project_name
    The persona is: $persona
    
    Implement the solution and tests according to the instructions. Please ensure all tests pass.
    
    Make sure to work in the current directory: $(pwd). The virtual environment has been activated and will be deactivated for you."

    deactivate
    
    # Return to the original directory
    popd > /dev/null
    
    # If we're testing and want to quit after one, exit now
    if [[ "$QUIT_AFTER_ONE" == true ]]; then
        echo "Single test completed. Exiting as requested."
        exit 0
    fi
}

# Use a simpler find pattern that matches the actual directory structure
if [[ -n "$SINGLE_TEST" ]]; then
    echo "Running single test for: $SINGLE_TEST"
    # Find matching instruction files
    find /Users/justinchiu/code/librarybench/projects -name "INSTRUCTIONS.md" | grep "$SINGLE_TEST" | while read instruction_file; do
        process_instruction "$instruction_file"
    done
else
    # Process all instruction files in parallel
    find /Users/justinchiu/code/librarybench/projects -name "INSTRUCTIONS.md" | while read instruction_file; do
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
fi
