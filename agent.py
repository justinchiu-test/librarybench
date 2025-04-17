import os
import json
import logging
from typing import Any, Dict
import anthropic
from openai import OpenAI

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create a separate logger for prompts and generations
prompt_logger = logging.getLogger("prompts")
file_handler = logging.FileHandler("prompts.log")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
prompt_logger.addHandler(file_handler)
prompt_logger.setLevel(logging.INFO)


def write_new_file(filepath, new_file_contents, repo):
    file_contents = ""
    original_content = ""
    is_new_file = not os.path.exists(filepath)

    # don't overwrite starter files.
    if os.path.basename(filepath) in repo.test_files + repo.task_files:
        logger.warning(f"Tried overwriting a starter file {filepath}")
        return

    file_contents += new_file_contents
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # Log file changes
    if is_new_file:
        logger.info(
            f"Creating new file: {filepath} with {len(new_file_contents)} characters"
        )
    else:
        if original_content != new_file_contents:
            logger.info(f"Updating file: {filepath}")
            logger.info(f"  - Original size: {len(original_content)} chars")
            logger.info(f"  - New size: {len(new_file_contents)} chars")
            logger.info(
                f"  - Diff: {len(new_file_contents) - len(original_content)} chars"
            )
        else:
            logger.warning(f"No changes detected when writing to {filepath}")

    open(filepath, "w").write(file_contents)


