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

implementation_prompt_template = """I need you to implement a solution and COMPREHENSIVE suite of tests based on the following task files. 
Your code must pass the tests provided.

# Task Details:
{task_content}

Please implement all necessary files to solve this task. For each source code file, provide the content in the following format:

```file:<relative_file_path>
<file_content>
```

For each test file, provide the content in the same format so that it can be extracted and run with `pytest`:

```file:<relative_file_path starting with test_>
<test_file_content>
```

Where <relative_file_path> is the relative path to the file and <file_content> is the content of the file. Be sure to output code in the specified format.
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
including any edge cases or special conditions mentioned in the tests. Be sure to output code in the specified format. 
"""

refactoring_prompt_template = """Please rewrite the following programs by extracting helper functions.
Start by writing helper functions that can reduce the size of the code.
Do not add classes. Do not use nonlocal variables.
The main function should not be extracted into a helper function.
If the original program contains nonlocal variables, rewrite the algorithm so that nonlocal variables are no longer used.
Do not create nested helper functions. Instead, write those as separate helper functions which can call other helper functions.
The refactored code must still pass all existing tests.

# Source Code Files:
{src_code_content}

# Test Files:
{test_content}

Your answer must have the headers and codeblocks formatted exactly like the following Markdown examples.

The first code block should contain the helper functions:

# Extracted helper functions
```file:utils.py
# Shared utility functions for all modules
# IMPORTANT: This file must work when imported by different modules in different directories

def helper_function():
    ...
```

The remaining code blocks should contain any re-written files that now use the helper functions:

# Source Code Files:
```file:<relative_file_path>
<file_content>
```

Try to make the re-written code as short as possible by introducing shared helper functions. Helper function parameters should be as general as possible and helper functions should be informatively named.
Do not add classes, only add functions.
Rewrite programs so that they do not contain nonlocal variables.
Programs MUST NOT CONTAIN NONLOCAL VARIABLES.
Refactored code must still pass all the existing tests.

IMPORTANT: When updating imports, ensure that the utils module is imported using a relative import statement that will work correctly regardless of the file's location within the project structure (i.e., prefer "from utils import function" over absolute imports).
"""