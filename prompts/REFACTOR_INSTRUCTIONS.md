# Unified Implementation Task

## Task Overview
Your task is to create a unified implementation that addresses the requirements from each directory.

## Steps

1. Read and analyze the TASK.md files in each directory: `*/TASK.md`

2. Copy all tests from each use case directory into `unified/tests/`:
   - Copy all test files from `*/*.py` that start with `test_` or are in a `test/` directory into `unified/tests/`
   - Ensure proper imports are maintained by updating import paths as needed

3. Analyze the common functionality, data structures, and interfaces across all implementations.

5. Design a unified architecture that satisfies all requirements from all use cases in `unified/PLAN.md`.

6. Implement the unified solution in the `unified` directory with an appropriate file structure that:
   - Includes all necessary modules and packages
   - Maintains compatibility with all test cases
   - Addresses the specific requirements from each TASK.md file
   - Uses consistent naming conventions and coding standards
   - Minimizes code duplication by consolidating similar functionality

7. Ensure that the unified implementation passes all tests copied from the use cases.

8. Document the architecture, key components, and how the solution addresses each use case's requirements.
