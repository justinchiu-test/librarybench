import os
import json
import re
import asyncio
import aiohttp
from tqdm import tqdm
from typing import List, Dict, Any

# URL for execution API - load from environment variable
CYBER_URL: str = os.getenv("CYBER_URL", "")
if not CYBER_URL:
    raise ValueError("Please set the CYBER_URL environment variable")


# Import LLM client classes
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
try:
    from taco_solution_generator import OpenAiClient, ClaudeClient
except ImportError:
    # Define fallback classes if import fails
    class OpenAiClient:
        def extract_code(self, solution):
            """Extract code from OpenAI solution."""
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
            
    class ClaudeClient:
        def extract_code(self, solution):
            """Extract code from Claude solution."""
            # Try to extract code between ```python and ``` markers (Claude's standard format)
            code_pattern = r"```python\n(.*?)\n```"
            match = re.search(code_pattern, solution, re.DOTALL)
            if match:
                return match.group(1)
                
            # If no python markers found, try with any language marker
            code_pattern = r"```(?:\w+)?\n(.*?)\n```"
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

# Function to extract code from model solutions
def extract_code(solution, model_type=None):
    """
    Extract code from model solutions using the appropriate extractor.
    
    Args:
        solution: String containing the model's solution
        model_type: Optional string indicating the model type ('openai' or 'claude')
                   If None, will try to detect from solution format
    
    Returns:
        The extracted code
    """
    # If model type is explicitly provided
    if model_type == "openai":
        extractor = OpenAiClient()
        return extractor.extract_code(solution)
    elif model_type == "claude":
        extractor = ClaudeClient()
        return extractor.extract_code(solution)
    
    # Auto-detect model type based on solution patterns
    # Check for OpenAI's dash pattern first (more specific)
    dashed_code_pattern = r"[-]{5,}\n(.*?)[-]{5,}"
    if re.search(dashed_code_pattern, solution, re.DOTALL):
        extractor = OpenAiClient()
        return extractor.extract_code(solution)
    
    # Default to Claude-style extraction (which is more general)
    extractor = ClaudeClient()
    return extractor.extract_code(solution)


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

        # Extract code from the solution - find model-specific solution key
        model_code = ""
        model_type = None
        
        # Find the first key that looks like a model solution
        for key in solution_data:
            if key.endswith("_solution") and key != "human_solution":
                # Determine model type based on key name
                if "claude" in key or "anthropic" in key:
                    model_type = "claude"
                elif "o3" in key or "gpt" in key or "openai" in key:
                    model_type = "openai"
                    
                model_code = extract_code(solution_data.get(key, ""), model_type)
                break
                
        # Fallback if no model solution found
        if not model_code:
            # Try the most common solution keys
            if "o3_mini_solution" in solution_data:
                model_code = extract_code(solution_data.get("o3_mini_solution", ""), "openai")
            elif "claude_solution" in solution_data:
                model_code = extract_code(solution_data.get("claude_solution", ""), "claude")
                
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
    output_file = os.path.join("data", os.path.basename(solution_file).replace(".json", "_execution_results.json"))
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
    """Run the evaluation with command-line arguments."""
    import argparse
    import glob
    
    # Check if CYBER_URL is set
    if not CYBER_URL:
        print("Error: CYBER_URL environment variable is not set")
        return
    
    parser = argparse.ArgumentParser(description="Evaluate generated solutions")
    parser.add_argument(
        "--files", 
        nargs="*", 
        help="Specific solution files to evaluate"
    )
    parser.add_argument(
        "--model", 
        type=str,
        help="Filter files by model name (e.g., 'o3_mini', 'claude_3_opus')"
    )
    
    args = parser.parse_args()
    
    # Use provided files, or find all solution files that don't have "execution_results" in their name
    if args.files:
        solution_files = args.files
    else:
        solution_files = [
            f for f in glob.glob("data/*_solutions.json") 
            if "execution_results" not in f
        ]
        
        # Filter by model if specified
        if args.model:
            solution_files = [f for f in solution_files if args.model in f]
    
    if not solution_files:
        print("No solution files found to evaluate.")
        return
        
    # Evaluate each file
    for solution_file in solution_files:
        print(f"\nEvaluating solutions in {solution_file}...")
        evaluate_solutions(solution_file)


if __name__ == "__main__":
    main()
