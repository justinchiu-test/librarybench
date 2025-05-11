library_ask_prompt = """I need ideas for Python libraries that can be implemented by language models. These libraries should:

1. Be implementable using only Python's standard library - no external dependencies
2. Have enough complexity to demonstrate sophisticated code design (10-20 functions/methods)
3. Include room for interpretation, so that different implementations can be unique while sharing core functionality
4. Have clear, practical utility that solves a real programming need
5. Be realistically implementable by an intelligent LLM
6. Be testable with pytest
7. Include opportunities for different design approaches (functional vs OOP, etc.)

For each library, provide a description that outlines:
- The problem domain and core purpose
- Key required functionality (without being too prescriptive about implementation details)
- Potential use cases that demonstrate practical applications
- Suggested extension points where implementers could add their creative spin

Please generate several proposals in markdown, following this format:

```file:<library_name>/DESCRIPTION.md
# <Library Name>

## Purpose and Motivation
<3-5 sentences on what problem this library solves and why it's useful>

## Core Functionality
<Description of 4-6 high-level key features/capabilities without specifying exact implementation>
```

Be creative! Focus on domains where standard Python libraries provide enough building blocks but where a well-designed abstraction layer would add significant value.
"""

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
```file:{library_name}/<persona_name>/TASK.md
# The Task

I am a <...> I want to be able to <...> This code repository <...>

# The Requirements

* `<function_name>` : <feature description>
* ...
```

Be creative! Write the task description in the style of the proposed persona. Be as exhaustive as possible in including the listed features in the task description's requirements.
"""

implementation_prompt_template = """I need you to implement a Python solution and COMPREHENSIVE suite of tests based on the following task files.
Your code must pass the tests provided.

{task_content}

CRITICAL FORMATTING INSTRUCTIONS:
1. You MUST format ALL code files exactly as shown below - no exceptions
2. Start each file with the markdown codeblock marker, followed by "file:" and the relative path
3. End each file with the closing markdown codeblock marker
4. Do not use any other format or markdown variations
5. For test files, do not put them in a subdirectory-- keep them in the outermost level.

For each source code file:

```file:<relative_file_path>
<file_content>
```

For each test file:

```file:<relative_file_path starting with test_>
<test_file_content>
```

IMPORTANT:
- The opening format must be exactly: ```file:path/to/file.py
- Do not add language indicators like ```python
- Do not add explanations between files
- Each file must be contained within its own codeblock with the precise format shown above
- The system parsing your response requires this exact format to function properly

EXAMPLE OUTPUT FORMAT:
```file:mymodule/mymodule.py
def example_function():
    return "This is a sample function"
```

```file:test_utils.py
import pytest
from mymodule.mymodule import example_function

def test_example_function():
    assert example_function() == "This is a sample function"
```

Begin your implementation now, following these formatting rules precisely.
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
