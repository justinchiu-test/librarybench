import os
import json
import datasets
import anthropic
from tqdm import tqdm

# Load API key from environment variable
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("Please set the ANTHROPIC_API_KEY environment variable")

client = anthropic.Anthropic(api_key=api_key)

def get_solutions(xs):
    """Extract examples with valid solutions."""
    examples = []
    for x in xs:
        solutions = json.loads(x["solutions"])
        if len(solutions) > 0:
            x["solutions"] = solutions
            examples.append(x)
    return examples

def format_prompt(example):
    """Format the problem for Claude."""
    prompt = f"""
You are an expert programming problem solver. Please solve the following problem using efficient algorithms and provide a well-commented solution.

Problem:
{example['question']}

Please provide a clear, efficient solution in Python. Make sure to handle edge cases and optimize for the expected time and space complexity.
"""
    return prompt

def generate_solution(example, max_retries=2):
    """Generate a solution using Anthropic API."""
    prompt = format_prompt(example)
    
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=4000,
                temperature=0.1,
                system="You are an expert programming problem solver specializing in competitive programming and algorithm challenges.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return {
                "problem": example["question"],
                "difficulty": example["difficulty"],
                "skill_types": example["skill_types"],
                "source": example["source"],
                "human_solution": example["solutions"][0] if example["solutions"] else None,
                "claude_solution": response.content[0].text,
            }
        except Exception as e:
            print(f"Error on attempt {attempt+1}: {e}")
            if attempt == max_retries - 1:
                return {
                    "problem": example["question"],
                    "difficulty": example["difficulty"],
                    "skill_types": example["skill_types"],
                    "source": example["source"],
                    "human_solution": example["solutions"][0] if example["solutions"] else None,
                    "claude_solution": f"ERROR: {str(e)}",
                }

def main():
    # Load the TACO dataset
    dataset = datasets.load_dataset("BAAI/TACO", trust_remote_code=True)
    train = dataset["train"]
    
    # Filter for problems with specific skills
    search_problems = [x for x in train if "Complete search" in x["skill_types"]]
    datastructure_problems = [x for x in train if "Data structures" in x["skill_types"]]
    
    # Get examples with solutions
    search_examples = get_solutions(search_problems)
    datastructure_examples = get_solutions(datastructure_problems)
    
    # Select a small sample for testing
    sample_size = 1  # Start with just 1 example to test
    search_sample = search_examples[:sample_size]
    datastructure_sample = datastructure_examples[:sample_size]
    
    # Generate solutions
    print(f"Generating solutions for {sample_size} search problems...")
    search_results = []
    for example in tqdm(search_sample):
        result = generate_solution(example)
        search_results.append(result)
    
    print(f"Generating solutions for {sample_size} data structure problems...")
    datastructure_results = []
    for example in tqdm(datastructure_sample):
        result = generate_solution(example)
        datastructure_results.append(result)
    
    # Save results
    with open("claude_search_solutions.json", "w") as f:
        json.dump(search_results, f, indent=2)
    
    with open("claude_datastructure_solutions.json", "w") as f:
        json.dump(datastructure_results, f, indent=2)
    
    print("Done! Results saved to claude_search_solutions.json and claude_datastructure_solutions.json")

if __name__ == "__main__":
    main()