class Agent:
    def __init__(self, model_name):
        self.model_name = model_name
        self.logger = logger

    def generate(self, prompt: str, sampling_params: Dict[str, Any]) -> str:
        """Generate a response from the model.

        Args:
            prompt: The input prompt
            sampling_params: Dictionary of sampling parameters

        Returns:
            The generated text response
        """
        raise NotImplementedError("Subclasses must implement this method")

    def implement_repo(self, repo):
        # Log starting the implementation process
        self.logger.info(
            f"Starting implementation for repo: {repo.repo_path} with model: {self.model_name}"
        )

        # Read task files
        task_content = ""
        for task_file in repo.task_files:
            file_path = os.path.join(repo.repo_path, task_file)
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    content = f.read()
                    task_content += f"\n\n{task_file}:\n{content}"
                    self.logger.info(
                        f"Loaded task file: {task_file} ({len(content)} chars)"
                    )

        # Read test files
        test_content = ""
        for test_file in repo.test_files:
            file_path = os.path.join(repo.repo_path, test_file)
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    content = f.read()
                    test_content += f"\n\n{test_file}:\n{content}"
                    self.logger.info(
                        f"Loaded test file: {test_file} ({len(content)} chars)"
                    )

        # Create prompt for implementation
        prompt = f"""I need you to implement a solution based on the following task and test files. 
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

        # Generate implementation
        self.logger.info(f"Generating implementation using {self.model_name}")
        response = self.generate(prompt, {"temperature": 0.3, "max_tokens": 8000})

        if not response:
            self.logger.error("Failed to generate implementation: empty response")
            return {"error": "Empty response from model"}

        # Extract and write files
        file_blocks = response.split("```file:")
        new_src_files = []

        self.logger.info(
            f"Model returned {len(file_blocks) - 1} file blocks to process"
        )

        for block in file_blocks[1:]:
            lines = block.split("\n")
            if not lines:
                continue

            file_path = lines[0].strip()
            content_parts = "\n".join(lines[1:]).split("```")
            if not content_parts:
                continue

            file_content = content_parts[0]

            # Write file to repository
            full_path = os.path.join(repo.repo_path, file_path)

            # Check if file already exists and would be overwritten
            if (
                os.path.exists(full_path)
                and os.path.basename(full_path) not in repo.test_files + repo.task_files
            ):
                with open(full_path, "r") as f:
                    original_content = f.read()
                if original_content == file_content:
                    self.logger.warning(
                        f"Implementation would not change existing file: {file_path}"
                    )

            new_src_files.append(file_path)
            write_new_file(full_path, file_content, repo)
            self.logger.info(f"Created file: {full_path}")

        # Count how many files were created or updated
        newly_created = 0
        for file_path in new_src_files:
            full_path = os.path.join(repo.repo_path, file_path)
            if os.path.exists(full_path):
                if os.path.basename(full_path) not in repo.test_files + repo.task_files:
                    # This is a file we created or updated, not a starter file
                    newly_created += 1

        self.logger.info(
            f"Implementation created/updated {newly_created} files out of {len(new_src_files)} total processed"
        )

        src_files_path = os.path.join(repo.repo_path, "SRC_FILES.txt")

        # If SRC_FILES.txt already exists, read its content
        existing_files = set()
        if os.path.exists(src_files_path):
            try:
                with open(src_files_path, "r") as rf:
                    existing_files = set(
                        line.strip() for line in rf.readlines() if line.strip()
                    )
            except Exception as e:
                self.logger.error(f"Error reading existing SRC_FILES.txt: {e}")

        # Make sure we only store relative paths, not absolute ones
        relative_src_files = [
            file_path
            if not os.path.isabs(file_path)
            else os.path.relpath(file_path, repo.repo_path)
            for file_path in new_src_files
        ]

        # Combine existing files with new files
        all_files = existing_files.union(set(relative_src_files))

        # Write the combined list back to SRC_FILES.txt
        with open(src_files_path, "w") as wf:
            wf.write("\n".join(sorted(all_files)))
            self.logger.info(
                f"Updated SRC_FILES.txt with {len(relative_src_files)} new source files"
            )

        return new_src_files

    def fix_implementation(self, repo):
        # Read report.json for errors
        report_path = os.path.join(repo.repo_path, "report.json")
        if not os.path.exists(report_path):
            self.logger.error(f"Report file not found: {report_path}")
            return {"error": "Report file not found"}, False

        try:
            with open(report_path, "r") as f:
                report = json.load(f)
        except json.JSONDecodeError:
            self.logger.error("Failed to parse report.json")
            return {"error": "Failed to parse report.json"}, False

        # Extract error information from report
        failed_tests = [
            test
            for test in report.get("tests", [])
            if test["outcome"] not in {"passed", "xfail"}
        ]
        self.logger.info(f"Attempting to fix {len(failed_tests)} failed tests")

        # Store original file checksums for later comparison
        original_file_checksums = {}
        original_file_contents = {}  # Store actual content for better comparison
        for src_file in repo.src_code_files:
            file_path = os.path.join(repo.repo_path, src_file)
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r") as f:
                        content = f.read()
                        # Store full content for exact comparison
                        original_file_contents[file_path] = content
                        # Use simple length as checksum for quick comparison
                        original_file_checksums[file_path] = len(content)
                except Exception as e:
                    self.logger.warning(
                        f"Could not read file {file_path} for checksum: {e}"
                    )

        # Read source code files
        src_code_content = ""
        for src_file in repo.src_code_files:
            file_path = os.path.join(repo.repo_path, src_file)
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    src_code_content += f"\n\n{src_file}:\n{f.read()}"

        # Read test files
        test_content = ""
        for test_file in repo.test_files:
            file_path = os.path.join(repo.repo_path, test_file)
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    test_content += f"\n\n{test_file}:\n{f.read()}"

        failed_test_details = "\n\n".join(
            [
                f"- {test['nodeid'][len(repo.repo_path + '/') :]}: {test['call']['longrepr']}"
                for test in failed_tests
            ]
        )
        # Add test output if it exists
        test_output = ""
        test_output_path = os.path.join(repo.repo_path, "test_output.txt")
        if os.path.exists(test_output_path):
            try:
                with open(test_output_path, "r") as f:
                    test_output = f.read()
                    self.logger.info(f"Loaded test output: ({len(test_output)} chars)")
            except Exception as e:
                self.logger.warning(f"Could not read test output file: {e}")

        # Create prompt for fixing implementation
        prompt = f"""I need you to fix the implementation of the following code that is failing tests.

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
        # Generate fixed implementation
        self.logger.info(f"Generating fixes for failed tests using {self.model_name}")
        response = self.generate(prompt, {"temperature": 0.2, "max_tokens": 8000})

        if not response:
            self.logger.error("Failed to generate fixed implementation: empty response")
            return {"error": "Empty response from model"}, False

        # Extract and write files
        file_blocks = response.split("```file:")
        modified_files = []
        files_with_actual_changes = 0
        has_content_changes = False  # Flag to indicate if any actual content changed

        self.logger.info(
            f"Model returned {len(file_blocks) - 1} file blocks to process"
        )

        for block in file_blocks[1:]:
            lines = block.split("\n")
            if not lines:
                continue

            file_path = lines[0].strip()
            content_parts = "\n".join(lines[1:]).split("```")
            if not content_parts:
                continue

            file_content = content_parts[0]

            # Write file to repository
            full_path = os.path.join(repo.repo_path, file_path)
            original_path = full_path

            # Check if the file content will actually change
            if os.path.exists(original_path):
                try:
                    with open(original_path, "r") as f:
                        original_content = f.read()
                    if original_content == file_content:
                        self.logger.warning(
                            f"No content changes detected for file: {file_path}"
                        )
                        continue
                    else:
                        files_with_actual_changes += 1
                        has_content_changes = True
                except Exception as e:
                    self.logger.warning(
                        f"Could not compare file contents for {file_path}: {e}"
                    )
            else:
                files_with_actual_changes += 1
                has_content_changes = True  # New file is definitely a change

            write_new_file(full_path, file_content, repo)
            self.logger.info(f"Fixed file: {full_path}")
            modified_files.append(file_path)

        self.logger.info(
            f"Successfully processed {len(modified_files)} files with {files_with_actual_changes} containing actual changes"
        )

        # Verify changes were actually made using content comparison
        changed_files = []
        for file_path, original_content in original_file_contents.items():
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r") as f:
                        new_content = f.read()
                        if new_content != original_content:
                            rel_path = os.path.relpath(file_path, repo.repo_path)
                            changed_files.append(rel_path)
                            has_content_changes = True
                            self.logger.info(
                                f"Verified content changes in file: {rel_path}"
                            )
                        elif original_file_checksums[file_path] != len(new_content):
                            # This is a fallback check, but content comparison is more reliable
                            rel_path = os.path.relpath(file_path, repo.repo_path)
                            changed_files.append(rel_path)
                            has_content_changes = True
                            self.logger.info(
                                f"Verified changes in file: {rel_path} (size changed: {original_file_checksums[file_path]} -> {len(new_content)})"
                            )
                except Exception as e:
                    self.logger.warning(f"Could not verify changes in {file_path}: {e}")

        self.logger.info(
            f"Verified changes in {len(changed_files)} files based on content comparison"
        )

        if not has_content_changes:
            self.logger.warning(
                "No actual content changes detected in any files despite LLM attempting fixes"
            )

        # Update SRC_FILES.txt with any newly fixed files
        src_files_path = os.path.join(repo.repo_path, "SRC_FILES.txt")

        # If SRC_FILES.txt already exists, read its content
        existing_files = set()
        if os.path.exists(src_files_path):
            try:
                with open(src_files_path, "r") as rf:
                    existing_files = set(
                        line.strip() for line in rf.readlines() if line.strip()
                    )
            except Exception as e:
                self.logger.error(f"Error reading existing SRC_FILES.txt: {e}")

        # Make sure we only store relative paths, not absolute ones
        relative_modified_files = [
            file_path
            if not os.path.isabs(file_path)
            else os.path.relpath(file_path, repo.repo_path)
            for file_path in modified_files
        ]

        # Combine existing files with modified files
        all_files = existing_files.union(set(relative_modified_files))

        # Write the combined list back to SRC_FILES.txt
        with open(src_files_path, "w") as wf:
            wf.write("\n".join(sorted(all_files)))
            self.logger.info(
                f"Updated SRC_FILES.txt with {len(relative_modified_files)} modified source files"
            )

        return list(all_files), has_content_changes

    def refactor_repo(self, repo):
        # Log starting the refactoring process
        self.logger.info(
            f"Starting refactoring of repo: {repo.repo_path} with model: {self.model_name}"
        )

        # Store original file checksums for later comparison
        original_file_checksums = {}
        for src_file in repo.src_code_files:
            file_path = os.path.join(repo.repo_path, src_file)
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r") as f:
                        content = f.read()
                        # Use simple length as checksum for quick comparison
                        original_file_checksums[file_path] = len(content)
                        self.logger.info(
                            f"Original file size of {src_file}: {len(content)} chars"
                        )
                except Exception as e:
                    self.logger.warning(
                        f"Could not read file {file_path} for checksum: {e}"
                    )

        # Read source code files
        src_code_content = ""
        for src_file in repo.src_code_files:
            file_path = os.path.join(repo.repo_path, src_file)
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    src_code_content += f"\n\n{src_file}:\n{f.read()}"

        # Read test files
        test_content = ""
        for test_file in repo.test_files:
            file_path = os.path.join(repo.repo_path, test_file)
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    test_content += f"\n\n{test_file}:\n{f.read()}"

        # Create prompt for refactoring
        prompt = f"""I need you to refactor the following source code to improve its maintainability, readability, and efficiency.
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

        # Generate refactored code
        self.logger.info(f"Generating refactored code using {self.model_name}")
        response = self.generate(prompt, {"temperature": 0.2, "max_tokens": 8000})

        if not response:
            self.logger.error("Failed to generate refactored code: empty response")
            return {"error": "Empty response from model"}

        # Extract and write files
        file_blocks = response.split("```file:")
        refactored_files = []
        files_with_actual_changes = 0

        self.logger.info(
            f"Model returned {len(file_blocks) - 1} file blocks to process"
        )

        for block in file_blocks[1:]:
            lines = block.split("\n")
            if not lines:
                continue

            file_path = lines[0].strip()
            content_parts = "\n".join(lines[1:]).split("```")
            if not content_parts:
                continue

            file_content = content_parts[0]

            # Write file to repository
            full_path = os.path.join(repo.repo_path, file_path)

            # Check if the file content will actually change
            if os.path.exists(full_path):
                try:
                    with open(full_path, "r") as f:
                        original_content = f.read()
                    if original_content == file_content:
                        self.logger.warning(
                            f"No content changes detected for file: {file_path}"
                        )
                        continue
                    else:
                        files_with_actual_changes += 1
                except Exception as e:
                    self.logger.warning(
                        f"Could not compare file contents for {file_path}: {e}"
                    )
            else:
                files_with_actual_changes += 1

            write_new_file(full_path, file_content, repo)
            self.logger.info(f"Refactored file: {full_path}")
            refactored_files.append(full_path)

        self.logger.info(
            f"Successfully processed {len(refactored_files)} files with {files_with_actual_changes} containing actual changes"
        )

        # Verify changes were actually made
        changed_files = []
        for file_path, original_checksum in original_file_checksums.items():
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r") as f:
                        new_content = f.read()
                        new_checksum = len(new_content)
                        if new_checksum != original_checksum:
                            rel_path = os.path.relpath(file_path, repo.repo_path)
                            changed_files.append(rel_path)
                            self.logger.info(
                                f"Verified changes in file: {rel_path} (size changed: {original_checksum} -> {new_checksum})"
                            )
                        else:
                            self.logger.warning(
                                f"No changes detected in file: {os.path.relpath(file_path, repo.repo_path)}"
                            )
                except Exception as e:
                    self.logger.warning(f"Could not verify changes in {file_path}: {e}")

        self.logger.info(
            f"Verified changes in {len(changed_files)} files based on content size"
        )

        # Update SRC_FILES.txt with refactored files
        src_files_path = os.path.join(repo.repo_path, "SRC_FILES.txt")

        # If SRC_FILES.txt already exists, read its content
        existing_files = set()
        if os.path.exists(src_files_path):
            try:
                with open(src_files_path, "r") as rf:
                    existing_files = set(
                        line.strip() for line in rf.readlines() if line.strip()
                    )
            except Exception as e:
                self.logger.error(f"Error reading existing SRC_FILES.txt: {e}")

        # Make sure we only store relative paths, not absolute ones
        relative_refactored_files = [
            file_path
            if not os.path.isabs(file_path)
            else os.path.relpath(file_path, repo.repo_path)
            for file_path in refactored_files
        ]

        # Combine existing files with refactored files
        all_files = existing_files.union(set(relative_refactored_files))

        # Write the combined list back to SRC_FILES.txt
        with open(src_files_path, "w") as wf:
            wf.write("\n".join(sorted(all_files)))
            self.logger.info(
                f"Updated SRC_FILES.txt with {len(relative_refactored_files)} refactored source files"
            )

        return list(all_files)


class OpenAIAgent(Agent):
    def __init__(self, model_name):
        super().__init__(model_name)
        self.client = OpenAI()

    def generate(self, prompt: str, sampling_params: Dict[str, Any]) -> str:
        # Log the prompt
        prompt_logger.info(f"MODEL: {self.model_name} - PROMPT:\n{prompt}\n{'=' * 80}")

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a world-class software engineer with expertise in writing clean, efficient, and maintainable code. Your task is to implement or refactor code according to the provided specifications and tests.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=sampling_params.get("temperature", 0.7),
            max_tokens=sampling_params.get("max_tokens", 4000),
        )

        if not response.choices:
            return ""

        content = response.choices[0].message.content
        result = content if content is not None else ""

        # Log the response
        prompt_logger.info(
            f"MODEL: {self.model_name} - RESPONSE:\n{result}\n{'=' * 80}"
        )

        return result


class ClaudeAgent(Agent):
    def __init__(self, model_name):
        super().__init__(model_name)
        self.client = anthropic.Anthropic()

    def generate(self, prompt: str, sampling_params: Dict[str, Any]) -> str:
        system_prompt = """You are a world-class software engineer with expertise in writing clean, efficient, and maintainable code. 
