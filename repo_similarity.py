import sys
import os
import glob

from collections import defaultdict
import itertools
from tabulate import tabulate
from thefuzz import fuzz
# for embeddings: oai's embedding-3-small

ONLY_SRC_CODE = True

def load_code(repo_path):
    repo_code = {}
    for src_code_file in glob.glob(os.path.join(repo_path, "**", "*.py"), recursive=True):
        repo_code[os.path.relpath(src_code_file, repo_path)] = open(src_code_file).read()
    return repo_code

def string_similarities(s1, s2):
    return {
        "ratio": fuzz.ratio(s1, s2),
        "partial_ratio": fuzz.partial_ratio(s1, s2),
        "token_sort_ratio": fuzz.token_sort_ratio(s1, s2),
        "token_set_ratio": fuzz.token_set_ratio(s1, s2),
    }

def code_string_similarity(repo1_code, repo2_code):
    repo1_concatenated = "\n".join(repo1_code.values())
    repo2_concatenated = "\n".join(repo2_code.values())
    return string_similarities(repo1_concatenated, repo2_concatenated)

def task_string_similarity(repo1_task, repo2_task):
    return string_similarities(repo1_task, repo2_task)

all_repos = sys.argv[1:]
all_repo_code = {path: load_code(path) for path in all_repos}

# get similarites for all pairs of repos
headers = ["repos", "Metric", "Value"]
for (repo_1_path, repo_1_code), (repo_2_path, repo_2_code) in itertools.combinations(all_repo_code.items(), 2):
    repo1_name = os.path.basename(repo_1_path)
    repo2_name = os.path.basename(repo_2_path)
    data = []
    for metric, value in task_string_similarity(os.path.join(repo_1_path, "TASK.md"), os.path.join(repo_2_path, "TASK.md")).items():
        data.append([f"{repo1_name},{repo2_name}", f"TASK.md:{metric}", value])
    for metric, value in code_string_similarity(repo_1_code, repo_2_code).items():
        data.append([f"{repo1_name},{repo2_name}", f"code:{metric}", value])

print(tabulate(data, headers=headers))

# Now compute per-pair average and sort
total_avg = []
# Group all metric values by repo pair
pair_scores = defaultdict(list)
for pair, metric, value in data:
    pair_scores[pair].append(value)
    total_avg.append(value)

# Compute average for each pair
avg_scores = [(pair, sum(vals) / len(vals)) for pair, vals in pair_scores.items()]

# Sort from most similar (highest avg) to least
avg_scores.sort(key=lambda x: x[1], reverse=True)

# Print out the rankings
print("\nMost similar repo pairs (by average fuzzy‐score):")
print(tabulate(avg_scores, headers=["Repo Pair", "Avg Score"]))


# Print average similarity across all repos
print(f"REPO AVERAGE SIMILARITY: {sum(total_avg)/len(total_avg)}")