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

from agent import OpenAIAgent, ClaudeAgent
from prompts import (
    feature_ask_prompt_template,
    persona_prompt_template,
    library_ask_prompt,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Repo:
    def __init__(self, repo_path, test_command="pytest"):
        self.logger = logger
        self.repo_path = repo_path

    def evaluate(self):
        test_files = [test_file_path[len(self.repo_path)+1:] for test_file_path in glob.glob(os.path.join(self.repo_path, "test_*.py"))]
        test_cmd = f"pytest {' '.join(test_files)} --json-report --json-report-file=report.json --continue-on-collection-errors > test_output.txt 2>&1"
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
                executable="/bin/bash",  # ensure we're using bash for the source command
            )
            result = {
                "returncode": process.returncode,
                "stdout": process.stdout,
                "stderr": process.stderr,
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
                    test_results = [
                        test["call"]
                        for test in report.get("tests", [])
                        if "call" in test
                    ]
                else:
                    # Old version: assume report is a list and filter tests with "when" equal to "call".
                    test_results = [
                        test for test in report if test.get("when") == "call"
                    ]
                num_tests = len(test_results)

                # Include collector failures
                collector_failures = [
                    collector
                    for collector in report.get("collectors", [])
                    if collector.get("outcome") == "failed"
                ]
                # Each failed collector represents a test file that didn't run any tests due to an error
                num_collector_failures = len(collector_failures)
                num_tests += num_collector_failures  # treat each as a failed test
                num_passed = sum(
                    1
                    for test in test_results
                    if test.get("outcome") in ("passed", "xfail")
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
                num_passed = outcome_counter.get("passed", 0) + outcome_counter.get(
                    "xfail", 0
                )
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


def propose_libraries(agent, args):
    new_libraries = set()
    while len(new_libraries) < args.num_new_generations:
        response = agent.generate(
            library_ask_prompt, {"temperature": 0.3}, system_prompt=""
        )
        # Extract new task files
        file_blocks = response.split("```file:")
        for block in file_blocks[1:]:
            lines = block.split("\n")
            if not lines:
                continue

            file_path = lines[0].strip()
            library_name = re.search(r"(.+)/DESCRIPTION.md", file_path)
            if not library_name:
                continue
            library_name = library_name.group(1)

            content_parts = "\n".join(lines[1:]).split("```")
            if not content_parts:
                continue
            file_content = content_parts[0]
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as wf:
                wf.write(file_content)
            new_libraries.add(os.path.dirname(file_path))
    return new_libraries


def make_personas(agent, args):
    # ask LLM for features
    task_content = ""
    task_file = os.path.join(args.starter_repo_path, "DESCRIPTION.md")
    if not os.path.exists(task_file):
        return
    with open(task_file, "r") as f:
        content = f.read()
        task_content += f"\n{content}"

    response = agent.generate(
        feature_ask_prompt_template.format(task_content=task_content),
        {"temperature": 0.3},
        system_prompt="",
    )

    all_features = {}
    # Extract features
    for feature in re.finditer(r"\n\d+:([^:]+):(.+)", response):
        all_features[feature.group(1).strip()] = feature.group(2).strip()

    # Subsample features into ten personas that would use it.
    new_personas = set()
    while len(new_personas) < args.num_new_generations:
        features = random.sample(sorted(all_features), 10)
        persona_prompt = persona_prompt_template.format(
            library_name=args.starter_repo_path,
            listed_features="\n".join(
                [
                    f"- {feature_name}: {all_features[feature_name]}"
                    for feature_name in features
                ]
            )
        )

        response = agent.generate(
            persona_prompt, {"temperature": 0.3}, system_prompt=""
        )
        # Extract new task files
        file_blocks = response.split("```file:")
        for block in file_blocks[1:]:
            lines = block.split("\n")
            if not lines:
                continue

            file_path = lines[0].strip()
            persona_name = re.search(rf"{args.starter_repo_path}/(.+)/TASK.md", file_path)
            if not persona_name:
                continue
            persona_name = persona_name.group(1)

            content_parts = "\n".join(lines[1:]).split("```")
            if not content_parts:
                continue

            file_content = content_parts[0]
            new_repo_location = os.path.join(args.starter_repo_path, persona_name)
            os.makedirs(new_repo_location, exist_ok=True)
            task_file_path = os.path.join(new_repo_location, "TASK.md")
            with open(task_file_path, "w") as wf:
                wf.write(file_content)
            new_personas.add(persona_name)


def implement(agent, args):
    # For the different attempts of implementation
    for suffix in args.suffixes:
        new_repo_location = os.path.join(
            os.path.dirname(args.starter_repo_path),
            f"{os.path.basename(args.starter_repo_path)}_{agent.model_name}{suffix}",
        )
        if os.path.exists(new_repo_location):
            do_reimplement = (
                input(f"{new_repo_location} already exists. Re-implement? [y/]").strip()
                == "y"
            )
            if not do_reimplement:
                continue
            shutil.rmtree(new_repo_location)
        shutil.copytree(args.starter_repo_path, new_repo_location)

        # Implement each persona in the subdir
        for persona_subdir in glob.glob(os.path.join(new_repo_location, "*")):
            if not os.path.isdir(persona_subdir):
                continue
            repo = Repo(persona_subdir)
            agent.implement_repo(repo)
            # Track success rates over different iterations
            num_attempts = 0
            attempt_results = []
            eval_result = repo.evaluate()
            while eval_result["passed"] < 1:
                if num_attempts > 5:
                    logger.warning("Reached maximum number of fix attempts (5)")
                    break
                logger.info(f"Fix implementation attempt #{num_attempts + 1}")
                attempt_results.append({"attempt": num_attempts, "before": eval_result})

                agent.fix_implementation(repo)
                num_attempts += 1
                new_eval = repo.evaluate()
                attempt_results[-1]["after"] = new_eval

                # Log progress for this attempt
                logger.info(f"Fix attempt #{num_attempts} results:")
                logger.info(
                    f"  - Before: {eval_result['num_passed']}/{eval_result['num_tests']} tests passing ({eval_result['passed']*100:.1f}%)"
                )
                logger.info(
                    f"  - After: {new_eval['num_passed']}/{new_eval['num_tests']} tests passing ({new_eval['passed']*100:.1f}%)"
                )
                logger.info(
                    f"  - Improvement: {(new_eval['passed'] - eval_result['passed'])*100:.1f}% more tests passing"
                )
                eval_result = new_eval

            print(eval_result)


def setup_for_refactor(args):
    """Move all test_*.py files into a unified test directory structure.

    This function takes test files scattered throughout the repository and
    moves them into a unified test directory at args.starter_repo_path/unified/tests/
    preserving their test names but organizing them consistently.
    """
    if not args.starter_repo_path:
        raise ValueError("No starter repo path provided")

    # Create unified test directory if it doesn't exist
    unified_test_dir = os.path.join(args.starter_repo_path, "unified", "tests")
    os.makedirs(unified_test_dir, exist_ok=True)

    # Find all test files in the repository (excluding those already in unified/tests)
    logger.info(f"Looking for test files in {args.starter_repo_path}")
    test_files = []
    for root, _, files in os.walk(args.starter_repo_path):
        if "unified/tests" in root:
            continue  # Skip files already in unified/tests
        persona_name = root[len(args.starter_repo_path)+1:]
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                mod_filename = f"test_{persona_name}_{os.path.basename(file)[len('test_'):]}"
                test_files.append((os.path.join(root, file), os.path.join(unified_test_dir, mod_filename)))

    logger.info(f"Found {len(test_files)} test files to move")

    # Move each test file to the unified test directory with appropriate naming
    for test_file_orig, test_file_dest in test_files:

        # Move the file 
        logger.info(f"Moving {test_file_orig} to {test_file_dest}")
        shutil.move(test_file_orig, test_file_dest)

    logger.info(f"Successfully moved {len(test_files)} test files to {unified_test_dir}")


def main():
    parser = argparse.ArgumentParser(description="LLM Repository Refactor")
    parser.add_argument(
        "--model", type=str, default=None, help="Model to use for refactoring"
    )
    parser.add_argument(
        "--task",
        type=str,
        choices=["propose_libraries", "make_personas", "implement", "setup_for_refactor"],
        required=True,
        help="Task to perform",
    )
    parser.add_argument(
        "--num_new_generations",
        type=int,
        help="Number of new generations, when producing new libraries or personas",
    )
    parser.add_argument(
        "--suffixes",
        type=str,
        nargs="*",
        default=["_0"],
        help="List of suffixes for task.",
    )
    parser.add_argument(
        "--starter-repo-path", type=str, help="Path to starter repository"
    )

    args = parser.parse_args()

    agent = None
    if args.model.startswith("gpt") or args.model in {"o3-mini", "o4-mini"}:
        agent = OpenAIAgent(args.model)
    elif args.model.startswith("claude"):
        agent = ClaudeAgent("claude-3-7-sonnet-20250219")

    if agent is None:
        raise ValueError(f"Unknown model: {args.model}")

    if args.task == "propose_libraries":
        propose_libraries(agent, args)
    elif args.task == "make_personas":
        make_personas(agent, args)
    elif args.task == "implement":
        implement(agent, args)
    elif args.task == "setup_for_refactor":
        setup_for_refactor(args)


if __name__ == "__main__":
    main()
