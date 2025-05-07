import os
import json
import glob
import re
import random
import math
import shutil
import subprocess
import sys
from pathlib import Path
from collections import Counter
import logging
import argparse
from typing import List

from agent import OpenAIAgent, ClaudeAgent
from prompts import feature_ask_prompt_template, persona_prompt_template

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Repo:
    def __init__(self, repo_path, test_command="pytest"):
        self.logger = logger
        self.repo_path = repo_path
        test_file_paths = glob.glob(os.path.join(repo_path, "**", "test*.py"), recursive=True)
        task_file_paths = glob.glob(os.path.join(repo_path, "**", "TASK*.md"), recursive=True)
        # Do not store repo_path but store the rest of the relative path
        self.test_files = [path[len(repo_path)+1:] for path in test_file_paths]
        self.task_files = [path[len(repo_path)+1:] for path in task_file_paths]
        
        self.test_command = test_command
        self.src_code_files = []
        self.src_files_path = os.path.join(repo_path, "SRC_FILES.txt")
        if os.path.exists(self.src_files_path):
            try:
                with open(self.src_files_path, "r") as rf:
                    self.src_code_files.extend([
                        os.path.join(os.path.dirname(self.src_files_path)[len(repo_path)+1:], line.strip()) for line in rf.readlines() if line.strip()
                    ])
            except Exception as e:
                self.logger.error(f"Error reading existing SRC_FILES.txt: {e}")
        else:
            for src_files_path in glob.glob(os.path.join(repo_path, "**", "SRC_FILES.txt"), recursive=True):
                try:
                    with open(src_files_path, "r") as rf:
                        self.src_code_files.extend([
                            os.path.join(os.path.dirname(src_files_path)[len(repo_path)+1:], line.strip()) for line in rf.readlines() if line.strip()
                        ])
                except Exception as e:
                    self.logger.error(f"Error reading existing SRC_FILES.txt: {e}")

        self.logger.info(f"New repo implemented with test files {self.test_files} and task files {self.task_files}.")

    def update_src_files(self, new_src_files):
        """Update the list of source code files and write to SRC_FILES.txt."""
        # Make sure we only store relative paths, not absolute ones
        relative_src_files = [
            file_path
            if not os.path.isabs(file_path)
            else os.path.relpath(file_path, self.repo_path)
            for file_path in new_src_files
        ]
        
        # Update the in-memory list
        self.src_code_files = sorted(set(self.src_code_files).union(set(relative_src_files)))
        
        # Write the combined list to SRC_FILES.txt
        with open(self.src_files_path, "w") as wf:
            wf.write("\n".join(self.src_code_files))
            self.logger.info(
                f"Updated SRC_FILES.txt with {len(relative_src_files)} source files"
            )
    
    def make_new_to_implement(self, new_repo_location) -> 'Repo':
        # if new_repo_location already exists, raise an error
        if os.path.exists(new_repo_location):
            self.logger.warning(f"Directory {new_repo_location} already exists. Overwriting...")
            shutil.rmtree(new_repo_location)
        
        # make a directory at target_repo_location and copy only the test_files and task_files in
        os.makedirs(new_repo_location)
        
        for file in self.task_files:
            src_path = os.path.join(self.repo_path, file)
            dst_path = os.path.join(new_repo_location, file)
            
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            
            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
            else:
                self.logger.warning(f"Source file {src_path} does not exist, skipping")
        
        # make new Repo object and return it
        return Repo(new_repo_location, self.test_command)

    def evaluate(self):
        test_cmd = f"pytest {' '.join(self.test_files)} --json-report --json-report-file=report.json --continue-on-collection-errors > test_output.txt 2>&1"
        self.logger.info(f"Running evaluation. test cmd: {test_cmd}")
        result = {}
        try:
            process = subprocess.run(
                test_cmd, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True,
                cwd=self.repo_path,
                executable="/bin/bash"  # ensure we're using bash for the source command
            )
            result = {
                "returncode": process.returncode,
                "stdout": process.stdout,
                "stderr": process.stderr
            }
            # Attempt to extract a test report from 'report.json'.
        except Exception as e: 
            self.logger.error(f"Failed to run tests: {e}")
            return {
                "sum": 0,
                "passed": 0,
                "num_passed": 0,
                "num_tests": 0,
            }

        report_path = Path(self.repo_path) / "report.json"
        if report_path.exists():
            try:

                with open(report_path, "r") as f:
                    report = json.load(f)
                result["report"] = report
                self.logger.info("Successfully extracted test report from report.json")
                # Determine the report format:
                if isinstance(report, dict) and "tests" in report:
                    # New version: extract test call info from all tests that have the "call" field.
                    test_results = [test["call"] for test in report.get("tests", []) if "call" in test]
                else:
                    # Old version: assume report is a list and filter tests with "when" equal to "call".
                    test_results = [test for test in report if test.get("when") == "call"]
                num_tests = len(test_results)

                # Include collector failures
                collector_failures = [
                    collector for collector in report.get("collectors", [])
                    if collector.get("outcome") == "failed"
                ]
                # Each failed collector represents a test file that didn't run any tests due to an error
                num_collector_failures = len(collector_failures)
                num_tests += num_collector_failures  # treat each as a failed test
                num_passed = sum(
                    1 for test in test_results if test.get("outcome") in ("passed", "xfail")
                )

                if num_tests == 0:
                    return {
                        "sum": 0,
                        "passed": 0,
                        "num_passed": 0,
                        "num_tests": 0,
                    }
                
                # Calculate total runtime.
                total_runtime = sum(test.get("duration", 0) for test in test_results)
                
                # Count outcomes (treat xfail as passed).
                outcomes = [test.get("outcome", "failed") for test in test_results]
                outcome_counter = Counter(outcomes)
                # Ensure key for xfail is present.
                if "xfail" not in outcome_counter:
                    outcome_counter["xfail"] = 0
                num_passed = outcome_counter.get("passed", 0) + outcome_counter.get("xfail", 0)
                passed_rate = num_passed / num_tests
                
                return {
                    "sum": total_runtime,
                    "passed": passed_rate,
                    "num_passed": num_passed,
                    "num_tests": num_tests,
                }
            except Exception as e:
                self.logger.error(f"Failed to parse report.json: {e}")

        return {
            "sum": 0,
            "passed": 0,
            "num_passed": 0,
            "num_tests": 0,
        }

