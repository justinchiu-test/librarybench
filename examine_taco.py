import datasets
import json


def get_solutions(xs):
    examples = []
    for x in xs:
        solutions = json.loads(x["solutions"])
        if len(solutions) > 0:
            x["solutions"] = solutions
            examples.append(x)
    return examples


def main():
    dataset = datasets.load_dataset("BAAI/TACO", trust_remote_code=True)
    train = dataset["train"]
    # len = 4695
    datastructures = [x for x in train if "Data structures" in x["skill_types"]]
    # len = 1886
    search = [x for x in train if "Complete search" in x["skill_types"]]

    # 3993
    datastructures = get_solutions(datastructures)
    # 1576
    search = get_solutions(search)

    # First print the available keys from the first example
    if search:
        print("Available keys in the first example:")
        print(list(search[0].keys()))

    # Print a couple examples from the search list
    print("\nSample search examples:")
    for i, example in enumerate(search[:2]):
        print(f"\n=== Example {i + 1} ===")
        print(f"Question: {example['question']}")
        print(f"Difficulty: {example['difficulty']}")
        print(f"Skill types: {example['skill_types']}")
        print(f"Source: {example['source']}")

        # Show solution with better formatting
        print("\nSolution:")
        print("---------")
        print(example["solutions"][0])
        print("---------")

    # No need for debugger breakpoint anymore
    # import ipdb; ipdb.set_trace()


if __name__ == "__main__":
    main()
