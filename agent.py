import os
import glob
import json
import logging
from typing import Any, Dict
import anthropic
from openai import OpenAI

from prompts import implementation_prompt_template, fix_implementation_prompt_template

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


def write_file(filepath, new_file_contents):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    open(filepath, "w").write(new_file_contents)


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
        task_content = []
        for task_file in glob.glob(os.path.join(repo.repo_path, "TASK*.md")):
            with open(task_file, "r") as f:
                content = f.read()
                task_content.append(f"```file:{task_file[len(repo.repo_path)+1:]}:\n{content}\n```")
                self.logger.info(
                    f"Loaded task file: {task_file} ({len(content)} chars)"
                    )
        task_content = "\n\n".join(task_content)

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

            write_file(full_path, file_content)
            self.logger.info(f"Created file: {full_path}")

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

        # Read source code files
        src_code_content = ""
        for src_file in glob.glob(os.path.join(repo.repo_path, "**", "*.py"), recursive=True):
            if os.path.basename(src_file).startswith("test_"): continue
            with open(src_file, "r") as f:
                content = f.read()
                src_code_content += f"\n\n```{src_file[len(repo.repo_path)+1:]}:\n{content}```"
                self.logger.info(
                    f"Loaded source file: {src_file} ({len(content)} chars)"
                )

        # Read test files
        test_content = ""
        # only allow top-level test files
        for test_file in glob.glob(os.path.join(repo.repo_path, "test_*.py"), recursive=True):
            with open(test_file, "r") as f:
                content = f.read()
                test_content += f"\n\n```{test_file[len(repo.repo_path)+1:]}\n{content}\n```"
                self.logger.info(
                    f"Loaded test file: {test_file} ({len(content)} chars)"
                )

        failed_test_details_list = []
        for test in failed_tests:
            if 'call' in test and 'longrepr' in test['call']:
                failed_test_details_list.append(f"- {test['nodeid'][len(repo.repo_path + '/') :]}: {test['call']['longrepr']}")
            elif 'setup' in test and 'longrepr' in test['setup']:
                failed_test_details_list.append(f"- {test['nodeid'][len(repo.repo_path + '/') :]}: {test['setup']['longrepr']}")
            elif 'teardown' in test and 'longrepr' in test['teardown']:
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
            write_file(full_path, file_content)
            self.logger.info(f"Fixed file: {full_path}")


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


    def generate_code(self, prompt: str, sampling_params: Dict[str, Any], task) -> str:
        system_prompt = f"You are a world-class software engineer with expertise in writing clean, efficient, and maintainable code. Your task is to {task} code according to the provided specifications and tests."
        return self.generate(prompt, sampling_params, system_prompt)
        

class ClaudeAgent(Agent):
    def __init__(self, model_name):
        super().__init__(model_name)
        self.client = anthropic.Anthropic()

    def generate_code(self, prompt: str, sampling_params: Dict[str, Any], task) -> str:
        system_prompt = """You are a world-class software engineer with expertise in writing clean, efficient, and maintainable code. 
Your task is to implement code according to the provided specifications and tests. 
When implementing new files or fixing existing ones, focus on creating well-structured, 
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

