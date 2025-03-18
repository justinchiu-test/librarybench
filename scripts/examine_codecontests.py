import datasets
import json
from collections import defaultdict
import numpy as np
import tiktoken
from openai import OpenAI
import tqdm
from pathlib import Path

client = OpenAI()
tokenizer = tiktoken.encoding_for_model("text-embedding-3-small")


TEMPLATE = """## Problem
{description}

## Solution
```cpp
{code}
```"""

def count_tokens(text):
    return len(tokenizer.encode(text))

def get_solutions(xs, max_solutions=3):
    all_solutions = [[] for _ in range(len(xs))]
    for i, x in enumerate(xs):
        stuff = x["solutions"]
        languages = stuff["language"]
        solutions = stuff["solution"]
        description = x["description"]
        for lang, sol in zip(languages, solutions):
            #if lang == 2 and count_tokens(description) + count_tokens(sol) <= 8192:
            if lang == 2 and count_tokens(sol) <= 8192:
                all_solutions[i].append(sol)
            if len(all_solutions[i]) >= max_solutions: break
    return all_solutions


def main():
    dataset = datasets.load_dataset("deepmind/code_contests", trust_remote_code=True)
    # train = dataset["train"]
    train = dataset["train"]

    skills = sorted(set([skills for ex in train["cf_tags"] for skills in ex]))
    skill = "graphs"

    idxs_with_tags = [(i,x) for i, x in enumerate(train["cf_tags"]) if x]
    problems = [train[i] for i,x in idxs_with_tags if skill in x]

    examples = get_solutions(problems)
    # concatenate prompt and solution
    texts = []
    fulltexts = []
    for i, solutions in enumerate(examples):
        problem = problems[i]
        for solution in solutions:
            text = solution
            texts.append(text)
            fulltext = TEMPLATE.format(description=problem["description"], code=solution)
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
            chunk = texts[i:i+batch_size]
            response = client.embeddings.create(input=chunk, model='text-embedding-3-small')
            chunk_embeddings = [item.embedding for item in response.data]
            embeddings.extend(chunk_embeddings)
        embeddings = np.array(embeddings)
        np.save(embeddings_path, embeddings)
        print(f"Embeddings saved to {embeddings_path}")

    # find inverse index from flattent list to problems to avoid same-problem nearest neighbours.
    lengths = np.array([len(lst) for lst in examples])
    inverse_mapping = np.repeat(np.arange(len(examples)), lengths)

    # find nearest neighbours
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    normed = embeddings / norms
    similarity_matrix = normed @ normed.T
    rankings = (-similarity_matrix).argsort()
    similarities = np.take_along_axis(similarity_matrix, rankings[:,:6], axis=1)

    # save full texts for refactoring
    selected = rankings[0,:6]
    selected_fulltexts = [fulltexts[x] for x in selected]
    problems_path = Path("data/saved_graph_problems.md")
    with problems_path.open("w") as f:
        f.write("\n\n".join([f"# Example {i}\n\n{x}" for i, x in enumerate(selected_fulltexts)]))
    print(f"saved selected problems to {problems_path}")


if __name__ == "__main__":
    main()
