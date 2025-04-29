import os
import json
import glob
import re
import random
import shutil
import subprocess
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
        test_files = glob.glob(os.path.join(repo_path, "test*.py"))
        task_files = glob.glob(os.path.join(repo_path, "TASK*.md"))
        self.src_code_files = [filename for filename in glob.glob(os.path.join(repo_path, "*.py")) if filename not in test_files + task_files]
        self.test_files = test_files
        self.task_files = task_files
        self.test_command = test_command
        print(f"New repo implemented with test files {test_files} and task files {task_files} and src files {self.src_code_files}")

    def update_src_files(self, new_src_files):
        self.src_code_files.extend([new_file for new_file in new_src_files if new_file not in self.src_code_files])

    def make_new_to_implement(self, new_repo_location) -> 'Repo':
        # new_repo_location = os.path.join(os.path.dirname(self.repo_path), f"{os.path.basename(self.repo_path)}_{agent.model_name}")
        # if new_repo_location already exists, raise an error
        if os.path.exists(new_repo_location):
            raise FileExistsError(f"Directory {new_repo_location} already exists")
        
        # make a directory at target_repo_location and copy only the test_files and task_files in
        os.makedirs(new_repo_location, exist_ok=False)
        
        for file in self.test_files + self.task_files:
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

    def make_copies_to_refactor(self, agent, refactor_suffixes) -> List['Repo']:
        results = []
        for refactor_suffix in refactor_suffixes:
            new_repo_location = os.path.join(os.path.dirname(self.repo_path), f"{os.path.basename(self.repo_path)}_{agent.model_name}{refactor_suffix}")
            # if new_repo_location already exists, raise an error
            if os.path.exists(new_repo_location):
                continue
            
            # make a directory at target_repo_location and copy all files in
            shutil.copytree(self.repo_path, new_repo_location)
            
            # make new Repo object and add to results
            results.append(Repo(new_repo_location, self.test_command))
        
        return results

    def evaluate(self):
        test_cmd = f"pytest {' '.join(self.test_files)} --json-report --json-report-file=report.json --continue-on-collection-errors > test_output.txt 2>&1"
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
            
            new_src_files, has_changes = agent.fix_implementation(repo)
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

def refactor(agent, args):
    orig_repo = Repo(args.starter_repo_path)
    new_repos = orig_repo.make_copies_to_refactor(agent, args.suffixes)
    for new_repo in new_repos:
        agent.refactor_repo(new_repo)
        # Track success rates over different iterations
        num_attempts = 0
        attempt_results = []
        num_no_changes = 0
        
        while new_repo.evaluate()["passed"] < 1:
            logger.info(f"Fix implementation attempt #{num_attempts + 1}")
            eval_before = new_repo.evaluate()
            attempt_results.append({"attempt": num_attempts, "before": eval_before})
            
            new_src_files, has_changes = agent.fix_implementation(new_repo)
            num_attempts += 1
            new_repo.update_src_files(new_src_files)
            
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
            eval_after = new_repo.evaluate()
            attempt_results[-1]["after"] = eval_after
            
            # Log progress for this attempt
            logger.info(f"Fix attempt #{num_attempts} results:")
            logger.info(f"  - Before: {eval_before['num_passed']}/{eval_before['num_tests']} tests passing ({eval_before['passed']*100:.1f}%)")
            logger.info(f"  - After: {eval_after['num_passed']}/{eval_after['num_tests']} tests passing ({eval_after['passed']*100:.1f}%)")
            logger.info(f"  - Improvement: {(eval_after['passed'] - eval_before['passed'])*100:.1f}% more tests passing")
            
            if num_attempts > 5: 
                logger.warning("Reached maximum number of fix attempts (5)")
                break
        final_repo_results = new_repo.evaluate()
        print(final_repo_results)

def main():
    parser = argparse.ArgumentParser(description="LLM Repository Refactor")
    parser.add_argument("--model", type=str, required=True, help="Model to use for refactoring")
    parser.add_argument("--task", type=str, choices=["make_personas", "implement", "refactor"], required=True, help="Task to perform")
    parser.add_argument("--iterative", action="store_true", help="Whether to perform task until it passes")
    parser.add_argument("--suffixes", type=str, nargs="*", default=["_0", "_1", "_2", "_3"], help="List of suffixes for task.")
    parser.add_argument("--starter-repo-path", type=str, required=True, help="Path to starter repository")
    # TODO make these naturally infer from repo path
    # parser.add_argument("--src-code-files", type=str, nargs="*", default=[], help="List of source code files (for refactoring)")
    # parser.add_argument("--test-files", type=str, nargs="*", help="List of test files")
    # parser.add_argument("--task-files", type=str, nargs="*", help="List of task description files")
    
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

# example usage: 
# make personas 
# python llm_repo_refactor.py --model gpt-4o --task make_personas --starter-repo-path document_editor
# implement repo one attempt
# python llm_repo_refactor.py --model o4-mini --task implement --suffixes _0 _1 _2 _3 --starter-repo-path workflow_orchestration --test-files tests.py --task-files TASK.md TASK_v2.md
# implement repo
# python llm_repo_refactor.py --model o4-mini --task implement --iterative --starter-repo-path workflow_orchestration --test-files tests.py --task-files TASK.md TASK_v2.md
# refactor repo
# python llm_repo_refactor.py --model claude --task refactor --iterative --starter-repo-path workflow_orchestration_o4-mini --test-files tests.py --task-files TASK.md TASK_v2.md