def make_personas(agent, args):
    # ask LLM for features 
    task_content = ""
    for task_file in [os.path.join(args.starter_repo_path, "TASK.md"), os.path.join(args.starter_repo_path, "TASK_v2.md")]:
        if not os.path.exists(task_file): continue
        with open(task_file, "r") as f:
            content = f.read()
            task_content += f"\n{content}"
    
    response = agent.generate(feature_ask_prompt_template.format(task_content=task_content), {"temperature": 0.3}, system_prompt="")

    all_features = {}
    # Extract features
    for feature in re.finditer(r'\n\d+:([^:]+):(.+)', response):
        all_features[feature.group(1).strip()] = feature.group(2).strip()

    # Subsample features into ten personas that would use it.
    personas = {}
    for _ in range(10):
        features = random.sample(sorted(all_features), 10)
        persona_prompt = persona_prompt_template.format(listed_features="\n".join([f"- {feature_name}: {all_features[feature_name]}" for feature_name in features]))

        response = agent.generate(persona_prompt, {"temperature": 0.3}, system_prompt="")
        # Extract new task files
        file_blocks = response.split("```file:")
        for block in file_blocks[1:]:
            lines = block.split("\n")
            if not lines:
                continue

            file_path = lines[0].strip()
            persona_name = re.search(r'TASK_(.+).md', file_path)
            if not persona_name: continue
            persona_name = persona_name.group(1)

            content_parts = "\n".join(lines[1:]).split("```")
            if not content_parts:
                continue

            file_content = content_parts[0]
            personas[persona_name] = file_content

    all_new_repos = []
    for persona_name, task_description in personas.items():
        new_repo_location = os.path.join(os.path.dirname(args.starter_repo_path), f"{os.path.basename(args.starter_repo_path)}_{persona_name}")
        os.makedirs(new_repo_location, exist_ok=True)
        task_file_path = os.path.join(new_repo_location, "TASK.md")
        with open(task_file_path, 'w') as wf:
            wf.write(task_description)
        repo = Repo(new_repo_location)
        all_new_repos.append(repo)

    return all_new_repos


