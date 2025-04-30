import os
import glob
import json
import logging
from typing import Any, Dict
import anthropic
from openai import OpenAI

from prompts import implementation_prompt_template, fix_implementation_prompt_template, refactoring_prompt_template

import sys
import ipdb
import traceback

def debughook(etype, value, tb):
    traceback.print_exception(etype, value, tb)
    print()
    ipdb.pm()  # post-mortem debugger


sys.excepthook = debughook


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

    def generate(self, prompt: str, sampling_params: Dict[str, Any], system_prompt: str) -> str:
        raise NotImplementedError("Subclasses must implement this method")


    def generate_code(self, prompt: str, sampling_params: Dict[str, Any]) -> str:
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

        file_blocks = []
        # While no blocks extracted, sample again
        num_attempts = 0
        while len(file_blocks) <= 1: 
            if num_attempts > 5: 
                return {"error": "No blocks generated"}, False
            # Create prompt for implementation
            prompt = implementation_prompt_template.format(task_content=task_content)

            # Generate implementation
            self.logger.info(f"Generating implementation using {self.model_name}")
            response = self.generate_code(prompt, {"temperature": 0.3}, task="implement")

            if not response:
                self.logger.error("Failed to generate implementation: empty response")
                return {"error": "Empty response from model"}

            # Extract and write files
            file_blocks = response.split("```file:")

            self.logger.info(
                f"Model returned {len(file_blocks) - 1} file blocks to process"
            )
            num_attempts += 1


        new_src_files = []

        for block in file_blocks[1:]:
            lines = block.split("\n")
            if not lines:
                continue

            file_path = lines[0].strip()
            if os.path.basename(file_path) in repo.test_files + repo.task_files:
                self.logger.info(
                    f"Will not write modifications to {file_path}"
                )
                continue

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
        for file_path in glob.glob(os.path.join(repo.repo_path, "*.py")):
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
        for src_file in glob.glob(os.path.join(repo.repo_path, "*.py")):
            if os.path.basename(src_file).startswith("test"): continue
            if os.path.exists(src_file):
                with open(src_file, "r") as f:
                    content = f.read()
                    src_code_content += f"\n\n```{os.path.basename(src_file)}:\n{content}```"
                    self.logger.info(
                        f"Loaded source file: {os.path.basename(src_file)} ({len(content)} chars)"
                    )

        # Read test files
        test_content = ""
        for test_file in repo.test_files:
            file_path = os.path.join(repo.repo_path, test_file)
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    content = f.read()
                    test_content += f"\n\n```{test_file}\n{content}\n```"
                    self.logger.info(
                        f"Loaded test file: {test_file} ({len(content)} chars)"
                    )

        failed_test_details_list = []
        for test in failed_tests:
            if 'call' in test and 'longrepr' in test['call']:
                failed_test_details_list.append(f"- {test['nodeid'][len(repo.repo_path + '/') :]}: {test['call']['longrepr']}")
            elif 'setup' in test and 'longrepr' in test['setup']['longrepr']:
                failed_test_details_list.append(f"- {test['nodeid'][len(repo.repo_path + '/') :]}: {test['setup']['longrepr']}")
            elif 'teardown' in test and 'longrepr' in test['teardown']['longrepr']:
                failed_test_details_list.append(f"- {test['nodeid'][len(repo.repo_path + '/') :]}: {test['teardown']['longrepr']}")
            else: 
                breakpoint()
        failed_test_details = "\n\n".join(failed_test_details_list)
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
        prompt = fix_implementation_prompt_template.format(src_code_content=src_code_content, test_content=test_content, failed_test_details=failed_test_details, test_output=test_output)
        # Generate fixed implementation
        self.logger.info(f"Generating fixes for failed tests using {self.model_name}")

        file_blocks = []
        num_attempts = 0
        while len(file_blocks) <= 1:
            if num_attempts > 5: 
                return {"error": "No blocks generated"}, False
            response = self.generate_code(prompt, {"temperature": 0.2}, task="implement")

            if not response:
                self.logger.error("Failed to generate fixed implementation: empty response")
                return {"error": "Empty response from model"}, False

            # Extract and write files
            file_blocks = response.split("```file:")
            self.logger.info(
                f"Model returned {len(file_blocks) - 1} file blocks to process"
            )
            num_attempts += 1
        
        modified_files = []
        files_with_actual_changes = 0
        has_content_changes = False  # Flag to indicate if any actual content changed


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
                    content = f.read()
                    src_code_content += f"\n\n{src_file}:\n{content}"
                    self.logger.info(
                        f"Loaded source file: {src_file} ({len(content)} chars)"
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

        # Create prompt for refactoring
        prompt = refactoring_prompt_template.format(src_code_content=src_code_content, test_content=test_content)

        # Generate refactored code
        self.logger.info(f"Generating refactored code using {self.model_name}")
        response = self.generate_code(prompt, {"temperature": 0.2}, task="refactor")

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

    def generate(self, prompt: str, sampling_params: Dict[str, Any], system_prompt: str) -> str:
        # Log the prompt
        prompt_logger.info(f"MODEL: {self.model_name} - PROMPT:\n{prompt}\n{'=' * 80}")
        messages = []
        if system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": system_prompt,
                },
            )
        messages.append({"role": "user", "content": prompt})
        if self.model_name in {"o3-mini", "o4-mini"}:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
            )
        else:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=sampling_params.get("temperature", 0.7),
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


    def generate_code(self, prompt: str, sampling_params: Dict[str, Any], task="refactor") -> str:
        system_prompt = f"You are a world-class software engineer with expertise in writing clean, efficient, and maintainable code. Your task is to {task} code according to the provided specifications and tests."
        return self.generate(prompt, sampling_params, system_prompt)
        

class ClaudeAgent(Agent):
    def __init__(self, model_name):
        super().__init__(model_name)
        self.client = anthropic.Anthropic()

    def generate_code(self, prompt: str, sampling_params: Dict[str, Any], task="refactor") -> str:
        system_prompt = """You are a world-class software engineer with expertise in writing clean, efficient, and maintainable code. 
Your task is to implement or refactor code according to the provided specifications and tests. 
When implementing new files or refactoring existing ones, focus on creating well-structured, 
modular code that is easy to understand and maintain. 
Always ensure your code passes all tests and maintains the expected functionality."""
        return self.generate(prompt, sampling_params, system_prompt)

    def generate(self, prompt: str, sampling_params: Dict[str, Any], system_prompt: str) -> str:
        # Log the prompt
        prompt_logger.info(f"MODEL: {self.model_name} - PROMPT:\n{prompt}\n{'=' * 80}")

        message = self.client.messages.create(
            model=self.model_name,
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

    def generate_code(self, prompt: str, sampling_params: Dict[str, Any], task="refactor") -> str:
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
