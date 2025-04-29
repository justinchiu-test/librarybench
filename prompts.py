feature_ask_prompt_template = """Consider a code repository designed to support the following task description:
```
{task_content}
```

Please list a couple dozen features that would be useful for the repository. Include the specified features as well as several others. 

List the suggested feature names and descriptions in the following format:

1: <feature_1_name>: <feature_1_description>
2: <feature_2_name>: <feature_2_description>
3: <feature_3_name>: <feature_3_description>
...
30: <feature_30_name>: <feature_30_description>
"""

persona_prompt_template = """Consider the following features of a code repository:
{listed_features}

Think about several possibilities for what kind of person might use this code repository and what they might use it for. Please write several brief descriptions for the code repository in first person, formatted in markdown as follows:
```file:TASK_<persona_name>.md
# The Task

I am a <...> I want to be able to <...> This code repository <...>

# The Requirements

* `<function_name>` : <feature description>
* ...
```

Be creative! Write the task description in the style of the proposed persona. Be as exhaustive as possible in including the listed features in the task description's requirements.
"""

implementation_prompt_template = """I need you to implement a solution based on the following task and test files. 
Your code must pass the tests provided.

# Task Details:
{task_content}

# Test Files:
{test_content}

Please implement all necessary files to solve this task. For each file, provide the content in the following format:

```file:<relative_file_path>
<file_content>
```

Where <relative_file_path> is the relative path to the file and <file_content> is the content of the file.
"""

fix_implementation_prompt_template = """I need you to fix the implementation of the following code that is failing tests.

# Current Implementation:
{src_code_content}

# Test Files:
{test_content}

# Failed Tests:
{failed_test_details}

# Test Output (if available):
{test_output}

Please carefully analyze the errors and test failures. Pay special attention to:
1. The exact assertion failures or error messages
2. What the tests expect vs. what your current implementation provides
3. Any edge cases or special conditions you might have missed

Your task is to fix the implementation to make all tests pass. For each file that needs to be modified, 
provide the content in the following format:

```file:<relative_file_path>
<file_content>
```

Where <relative_file_path> is the relative path to the file and <file_content> is the updated content of the file.
Focus on fixing the specific issues identified in the errors and failed tests while maintaining the overall structure of the code.

IMPORTANT: Make targeted changes to address the specific failing test cases. Make sure your implementation passes all test cases,
including any edge cases or special conditions mentioned in the tests.
"""

refactoring_prompt_template = """I need you to refactor the following source code to improve its maintainability, readability, and efficiency.
The refactored code must still pass all the existing tests.

# Source Code Files:
{src_code_content}

# Test Files (for your reference):
{test_content}

Please refactor each source code file, focusing on:
1. Abstracting out helper functions to reduce complexity
2. Improving code organization and structure
3. Enhancing readability while maintaining functionality
4. Optimizing performance where possible
5. Applying consistent code styling and documentation

Specifically, consider these refactoring techniques:
- Extract complex or duplicated logic into helper functions
- Apply design patterns where appropriate
- Improve variable and function naming for clarity
- Add type hints for better code understanding
- Restructure code to reduce nesting levels
- Implement better error handling
- Remove any unused code or imports

For each file, provide the refactored content in the following format:

```file:<relative_file_path>
<file_content>
```

IMPORTANT: The refactored files MUST execute to the same results as the original programs and pass all tests.
Do not change the external API or behavior of the code. Focus on internal improvements while maintaining
compatibility with existing tests and functionality.
"""