def implement(agent, args):
    orig_repo = Repo(args.starter_repo_path)
    for suffix in args.suffixes:
        new_repo_location = os.path.join(os.path.dirname(args.starter_repo_path), f"{os.path.basename(args.starter_repo_path)}_{agent.model_name}{'' if args.iterative else '_onepass'}{suffix}")
        if os.path.exists(new_repo_location):
            do_reimplement = input(f"{new_repo_location} already exists. Re-implement? [y/]").strip() == "y"
            if not do_reimplement: continue

        repo = orig_repo.make_new_to_implement(new_repo_location)
        new_src_files = agent.implement_repo(repo)
        repo.update_src_files(new_src_files)
        # Track success rates over different iterations
        num_attempts = 0
        attempt_results = []
        num_no_changes = 0
        
        while args.iterative and (repo.evaluate()["passed"] < 1):
            logger.info(f"Fix implementation attempt #{num_attempts + 1}")
            eval_before = repo.evaluate()
            attempt_results.append({"attempt": num_attempts, "before": eval_before})
            
            fix_results = agent.fix_implementation(repo)
            if fix_results is None:
                continue
            new_src_files, has_changes = fix_results
            num_attempts += 1
            repo.update_src_files(new_src_files)
            
            # Skip evaluation if no actual code changes occurred
            if not has_changes:
                logger.warning("No source code changes detected, skipping unnecessary evaluation")
                attempt_results[-1]["after"] = eval_before  # Use previous evaluation results
                attempt_results[-1]["skipped_eval"] = True
                num_no_changes += 1
                # If we've had multiple attempts with no changes, we might be stuck
                if num_no_changes > 2:
                    logger.warning("Multiple attempts with no changes detected, possible stagnation")
                
                # We still count this as an attempt towards the limit
                if num_attempts > 5:
                    logger.warning("Reached maximum number of fix attempts (5)")
                    break
                
                # Continue to next iteration without evaluating
                continue
            num_no_changes = 0
            # Only evaluate if changes were actually made
            eval_after = repo.evaluate()
            attempt_results[-1]["after"] = eval_after
            
            # Log progress for this attempt
            logger.info(f"Fix attempt #{num_attempts} results:")
            logger.info(f"  - Before: {eval_before['num_passed']}/{eval_before['num_tests']} tests passing ({eval_before['passed']*100:.1f}%)")
            logger.info(f"  - After: {eval_after['num_passed']}/{eval_after['num_tests']} tests passing ({eval_after['passed']*100:.1f}%)")
            logger.info(f"  - Improvement: {(eval_after['passed'] - eval_before['passed'])*100:.1f}% more tests passing")
            
            if num_attempts > 5: 
                logger.warning("Reached maximum number of fix attempts (5)")
                break
        final_repo_results = repo.evaluate()
        print(final_repo_results)

def _update_local_imports(file_paths, target_dir, repo_path):
    # Update relative imports in the files to account for new directory structure
    for file_path in file_paths:
        target_file = os.path.join(target_dir, os.path.relpath(file_path, repo_path))
        if os.path.exists(target_file):
            try:
                with open(target_file, 'r') as f:
                    content = f.read()
                
                # Add __init__.py files to make imports work
                file_dir = os.path.dirname(target_file)
                init_file = os.path.join(file_dir, "__init__.py")
                if not os.path.exists(init_file):
                    with open(init_file, 'w') as f:
                        f.write("# Auto-generated __init__.py to enable imports\n")
                    logger.info(f"Created {init_file}")
                
                # Find import statements (both regular imports and from imports)
                import_pattern = re.compile(r'(?m)^(from\s+|import\s+)([.\w]+)')
                if "core.logger" in content: breakpoint()
                matches = import_pattern.findall(content)
                
                # Get the persona name to prepend to imports
                persona_subdir = os.path.basename(target_dir)
                
                modified_content = content
                for match in matches:
                    import_type, module_path = match
                    # Skip standard library and third-party imports
                    if '.' not in module_path and module_path in sys.builtin_module_names:
                        continue
                    
                    # Skip imports that already include the subdirectory
                    if persona_subdir in module_path:
                        continue
                    
                    # List of common built-in or 3rd-party modules to avoid modifying
                    standard_modules = {'os', 'sys', 'json', 'pytest', 'unittest', 're', 
                                        'datetime', 'time', 'collections', 'pathlib', 'math',
                                        'logging', 'random', 'shutil', 'glob', 'argparse', 
                                        'typing', 'io', 'tempfile'}
                    
                    if module_path in standard_modules:
                        continue
                    
                    # Check if this is a relative import referring to a local module
                    module_file = module_path.replace('.', '/') + '.py'
                    if os.path.exists(os.path.join(target_dir, module_file)):
                        # This is a local module that needs to be updated
                        old_import = f"{import_type}{module_path}"
                        new_import = f"{import_type}{persona_subdir}.{module_path}"
                        modified_content = modified_content.replace(old_import, new_import)
                    elif os.path.exists(os.path.join(target_dir, module_path + '.py')):
                        # Direct file import
                        old_import = f"{import_type}{module_path}"
                        new_import = f"{import_type}{persona_subdir}.{module_path}"
                        modified_content = modified_content.replace(old_import, new_import)
                    
                    # Handle local imports without checking if file exists (useful for packages)
                    if not module_path.startswith('.') and not any(module_path.startswith(std) for std in standard_modules):
                        # Check if this module exists in the persona directory
                        if glob.glob(os.path.join(target_dir, "**", f"{module_path.split('.')[0]}.py"), recursive=True):
                            old_import = f"{import_type}{module_path}"
                            new_import = f"{import_type}{persona_subdir}.{module_path}"
                            modified_content = modified_content.replace(old_import, new_import)
                # Write the updated content back to the file
                if modified_content != content:
                    with open(target_file, 'w') as f:
                        f.write(modified_content)
                    logger.info(f"Updated imports in {target_file}")
            except Exception as e:
                logger.error(f"Error updating imports in {target_file}: {e}")

