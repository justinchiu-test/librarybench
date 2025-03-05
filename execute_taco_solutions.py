import os
import json
import re
import requests
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




def evaluate_solutions(solution_file):
    """Evaluate generated solutions from the given file"""
    # Load solutions
    with open(solution_file, "r") as f:
        solutions = json.load(f)

    results = []

    for i, solution_data in enumerate(solutions):
        print(
            f"Evaluating problem {i + 1}: {solution_data['source']} (Difficulty: {solution_data['difficulty']})"
        )

        # Use the input_output field directly from the solution data
        input_output = solution_data.get("input_output")
        if not input_output:
            print(f"  No input_output field found in solution data for problem {i + 1}")
            continue

        # Parse input_output if it's a string
        if isinstance(input_output, str):
            try:
                input_output = json.loads(input_output)
            except json.JSONDecodeError:
                print(f"  Error parsing input_output JSON for problem {i + 1}")
                continue

        # Format as stdin/stdout tests
        stdin_stdout_tests = []
        if "inputs" in input_output and "outputs" in input_output:
            for inp, out in zip(input_output["inputs"], input_output["outputs"]):
                stdin_stdout_tests.append({"stdin": inp, "stdout": out})

        if not stdin_stdout_tests:
            print(f"  No test cases found for problem {i + 1}")
            continue

        print(f"  Found {len(stdin_stdout_tests)} test cases")

        # Extract code from the solution
        model_code = extract_code(solution_data.get("o3_mini_solution", solution_data.get("claude_solution", "")))
        human_code = solution_data.get("human_solution", "")

        # Run code against test cases
        model_results = run_unit_tests([model_code], stdin_stdout_tests)
        human_results = (
            run_unit_tests([human_code], stdin_stdout_tests) if human_code else []
        )

        # Summarize results - each element in model_results is a list of test results for each test
        model_passed = sum(
            1 for result in model_results[0] if result.get("passed", False)
        )
        human_passed = (
            sum(1 for result in human_results[0] if result.get("passed", False))
            if human_results
            else 0
        )

        print(
            f"  Model solution: {model_passed}/{len(stdin_stdout_tests)} tests passed"
        )
        if human_code:
            print(
                f"  Human solution: {human_passed}/{len(stdin_stdout_tests)} tests passed"
            )

        # Save detailed results
        result_entry = {
            "problem_id": i,
            "model_tests_passed": model_passed,
            "model_tests_total": len(stdin_stdout_tests),
            "human_tests_passed": human_passed,
            "human_tests_total": len(stdin_stdout_tests),
            "detailed_model_results": model_results[0] if model_results else [],
            "detailed_human_results": human_results[0] if human_results else [],
        }
        
        # Include all original keys from solution_data
        for key, value in solution_data.items():
            if key not in result_entry:
                result_entry[key] = value
        
        results.append(result_entry)

    # Save results to file
    output_file = solution_file.replace(".json", "_execution_results.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Execution results saved to {output_file}")

    # Print summary
    model_total_passed = sum(r["model_tests_passed"] for r in results)
    model_total_tests = sum(r["model_tests_total"] for r in results)
    human_total_passed = sum(r["human_tests_passed"] for r in results)
    human_total_tests = sum(r["human_tests_total"] for r in results)

    if model_total_tests > 0:
        print("\nSummary:")
        print(
            f"Model solutions: {model_total_passed}/{model_total_tests} tests passed ({model_total_passed / model_total_tests * 100:.2f}%)"
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
    evaluate_solutions("o3mini_search_solutions.json")
    
    # Uncomment to evaluate data structure problems as well
    # print("\nEvaluating data structure problem solutions...")
    # evaluate_solutions("o3mini_datastructure_solutions.json")


if __name__ == "__main__":
    main()
