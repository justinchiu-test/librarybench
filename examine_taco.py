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
    import pdb; pdb.set_trace()


if __name__ == "__main__":
    main()