def _create_grouped_repo(central_repo_path, persona_repos, args):
    persona_names = []
    for repo_name in persona_repos:
        persona_name = re.search(rf'{args.starter_repo_path}_(.+)_{args.model}', repo_name).group(1)
        persona_names.append(persona_name)
    personas = "_".join(sorted(persona_names))
    
    # If it already exists, ask for confirmation before overwriting
    do_reimplement = True
    if os.path.exists(central_repo_path):
        do_reimplement = input(f"{central_repo_path} already exists. Re-create? [y/]").strip() == "y"
        if not do_reimplement:
            return personas, Repo(central_repo_path)
        shutil.rmtree(central_repo_path)

    os.makedirs(central_repo_path, exist_ok=True)

    # Copy all repos into the central repo as subdirectories
    for repo_path in persona_repos:
        repo_name = os.path.basename(repo_path)
        persona_name = re.search(rf'{args.starter_repo_path}_(.+)_{args.model}', repo_name).group(1)
        target_dir = os.path.join(central_repo_path, persona_name)
        
        # Copy the repo contents
        shutil.copytree(repo_path, target_dir)
        # TODO consider removing old eval artifacts e.g. test_output.txt and report.json
        
        # Collect source and test files
        file_paths = glob.glob(os.path.join(repo_path, "**", "*.py"), recursive=True)
        _update_local_imports(file_paths, target_dir, repo_path)
    
    # Create the central repo object
    central_repo = Repo(central_repo_path)
    logger.info(f"Computing metrics before refactoring for {central_repo_path}")
    try:
        before_score_cmd = f"python score.py --directory {central_repo_path} --branch_name {personas}_original"
        subprocess.run(before_score_cmd, shell=True, check=True)
        logger.info(f"Successfully computed metrics before refactoring")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to compute metrics before refactoring: {e}")

    # Try to load the metrics file to show differences
    metrics_file = f"{os.path.basename(args.starter_repo_path)}_metrics.json"
    original_metrics = {}
    if os.path.exists(metrics_file):
        try:
            with open(metrics_file, 'r') as f:
                metrics_data = json.load(f)
            original_metrics = metrics_data.get(f"{personas}_original", {})
        except: 
            pass
    eval_results = central_repo.evaluate()
    logger.info(f"Originl repo test results: {eval_results['num_passed']}/{eval_results['num_tests']} tests passing ({eval_results['passed']*100:.1f}%)")
    with open(os.path.join(central_repo.repo_path, "results.json"), 'w') as wf:
        json.dump({"pytest": eval_results, "metrics_before": original_metrics}, wf, indent=4)

    return personas, central_repo

