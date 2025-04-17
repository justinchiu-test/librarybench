import os
import json
import logging
from typing import Any, Dict
import anthropic
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def write_new_file(filepath, new_file_contents, is_new_file):
    file_contents = ""
    if is_new_file:
        # if the LLM generated this as a new helper file, and it already exists in the repo, append to it. 
        if os.path.exists(filepath):
            file_contents = open(filepath).read() + "\n\n"
    file_contents += new_file_contents
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    open(filepath, 'w').write(file_contents)
    
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
        # Read task files
        task_content = ""
        for task_file in repo.task_files:
            file_path = os.path.join(repo.repo_path, task_file)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    task_content += f"\n\n{task_file}:\n{f.read()}"
        
        # Read test files
        test_content = ""
        for test_file in repo.test_files:
            file_path = os.path.join(repo.repo_path, test_file)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    test_content += f"\n\n{test_file}:\n{f.read()}"
        
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
        response = self.generate(prompt, {"temperature": 0.3, "max_tokens": 8000})
        
        if not response:
            self.logger.error("Failed to generate implementation: empty response")
            return {"error": "Empty response from model"}
        
        # Extract and write files
        file_blocks = response.split("```file:")
        new_src_files = []
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
            new_src_files.append(full_path)
            write_new_file(full_path, file_content, True)
            self.logger.info(f"Created file: {full_path}")
        
        src_files_path = os.path.join(repo.repo_path, "SRC_FILES.txt")
        
        # If SRC_FILES.txt already exists, read its content
        existing_files = set()
        if os.path.exists(src_files_path):
            try:
                with open(src_files_path, 'r') as rf:
                    existing_files = set(line.strip() for line in rf.readlines() if line.strip())
            except Exception as e:
                self.logger.error(f"Error reading existing SRC_FILES.txt: {e}")
        
        # Combine existing files with new files
        all_files = existing_files.union(set(new_src_files))
        
        # Write the combined list back to SRC_FILES.txt
        with open(src_files_path, 'w') as wf:
            wf.write('\n'.join(sorted(all_files)))
            self.logger.info(f"Updated SRC_FILES.txt with {len(new_src_files)} new source files")
            
        return new_src_files

    def fix_implementation(self, repo):
        # Read report.json for errors
        report_path = os.path.join(repo.repo_path, "report.json")
        if not os.path.exists(report_path):
            self.logger.error(f"Report file not found: {report_path}")
            return {"error": "Report file not found"}
        
        try:
            with open(report_path, 'r') as f:
                report = json.load(f)
        except json.JSONDecodeError:
            self.logger.error("Failed to parse report.json")
            return {"error": "Failed to parse report.json"}
        
        # Read source code files
        src_code_content = ""
        for src_file in repo.src_code_files:
            file_path = os.path.join(repo.repo_path, src_file)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    src_code_content += f"\n\n{src_file}:\n{f.read()}"
        
        # Read test files
        test_content = ""
        for test_file in repo.test_files:
            file_path = os.path.join(repo.repo_path, test_file)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    test_content += f"\n\n{test_file}:\n{f.read()}"
        
        # Extract error information from report
        failed_tests = [test for test in report.get("tests", []) if test['outcome'] not in {'passed', 'xfail'}]
        failed_test_details = "\n\n".join([f"- {test['nodeid'][len(repo.repo_path+'/'):]}: {test['call']['longrepr']}" for test in failed_tests])
        # Create prompt for fixing implementation
        prompt = f"""I need you to fix the implementation of the following code that is failing tests.

# Current Implementation:
{src_code_content}

# Test Files:
{test_content}

# Failed Tests:
{failed_test_details}

Please fix the implementation to resolve these errors and make the tests pass. 
For each file that needs to be modified, provide the content in the following format:

```file:<relative_file_path>
<file_content>
```

Where <relative_file_path> is the relative path to the file and <file_content> is the updated content of the file.
Focus on fixing the specific issues identified in the errors and failed tests while maintaining the overall structure of the code.
"""
        print(prompt)
        # Generate fixed implementation
        response = self.generate(prompt, {"temperature": 0.2, "max_tokens": 8000})
        
        if not response:
            self.logger.error("Failed to generate fixed implementation: empty response")
            return {"error": "Empty response from model"}
        
        # Extract and write files
        file_blocks = response.split("```file:")
        modified_files = []
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
            write_new_file(full_path, file_content, False)  # Not a new file, it's a fix to an existing file
            self.logger.info(f"Fixed file: {full_path}")
            modified_files.append(file_path)
        
        # Update SRC_FILES.txt with any newly fixed files
        src_files_path = os.path.join(repo.repo_path, "SRC_FILES.txt")
        
        # If SRC_FILES.txt already exists, read its content
        existing_files = set()
        if os.path.exists(src_files_path):
            try:
                with open(src_files_path, 'r') as rf:
                    existing_files = set(line.strip() for line in rf.readlines() if line.strip())
            except Exception as e:
                self.logger.error(f"Error reading existing SRC_FILES.txt: {e}")
        
        # Combine existing files with modified files
        all_files = existing_files.union(set(modified_files))
        
        # Write the combined list back to SRC_FILES.txt
        with open(src_files_path, 'w') as wf:
            wf.write('\n'.join(sorted(all_files)))
            self.logger.info(f"Updated SRC_FILES.txt with {len(modified_files)} modified source files")
            
        return list(all_files)
        

    def refactor_repo(self, repo):
        # Read source code files
        src_code_content = ""
        for src_file in repo.src_code_files:
            file_path = os.path.join(repo.repo_path, src_file)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    src_code_content += f"\n\n{src_file}:\n{f.read()}"
        
        # Read test files
        test_content = ""
        for test_file in repo.test_files:
            file_path = os.path.join(repo.repo_path, test_file)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
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
    
    For each file, provide the refactored content in the following format:
    
    ```file:<relative_file_path>
    <file_content>
    ```
    
    The refactored files MUST execute to the same results as the original programs and pass all tests.
    """
        
        # Generate refactored code
        response = self.generate(prompt, {"temperature": 0.2, "max_tokens": 8000})
        
        if not response:
            self.logger.error("Failed to generate refactored code: empty response")
            return {"error": "Empty response from model"}
        
        # Extract and write files
        file_blocks = response.split("```file:")
        refactored_files = []
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
            write_new_file(full_path, file_content, False)  # Not a new file, it's a refactored existing file
            self.logger.info(f"Refactored file: {full_path}")
            refactored_files.append(full_path)
        
        # Update SRC_FILES.txt with refactored files
        src_files_path = os.path.join(repo.repo_path, "SRC_FILES.txt")
        
        # If SRC_FILES.txt already exists, read its content
        existing_files = set()
        if os.path.exists(src_files_path):
            try:
                with open(src_files_path, 'r') as rf:
                    existing_files = set(line.strip() for line in rf.readlines() if line.strip())
            except Exception as e:
                self.logger.error(f"Error reading existing SRC_FILES.txt: {e}")
        
        # Combine existing files with refactored files
        all_files = existing_files.union(set(refactored_files))
        
        # Write the combined list back to SRC_FILES.txt
        with open(src_files_path, 'w') as wf:
            wf.write('\n'.join(sorted(all_files)))
            self.logger.info(f"Updated SRC_FILES.txt with {len(refactored_files)} refactored source files")
        
        return list(all_files)

class OpenAIAgent(Agent):
    def __init__(self, model_name):
        super().__init__(model_name)
        self.client = OpenAI()

    def generate(self, prompt: str, sampling_params: Dict[str, Any]) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a world-class software engineer with expertise in writing clean, efficient, and maintainable code. Your task is to implement or refactor code according to the provided specifications and tests."},
                {"role": "user", "content": prompt}
            ],
            temperature=sampling_params.get("temperature", 0.7),
            max_tokens=sampling_params.get("max_tokens", 4000)
        )
        
        if not response.choices:
            return ""
            
        content = response.choices[0].message.content
        return content if content is not None else ""

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
        
        message = self.client.messages.create(
            model=self.model_name,
            max_tokens=sampling_params.get("max_tokens", 4000),
            temperature=sampling_params.get("temperature", 0.7),
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        
        if not message.content or len(message.content) == 0:
            return ""
            
        # Extract text from the first content block
        # Handle different content block formats
        try:
            # Try new API format where content is an array of blocks
            if isinstance(message.content, list):
                for block in message.content:
                    if getattr(block, "type", None) == "text":
                        return getattr(block, "text", "")
            # For older API where content might be a string directly
            elif isinstance(message.content, str):
                return message.content
        except Exception as e:
            self.logger.error(f"Error extracting text from content: {e}")
        
        # Fallback if no text is found
        return ""

class TogetherAgent(Agent):
    def __init__(self, model_name):
        super().__init__(model_name)
        # Initialize TogetherAI client here
        # This is a placeholder - implementation depends on Together API
        self.client = None

    def generate(self, prompt: str, sampling_params: Dict[str, Any]) -> str:
        # Placeholder implementation for Together API
        # Replace with actual implementation based on Together's API
        self.logger.warning("TogetherAgent implementation is a placeholder. Update with actual API integration.")
        return "Placeholder response from TogetherAgent"