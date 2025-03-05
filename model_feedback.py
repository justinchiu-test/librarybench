import os
import json
import re
import asyncio
import aiohttp
from tqdm import tqdm
from typing import List, Dict, Any, Tuple

# URL for execution API - load from environment variable
CYBER_URL: str = os.getenv("CYBER_URL", "")
if not CYBER_URL:
    raise ValueError("Please set the CYBER_URL environment variable")


# Function to extract code from model's solution
def extract_code(solution):
    # For O3 mini solutions, try to extract code between dashed lines
    dashed_code_pattern = r"[-]{5,}\n(.*?)[-]{5,}"
    match = re.search(dashed_code_pattern, solution, re.DOTALL)
    if match:
        return match.group(1)

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


async def execute_test(
    session: aiohttp.ClientSession,
    code: str,
    test: Dict[str, str],
    semaphore: asyncio.Semaphore,
) -> Dict[str, Any]:
    """Execute a single test against the execution API"""
    async with semaphore:
        code_dict = {
            "code": code,
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
            async with session.post(
                CYBER_URL, json=code_dict, params=params
            ) as response:
                result = await response.json()
                return result
        except Exception as e:
            return {
                "passed": False,
                "exec_output": {"run_output": {"stderr": str(e)}},
                "uncaught_exception": str(e),
            }


async def run_unit_tests_async(
    generations: List[str], stdin_stdout_tests: List[Dict[str, str]]
) -> List[List[Dict[str, Any]]]:
    """Execute code against unit tests using the execution API asynchronously"""
    outputs = []
    semaphore = asyncio.Semaphore(512)  # Limit concurrency to 512 simultaneous requests

    async with aiohttp.ClientSession() as session:
        for generation in tqdm(generations, desc="Running tests"):
            tasks = [
                execute_test(session, generation, test, semaphore)
                for test in stdin_stdout_tests
            ]
            test_results = await asyncio.gather(*tasks)
            outputs.append(test_results)

    return outputs


def run_unit_tests(generations, stdin_stdout_tests):
    """Execute code against unit tests using the execution API"""
    return asyncio.run(run_unit_tests_async(generations, stdin_stdout_tests))


def create_test_cases_from_input_output(input_output: Dict) -> List[Dict[str, str]]:
    """Convert input-output pairs to test cases for execution"""
    stdin_stdout_tests = []
    if "inputs" in input_output and "outputs" in input_output:
        for inp, out in zip(input_output["inputs"], input_output["outputs"]):
            stdin_stdout_tests.append({"stdin": inp, "stdout": out})
    return stdin_stdout_tests


def format_feedback(
    test_results: List[Dict[str, Any]], 
    test_cases: List[Dict[str, str]],
    passed_count: int,
    total_count: int
) -> str:
    """Format test results as feedback for the model"""
    feedback = f"Test Results: {passed_count}/{total_count} tests passed\n\n"
    
    for i, (test, result) in enumerate(zip(test_cases, test_results), 1):
        status = "✅ PASSED" if result.get("passed", False) else "❌ FAILED"
        feedback += f"Test #{i}: {status}\n"
        feedback += f"Input:\n{test['stdin']}\n"
        feedback += f"Expected Output:\n{test['stdout']}\n"
        
        if not result.get("passed", False):
            stdout = result.get("exec_output", {}).get("run_output", {}).get("stdout", "")
            stderr = result.get("exec_output", {}).get("run_output", {}).get("stderr", "")
            feedback += f"Actual Output:\n{stdout}\n"
            if stderr:
                feedback += f"Error:\n{stderr}\n"
        
        feedback += "-" * 40 + "\n"
    
    return feedback


def get_model_feedback(
    solution_file: str, 
    problem_id: int = None,
    model_name: str = None
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Get feedback for a specific model solution
    
    Args:
        solution_file: Path to the solution JSON file
        problem_id: ID of the problem to get feedback for (optional)
        model_name: Name of the model (e.g., 'claude' or 'o3_mini')
        
    Returns:
        Tuple of (feedback string, detailed test results)
    """
    # Load solutions
    with open(solution_file, "r") as f:
        solutions = json.load(f)
    
    # If problem_id specified, filter to that problem
    if problem_id is not None:
        solutions = [solutions[problem_id]]
    
    # Track all feedbacks
    all_feedbacks = []
    all_results = []
    
    for solution_data in solutions:
        # Use the input_output field directly from the solution data
        input_output = solution_data.get("input_output")
        if not input_output:
            continue

        # Parse input_output if it's a string
        if isinstance(input_output, str):
            try:
                input_output = json.loads(input_output)
            except json.JSONDecodeError:
                continue

        # Format as stdin/stdout tests
        stdin_stdout_tests = create_test_cases_from_input_output(input_output)
        if not stdin_stdout_tests:
            continue

        # Extract code from the solution based on model name
        if model_name == 'o3_mini' and "o3_mini_solution" in solution_data:
            model_code = extract_code(solution_data.get("o3_mini_solution", ""))
        else:  # default to claude
            model_code = extract_code(solution_data.get("claude_solution", ""))

        # Run code against test cases
        model_results = run_unit_tests([model_code], stdin_stdout_tests)
        
        # Calculate passed tests
        model_results_flat = model_results[0] if model_results else []
        passed = sum(1 for result in model_results_flat if result.get("passed", False))
        total = len(stdin_stdout_tests)
        
        # Format feedback
        feedback = format_feedback(
            model_results_flat, 
            stdin_stdout_tests,
            passed, 
            total
        )
        
        all_feedbacks.append(feedback)
        all_results.append(model_results_flat)
    
    return "\n".join(all_feedbacks), all_results


def main():
    # Check if CYBER_URL is set
    if not CYBER_URL:
        print("Error: CYBER_URL environment variable is not set")
        return

    # Command line arguments handling could be added here
    # For now, we'll just use default values
    
    # Get feedback for Claude solutions
    print("Getting feedback for Claude search problem solutions...")
    feedback, _ = get_model_feedback("claude_search_solutions.json", model_name="claude")
    print(feedback)
    
    # Get feedback for O3 mini solutions
    print("\nGetting feedback for O3 mini search problem solutions...")
    feedback, _ = get_model_feedback("o3mini_search_solutions.json", model_name="o3_mini")
    print(feedback)


if __name__ == "__main__":
    main()