def refactor(agent, args):
    repos_to_refactor = glob.glob(f"{args.starter_repo_path}_*_{args.model}_iterative")
    group_idx_to_remaining_suffixes = {group_idx: args.suffixes for group_idx in range(math.ceil(len(repos_to_refactor) / 3.0))}

    for i in range(0, len(repos_to_refactor), 3):
        group_idx = int(i / 3)
        central_repo_starter = f"{args.starter_repo_path}_{args.model}_group{group_idx}"
        for grouped_repo in glob.glob(f"{central_repo_starter}*"):
            suffix = grouped_repo[len(central_repo_starter):]
            if suffix in group_idx_to_remaining_suffixes[group_idx]:
                group_idx_to_remaining_suffixes[group_idx].remove(suffix)

        # Make a new central library that all of these can reference.
        # Process repos in groups of 3
        group = repos_to_refactor[i:i+3]
        logger.info(f"Processing group of repos: {group}")
        
        # Compute metrics on original
        original_central_repo_path = f"{central_repo_starter}_original"
        personas, central_repo = _create_grouped_repo(original_central_repo_path, group, args)

        for suffix in group_idx_to_remaining_suffixes[group_idx]:
            # Create a new central repo that combines these as subdirectories
            central_repo_path = f"{central_repo_starter}{suffix}"
            
            # If it already exists, ask for confirmation before overwriting
            if os.path.exists(central_repo_path):
                do_reimplement = input(f"{central_repo_path} already exists. Re-refactor? [y/]").strip() == "y"
                if not do_reimplement:
                    continue
                shutil.rmtree(central_repo_path)
            
            # Create the central repo directory
            shutil.copytree(original_central_repo_path, central_repo_path)
            
            # Create the central repo object
            central_repo = Repo(central_repo_path)
                
            # Perform the refactoring
            logger.info(f"Starting refactoring of {central_repo_path}")
            agent.refactor_repo(central_repo)
            
            # Calculate metrics after refactoring
            logger.info(f"Computing metrics after refactoring for {central_repo_path}")
            try:
                after_score_cmd = f"python score.py --directory {central_repo_path} --branch_name {personas}{suffix}"
                subprocess.run(after_score_cmd, shell=True, check=True)
                logger.info(f"Successfully computed metrics after refactoring")
                
                # Try to load the metrics file to show differences
                metrics_file = f"{os.path.basename(args.starter_repo_path)}_metrics.json"
                if os.path.exists(metrics_file):
                    try:
                        with open(metrics_file, 'r') as f:
                            metrics_data = json.load(f)
                            
                        # Find before and after metrics if they exist
                        refactor_metrics = metrics_data.get(f"{personas}{suffix}", {})
                        original_metrics = metrics_data.get(f"{personas}_original", {})
                        
                        # Log the total metrics
                        logger.info(f"Refactored Total Log Probability: {refactor_metrics.get('total_logprobs', 'N/A')}")
                        logger.info(f"Refactored Total Tokens: {refactor_metrics.get('total_tokens', 'N/A')}")
                        logger.info(f"Refactored Total LOC: {refactor_metrics.get('total_loc', 'N/A')}")
                        logger.info(f"Refactored Total SLOC: {refactor_metrics.get('total_sloc', 'N/A')}")
                        logger.info(f"Refactored Total LLOC: {refactor_metrics.get('total_lloc', 'N/A')}")
                        logger.info(f"Refactored Total Comments: {refactor_metrics.get('total_comments', 'N/A')}")
                        logger.info(f"Refactored Total Multi: {refactor_metrics.get('total_multi', 'N/A')}")
                        logger.info(f"Refactored Total Blank: {refactor_metrics.get('total_blank', 'N/A')}")
                        logger.info(f"Refactored Total CycloComp: {refactor_metrics.get('total_cyclomatic', 'N/A')}")
                        
                    except Exception as e:
                        logger.error(f"Failed to analyze metrics: {e}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to compute metrics after refactoring: {e}")
                refactor_metrics = {}
            
            # Run tests to make sure functionality is preserved
            eval_results = central_repo.evaluate()
            logger.info(f"Refactored repo test results: {eval_results['num_passed']}/{eval_results['num_tests']} tests passing ({eval_results['passed']*100:.1f}%)")
            with open(os.path.join(central_repo.repo_path, "results.json"), 'w') as wf:
                json.dump({"pytest": eval_results, "metrics_before": original_metrics, "metrics_after": refactor_metrics}, wf, indent=4)

def main():
    parser = argparse.ArgumentParser(description="LLM Repository Refactor")
    parser.add_argument("--model", type=str, required=True, help="Model to use for refactoring")
    parser.add_argument("--task", type=str, choices=["make_personas", "implement", "refactor"], required=True, help="Task to perform")
    parser.add_argument("--iterative", action="store_true", help="Whether to perform task until it passes")
    parser.add_argument("--suffixes", type=str, nargs="*", default=["_0"], help="List of suffixes for task.")
    parser.add_argument("--starter-repo-path", type=str, required=True, help="Path to starter repository")
    parser.add_argument("--repos_to_refactor", type=str, nargs="*", help="Path to repositories to factor together. Will group into 3s")
    
    args = parser.parse_args()
    
    agent = None
    if args.model.startswith("gpt") or args.model in {"o3-mini", "o4-mini"}:
        agent = OpenAIAgent(args.model)
    elif args.model.startswith("claude"):
        agent = ClaudeAgent('claude-3-7-sonnet-20250219')

    if agent is None:
        raise ValueError(f"Unknown model: {args.model}")

    if args.task == 'make_personas':
        make_personas(agent, args)
    elif args.task == 'implement':
        implement(agent, args)
    elif args.task == "refactor":
        refactor(agent, args)
            

if __name__ == "__main__":
    main()