Your task is to implement or refactor code according to the provided specifications and tests. 
When implementing new files or refactoring existing ones, focus on creating well-structured, 
modular code that is easy to understand and maintain. 
Always ensure your code passes all tests and maintains the expected functionality."""

        # Log the prompt
        prompt_logger.info(f"MODEL: {self.model_name} - PROMPT:\n{prompt}\n{'=' * 80}")

        message = self.client.messages.create(
            model=self.model_name,
            max_tokens=sampling_params.get("max_tokens", 4000),
            temperature=sampling_params.get("temperature", 0.7),
            system=system_prompt,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        )

        if not message.content or len(message.content) == 0:
            return ""

        result = ""
        # Extract text from the first content block
        # Handle different content block formats
        try:
            # Try new API format where content is an array of blocks
            if isinstance(message.content, list):
                for block in message.content:
                    if getattr(block, "type", None) == "text":
                        result = getattr(block, "text", "")
                        break
            # For older API where content might be a string directly
            elif isinstance(message.content, str):
                result = message.content
        except Exception as e:
            self.logger.error(f"Error extracting text from content: {e}")

        # Log the response
        prompt_logger.info(
            f"MODEL: {self.model_name} - RESPONSE:\n{result}\n{'=' * 80}"
        )

        # Return the result
        return result


class TogetherAgent(Agent):
    def __init__(self, model_name):
        super().__init__(model_name)
        # Initialize TogetherAI client here
        # This is a placeholder - implementation depends on Together API
        self.client = None

    def generate(self, prompt: str, sampling_params: Dict[str, Any]) -> str:
        # Log the prompt
        prompt_logger.info(f"MODEL: {self.model_name} - PROMPT:\n{prompt}\n{'=' * 80}")

        # Placeholder implementation for Together API
        # Replace with actual implementation based on Together's API
        self.logger.warning(
            "TogetherAgent implementation is a placeholder. Update with actual API integration."
        )
        result = "Placeholder response from TogetherAgent"

        # Log the response
        prompt_logger.info(
            f"MODEL: {self.model_name} - RESPONSE:\n{result}\n{'=' * 80}"
        )

        return result
