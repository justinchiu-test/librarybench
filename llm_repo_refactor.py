import os
import json
import shutil
import subprocess
from pathlib import Path
from collections import Counter
import logging
import argparse
from typing import List

from agent import OpenAIAgent, ClaudeAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Repo:
    def __init__(self, repo_path, src_code_files, test_files, task_files, test_command="pytest"):
        self.logger = logger
        self.repo_path = repo_path
        self.src_code_files = src_code_files
        self.test_files = test_files
        self.task_files = task_files
        self.test_command = test_command

    def update_src_files(self, new_src_files):
        self.src_code_files.extend([new_file for new_file in new_src_files if new_file not in self.src_code_files])

    def make_new_to_implement(self, agent) -> 'Repo':
        new_repo_location = os.path.join(os.path.dirname(self.repo_path), f"{os.path.basename(self.repo_path)}_{agent.model_name}")
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
        return Repo(new_repo_location, [], self.test_files, self.task_files, self.test_command)

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
            results.append(Repo(new_repo_location, self.src_code_files, self.test_files, self.task_files, self.test_command))
        
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


def main():
    parser = argparse.ArgumentParser(description="LLM Repository Refactor")
    parser.add_argument("--model", type=str, required=True, help="Model to use for refactoring")
    parser.add_argument("--task", type=str, choices=["implement", "refactor"], required=True, help="Task to perform")
    parser.add_argument("--starter-repo-path", type=str, required=True, help="Path to starter repository")
    parser.add_argument("--src-code-files", type=str, nargs="*", default=[], help="List of source code files (for refactoring)")
    parser.add_argument("--test-files", type=str, nargs="*", required=True, help="List of test files")
    parser.add_argument("--task-files", type=str, nargs="*", required=True, help="List of task description files")
    
    args = parser.parse_args()
    
    agent = None
    if args.model.startswith("gpt") or args.model in {"o3-mini", "o4-mini"}:
        agent = OpenAIAgent(args.model)
    elif args.model.startswith("claude"):
        agent = ClaudeAgent('claude-3-7-sonnet-20250219')

    if agent is None:
        raise ValueError(f"Unknown model: {args.model}")

    if args.task == 'implement':
        orig_repo = Repo(args.starter_repo_path, [], args.test_files, args.task_files)
        new_repo_location = os.path.join(os.path.dirname(args.starter_repo_path), f"{os.path.basename(args.starter_repo_path)}_{agent.model_name}")
        
        # Update SRC_FILES.txt with refactored files
        src_files_path = os.path.join(new_repo_location, "SRC_FILES.txt")
        
        # If SRC_FILES.txt already exists, read its content
        existing_files = []
        if os.path.exists(src_files_path):
            try:
                with open(src_files_path, 'r') as rf:
                    existing_files = list(line.strip() for line in rf.readlines() if line.strip())
            except Exception as e:
                logger.error(f"Error reading existing SRC_FILES.txt: {e}")
            repo = Repo(new_repo_location, existing_files, args.test_files, args.task_files)
        else:
            repo = orig_repo.make_new_to_implement(agent)
            new_src_files = agent.implement_repo(repo)
            repo.update_src_files(new_src_files)
        # Track success rates over different iterations
        num_attempts = 0
        attempt_results = []
        num_no_changes = 0
        
        while repo.evaluate()["passed"] < 1:
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
        
    elif args.task == "refactor":
        src_files_path = os.path.join(args.starter_repo_path, "SRC_FILES.txt")
        # If SRC_FILES.txt already exists, read its content
        existing_files = []
        if os.path.exists(src_files_path):
            try:
                with open(src_files_path, 'r') as rf:
                    existing_files = list(line.strip() for line in rf.readlines() if line.strip())
            except Exception as e:
                logger.error(f"Error reading existing SRC_FILES.txt: {e}")
        orig_repo = Repo(args.starter_repo_path, existing_files, args.test_files, args.task_files)
        new_repos = orig_repo.make_copies_to_refactor(agent, ['_0', '_1'])
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
            

if __name__ == "__main__":
    main()

# example usage: 
# implement repo
# python llm_repo_refactor.py --model o4-mini --task implement --starter-repo-path workflow_orchestration --test-files tests.py --task-files TASK.md TASK_v2.md
# refactor repo
# python llm_repo_refactor.py --model claude --task refactor  --starter-repo-path workflow_orchestration_o4-mini --test-files tests.py --task-files TASK.md TASK_v2.md
