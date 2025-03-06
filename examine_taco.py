import ast
import datasets
import json


def get_solutions(xs):
    examples = []
    for x in xs:
        #solutions = json.loads(x["solutions"])
        solutions = ast.literal_eval(x["solutions"])
        if len(solutions) > 0:
            x["solutions"] = solutions
            examples.append(x)
    return examples


def count_defs_(xs):
    examples = []
    for x in xs:
        x["solution_def_count"] = [x.count("def") for x in x["solutions"]]


def filter_solutions_by_def(xs):
    good_examples = []
    for x in xs:
        prompt = x["question"]
        for sol, defs in zip(x["solutions"], x["solution_def_count"]):
            if defs > 2:
                good_examples.append((prompt, sol, x["url"]))
    return good_examples



def get_chess(xs):
    return [x for x in xs if "chess" in x["question"].lower()]

def main():
    dataset = datasets.load_dataset("BAAI/TACO", trust_remote_code=True)
    #train = dataset["train"]
    train = dataset["test"]
    # len = 4695
    datastructures = [x for x in train if "Data structures" in x["skill_types"]]
    # len = 1886
    search = [x for x in train if "Complete search" in x["skill_types"]]
    dp = [x for x in train if "Dynamic programming" in x["skill_types"]]

    # 3993
    datastructures = get_solutions(datastructures)
    # 1576
    search = get_solutions(search)
    dp = get_solutions(dp)

    count_defs_(datastructures)
    count_defs_(search)
    count_defs_(dp)

    good_search = filter_solutions_by_def(search)
    good_ds = filter_solutions_by_def(datastructures)
    good_dp = filter_solutions_by_def(dp)

    # good_dp[1], good_dp[8], good_dp[9]
    chess = get_solutions(get_chess(train))
    import ipdb; ipdb.set_trace()

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
