import os
import ipdb
import json
import re
import requests
import datasets
from tqdm import tqdm

# URL for execution API - load from environment variable
CYBER_URL = os.getenv("CYBER_URL")
if not CYBER_URL:
    raise ValueError("Please set the CYBER_URL environment variable")


# Function to extract code from Claude's solution
def extract_code(solution):
    # Try to extract code between ```python and ``` markers
    code_pattern = r"```python\n(.*?)\n```"
    match = re.search(code_pattern, solution, re.DOTALL)
    if match:
        return match.group(1)

    # If no markers found, try to extract the first code-like block
    code_pattern = r"class .*?:|def .*?:"
    match = re.search(code_pattern, solution)
    if match:
        # Get the position of the match
        start_pos = match.start()
        # Extract from this position to the end
        return solution[start_pos:]

    return solution


def run_unit_tests(generations, stdin_stdout_tests):
    """Execute code against unit tests using the execution API"""
    outputs = []
    for generation in tqdm(generations, desc="Running tests"):
        test_results = []

        # Process each test separately
        for test in stdin_stdout_tests:
            # Create the request
            code_dict = {
                "code": generation,
                "test": test,
            }

            params = {
                "language": "python",
                "environment": "default",
                "timeout": 30,
                "generation_formatting": "true",
                "fill_missing_imports": "true",
            }

            try:
                response = requests.post(CYBER_URL, json=code_dict, params=params)
                result = response.json()
                test_results.append(result)
            except Exception as e:
                test_results.append(
                    {
                        "passed": False,
                        "exec_output": {"run_output": {"stderr": str(e)}},
                        "uncaught_exception": str(e),
                    }
                )

        outputs.append(test_results)
    return outputs


def fetch_taco_tests(problem_id):
    """Fetch test cases from the TACO dataset for a given problem ID"""
    # Load the TACO dataset
    dataset = datasets.load_dataset("BAAI/TACO", trust_remote_code=True)
    train = dataset["train"]

    # Find problem by ID (assuming ID is position in the dataset)
    if problem_id < len(train):
        problem = train[problem_id]
        input_output = (
            json.loads(problem["input_output"])
            if isinstance(problem["input_output"], str)
            else problem["input_output"]
        )

        # Format as stdin/stdout tests
        tests = []
        if "inputs" in input_output and "outputs" in input_output:
            for inp, out in zip(input_output["inputs"], input_output["outputs"]):
                tests.append({"stdin": inp, "stdout": out})
        return tests
    return []


def evaluate_solutions(solution_file):
    """Evaluate generated solutions from the given file"""
    # Load solutions
    with open(solution_file, "r") as f:
        solutions = json.load(f)

    # Load the TACO dataset
    dataset = datasets.load_dataset("BAAI/TACO", trust_remote_code=True)
    train = dataset["train"]

    results = []

    for i, solution_data in enumerate(solutions):
        print(
            f"Evaluating problem {i + 1}: {solution_data['source']} (Difficulty: {solution_data['difficulty']})"
        )

        # Find matching problem in TACO dataset
        matching_problems = []
        for j, problem in enumerate(train):
            # Match by question content
            if solution_data["problem"] in problem["question"]:
                matching_problems.append((j, problem))

        if not matching_problems:
            print(f"  No matching problem found in TACO dataset for problem {i + 1}")
            continue

        problem_id, problem = matching_problems[0]  # Use first match

        # Extract test cases from the input_output field
        input_output = (
            json.loads(problem["input_output"])
            if isinstance(problem["input_output"], str)
            else problem["input_output"]
        )

        # Format as stdin/stdout tests
        stdin_stdout_tests = []
        if "inputs" in input_output and "outputs" in input_output:
            for inp, out in zip(input_output["inputs"], input_output["outputs"]):
                stdin_stdout_tests.append({"stdin": inp, "stdout": out})

        if not stdin_stdout_tests:
            print(f"  No test cases found for problem {i + 1}")
            ipdb.set_trace()
            continue

        print(f"  Found {len(stdin_stdout_tests)} test cases")

        # Extract code from Claude's solution
        claude_code = extract_code(solution_data["claude_solution"])
        human_code = solution_data.get("human_solution", "")

        # Run code against test cases
        claude_results = run_unit_tests([claude_code], stdin_stdout_tests)
        human_results = (
            run_unit_tests([human_code], stdin_stdout_tests) if human_code else []
        )
        ipdb.set_trace()

        # Summarize results - each element in claude_results is a list of test results for each test
        claude_passed = sum(
            1 for result in claude_results[0] if result.get("passed", False)
        )
        human_passed = (
            sum(1 for result in human_results[0] if result.get("passed", False))
            if human_results
            else 0
        )

        print(
            f"  Claude solution: {claude_passed}/{len(stdin_stdout_tests)} tests passed"
        )
        if human_code:
            print(
                f"  Human solution: {human_passed}/{len(stdin_stdout_tests)} tests passed"
            )

        # Save detailed results
        results.append(
            {
                "problem_id": i,
                "taco_problem_id": problem_id,
                "source": solution_data["source"],
                "difficulty": solution_data["difficulty"],
                "claude_tests_passed": claude_passed,
                "claude_tests_total": len(stdin_stdout_tests),
                "human_tests_passed": human_passed,
                "human_tests_total": len(stdin_stdout_tests),
                "detailed_claude_results": claude_results[0] if claude_results else [],
                "detailed_human_results": human_results[0] if human_results else [],
            }
        )

    # Save results to file
    output_file = solution_file.replace(".json", "_execution_results.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Execution results saved to {output_file}")

    # Print summary
    claude_total_passed = sum(r["claude_tests_passed"] for r in results)
    claude_total_tests = sum(r["claude_tests_total"] for r in results)
    human_total_passed = sum(r["human_tests_passed"] for r in results)
    human_total_tests = sum(r["human_tests_total"] for r in results)

    if claude_total_tests > 0:
        print("\nSummary:")
        print(
            f"Claude solutions: {claude_total_passed}/{claude_total_tests} tests passed ({claude_total_passed / claude_total_tests * 100:.2f}%)"
        )
        if human_total_tests > 0:
            print(
                f"Human solutions: {human_total_passed}/{human_total_tests} tests passed ({human_total_passed / human_total_tests * 100:.2f}%)"
            )


def main():
    # Check if CYBER_URL is set
    if not CYBER_URL:
        print("Error: CYBER_URL environment variable is not set")
        return

    # Evaluate solutions
    print("Evaluating search problem solutions...")
    evaluate_solutions("claude_search_solutions.json")

    print("\nEvaluating data structure problem solutions...")
    evaluate_solutions("claude_datastructure_solutions.json")


if __name__ == "__main__":
    main()
