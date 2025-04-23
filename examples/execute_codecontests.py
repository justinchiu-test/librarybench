import bm25s
import datasets
import json
from collections import defaultdict
import numpy as np
import tiktoken
from openai import OpenAI
import tqdm
from pathlib import Path

from librarybench.execution import run_unit_tests
from librarybench.types import Problem, ProblemDescriptions, StdinStdout, SolutionResult


client = OpenAI()
tokenizer = tiktoken.encoding_for_model("text-embedding-3-small")


TEMPLATE = """## Problem
{question}

## Solution
```cpp
{code}
```"""


def count_tokens(text):
    return len(tokenizer.encode(text))


def get_problems(xs, max_solutions=3):
    problems = []
    for i, x in enumerate(xs):
        stuff = x["solutions"]
        languages = stuff["language"]
        solutions = stuff["solution"]
        description = x["description"]
        selected_solutions = []
        for lang, sol in zip(languages, solutions):
            # if lang == 2 and count_tokens(description) + count_tokens(sol) <= 8192:
            if lang == 2 and count_tokens(sol) <= 8192:
                selected_solutions.append(sol)
            if len(selected_solutions) >= max_solutions:
                break
        problems.append(
            Problem(
                problem_id=i,
                question=x["description"],
                tests=[
                    StdinStdout(stdin=stdin, stdout=stdout)
                    for stdin, stdout in zip(
                        x["public_tests"]["input"] + x["private_tests"]["input"] + x["generated_tests"]["input"],
                        x["public_tests"]["output"] + x["private_tests"]["output"] + x["generated_tests"]["output"],
                    )
                ],
                source="codeforces",
                difficulty=x["cf_rating"],
                human_solutions=selected_solutions,
                original_code=None,
                language="cpp",
            )
        )
    return problems


def main():
    dataset = datasets.load_dataset("deepmind/code_contests", trust_remote_code=True)
    # train = dataset["train"]
    train = dataset["train"]

    skills = sorted(set([skills for ex in train["cf_tags"] for skills in ex]))
    skill = "graphs"

    idxs_with_tags = [(i, x) for i, x in enumerate(train["cf_tags"]) if x]
    problems = [train[i] for i, x in idxs_with_tags if skill in x]

    examples = get_problems(problems)
    # concatenate prompt and solution
    texts = []
    fulltexts = []
    problems_with_descriptions = []
    for i, problem in enumerate(examples):
        outputs = run_unit_tests("cpp", problem.human_solutions, problem.tests)
        test_results = np.array([[x["passed"] for x in test_results] for test_results in outputs])
        import pdb; pdb.set_trace()


if __name__ == "__main__":
    main()
