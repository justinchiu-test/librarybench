import datasets
import json
from collections import defaultdict
import numpy as np
import tiktoken
from openai import OpenAI
import tqdm
from pathlib import Path

from librarybench.types import Problem, StdinStdout, SolutionResult

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
                        x["private_tests"]["input"], x["private_tests"]["output"]
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
    for i, problem in enumerate(examples):
        for solution in problem.human_solutions:
            text = solution
            texts.append(text)
            fulltext = TEMPLATE.format(
                question=problem.question, code=solution
            )
            fulltexts.append(fulltext)

    embeddings_path = Path("embeddings.npy")
    if embeddings_path.exists():
        # load cached embeddings
        print("Loading existing embeddings...")
        embeddings = np.load(embeddings_path)
        print(f"Loaded {len(embeddings)} embeddings from cache.")
    else:
        print("Creating embeddings")
        batch_size = 128
        embeddings = []
        for i in tqdm.tqdm(range(0, len(texts), batch_size), desc="Processing batches"):
            chunk = texts[i : i + batch_size]
            response = client.embeddings.create(
                input=chunk, model="text-embedding-3-small"
            )
            chunk_embeddings = [item.embedding for item in response.data]
            embeddings.extend(chunk_embeddings)
        embeddings = np.array(embeddings)
        np.save(embeddings_path, embeddings)
        print(f"Embeddings saved to {embeddings_path}")

    # find inverse index from flattent list to problems to avoid same-problem nearest neighbours.
    lengths = np.array([len(x.human_solutions) for x in examples])
    inverse_mapping = np.repeat(np.arange(len(examples)), lengths)

    # find nearest neighbours
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    normed = embeddings / norms
    similarity_matrix = normed @ normed.T
    rankings = (-similarity_matrix).argsort()
    similarities = np.take_along_axis(similarity_matrix, rankings[:, :6], axis=1)

    # save full texts for refactoring
    selected = rankings[1, :6]
    selected_fulltexts = [fulltexts[x] for x in selected]
    selected_texts = [texts[x] for x in selected]

    problems_path = Path("data/saved_graph_problems.md")
    with problems_path.open("w") as f:
        f.write(
            "\n\n".join(
                [f"# Example {i}\n\n{x}" for i, x in enumerate(selected_fulltexts)]
            )
        )

    # store the chosen solution in original_code
    problems = [examples[inverse_mapping[i]].model_copy(update=dict(original_code=texts[i])) for i in selected]
    solutions = [SolutionResult(
        problem=problem,
        code=problem.original_code,
        # dummy values
        status="success",
        pass_ratio=1,
        tests_passed=1,
        tests_total=1,
        iterations=1,
        history=[],
        model_name="human",
        model_type="human",
    ).model_dump() for problem in problems]
    solutions_path = Path("data/saved_graph_solutions.json")
    with solutions_path.open("w") as f:
        json.dump(solutions, f)
    print(f"saved selected solutions to {solutions_path}")


if __name__ == "__main__":
    main()
