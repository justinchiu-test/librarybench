import json
import re
from tqdm import tqdm

# Function to extract code from solution
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

def load_and_analyze_solutions(file_path):
    with open(file_path, 'r') as f:
        results = json.load(f)
    
    problem_counts = {}
    solution_lengths = {"human": [], "claude": []}
    
    for result in results:
        # Count problem types
        for skill in eval(result["skill_types"]):
            if skill in problem_counts:
                problem_counts[skill] += 1
            else:
                problem_counts[skill] = 1
        
        # Extract code and count lines
        human_code = result["human_solution"]
        claude_code = extract_code(result["claude_solution"])
        
        human_lines = len(human_code.strip().split('\n'))
        claude_lines = len(claude_code.strip().split('\n'))
        
        solution_lengths["human"].append(human_lines)
        solution_lengths["claude"].append(claude_lines)
    
    # Calculate averages
    avg_human_length = sum(solution_lengths["human"]) / len(solution_lengths["human"])
    avg_claude_length = sum(solution_lengths["claude"]) / len(solution_lengths["claude"])
    
    return {
        "count": len(results),
        "problem_types": problem_counts,
        "avg_human_solution_length": avg_human_length,
        "avg_claude_solution_length": avg_claude_length,
        "human_solution_lengths": solution_lengths["human"],
        "claude_solution_lengths": solution_lengths["claude"]
    }

def main():
    print("Evaluating solutions...")
    
    # Load and analyze search solutions
    search_analysis = load_and_analyze_solutions("claude_search_solutions.json")
    print("\nSearch problems analysis:")
    print(f"Total problems: {search_analysis['count']}")
    print(f"Problem types: {search_analysis['problem_types']}")
    print(f"Average human solution length: {search_analysis['avg_human_solution_length']:.2f} lines")
    print(f"Average Claude solution length: {search_analysis['avg_claude_solution_length']:.2f} lines")
    
    # Load and analyze data structure solutions
    ds_analysis = load_and_analyze_solutions("claude_datastructure_solutions.json")
    print("\nData Structure problems analysis:")
    print(f"Total problems: {ds_analysis['count']}")
    print(f"Problem types: {ds_analysis['problem_types']}")
    print(f"Average human solution length: {ds_analysis['avg_human_solution_length']:.2f} lines")
    print(f"Average Claude solution length: {ds_analysis['avg_claude_solution_length']:.2f} lines")
    
    # Compare solutions
    print("\nComparison:")
    print(f"Human vs. Claude solution length ratio (Search): {search_analysis['avg_human_solution_length'] / search_analysis['avg_claude_solution_length']:.2f}")
    print(f"Human vs. Claude solution length ratio (Data Structure): {ds_analysis['avg_human_solution_length'] / ds_analysis['avg_claude_solution_length']:.2f}")

if __name__ == "__main__":
    main()