import sys
import os
import glob
import itertools

from multiprocessing import Pool, cpu_count
from functools import partial
import hashlib
import json
import numpy as np


def load_code(repo_path):
    repo_code = {}
    for src_code_file in glob.glob(os.path.join(repo_path, "**", "*.py"), recursive=True):
        with open(src_code_file, 'r', encoding='utf-8', errors='ignore') as f:
            repo_code[os.path.relpath(src_code_file, repo_path)] = f.read()
    return repo_code

### STRING SIM COMPUTING CODE ####
from thefuzz import fuzz

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

def task_string_similarity(task1, task2):
    return string_similarities(task1, task2)

def compute_pairwise_similarity(pair, task_strings, all_repo_code):
    i, j = pair
    # compute average fuzzy similarity on tasks
    t_sim = task_string_similarity(task_strings[i], task_strings[j])
    task_avg = sum(t_sim.values()) / len(t_sim)
    # compute average fuzzy similarity on code
    c_sim = code_string_similarity(all_repo_code[i][1], all_repo_code[j][1])
    code_avg = sum(c_sim.values()) / len(c_sim)
    return i, j, task_avg, code_avg

def compute_string_matrices_parallel(directory_paths, processes=None):
    # read all TASK.md strings and code once
    task_strings = []
    for path in directory_paths:
        with open(os.path.join(path, "TASK.md"), 'r', encoding='utf-8') as f:
            task_strings.append(f.read())
    all_repo_code = [(p, load_code(p)) for p in directory_paths]

    n = len(directory_paths)
    task_sim = np.zeros((n, n))
    code_sim = np.zeros((n, n))

    pairs = list(itertools.combinations(range(n), 2))
    procs = min(processes or cpu_count(), cpu_count())

    with Pool(processes=procs) as pool:
        func = partial(compute_pairwise_similarity,
                       task_strings=task_strings,
                       all_repo_code=all_repo_code)
        for i, j, task_avg, code_avg in pool.map(func, pairs):
            task_sim[i][j] = task_sim[j][i] = task_avg
            code_sim[i][j] = code_sim[j][i] = code_avg

    return task_sim, code_sim

### EMBEDDING COMPUTING CODE ####

from openai import OpenAI

def sha256_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def load_or_compute_embedding(task_path, model_name="text-embedding-ada-002", cache_dir=".embedding_cache", client=None):
    # instantiate client locally to avoid pickling issues
    client = OpenAI()

    os.makedirs(cache_dir, exist_ok=True)
    with open(task_path, "r", encoding="utf-8") as f:
        task_str = f.read()

    cache_key = sha256_hash(task_str)
    cache_path = os.path.join(cache_dir, f"{cache_key}.json")

    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)

    response = client.embeddings.create(input=task_str, model=model_name)
    embedding = response.data[0].embedding

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(embedding, f)

    return embedding


def compute_embeddings_parallel(repo_paths, model_name, cache_dir=".embedding_cache"):
    task_paths = [os.path.join(path, "TASK.md") for path in repo_paths]
    with Pool(processes=min(cpu_count(), 8)) as pool:
        # note: we no longer pass `client`, only simple args
        func = partial(load_or_compute_embedding, model_name=model_name, cache_dir=cache_dir)
        embeddings = pool.map(func, task_paths)
    return embeddings


#### CLUSTERING CODE ####
from sklearn.cluster import AgglomerativeClustering

def agglomerative_clustering(embeddings, embedding_clusterer):
    X = np.array(embeddings)
    print("shape of X", X.shape)
    clustering = embedding_clusterer.fit_predict(X)
    return clustering

def get_embedding_clusters(directory_paths, num_clusters):
    embedding_clusterer = AgglomerativeClustering(n_clusters=num_clusters)

    print("Computing embeddings in parallel with caching...")
    all_embeddings = compute_embeddings_parallel(
        directory_paths,
        model_name="text-embedding-ada-002",
        cache_dir=".embedding_cache"
    )

    labels = embedding_clusterer.fit_predict(all_embeddings)
    clusters = [[] for _ in range(num_clusters)]
    for idx, lab in enumerate(labels):
        clusters[lab].append(directory_paths[idx])
    return clusters

def get_string_clusters(directory_paths, num_clusters, processes=None):
    # compute similarity matrices in parallel
    task_sim, code_sim = compute_string_matrices_parallel(directory_paths, processes)

    # convert similarity to distance
    task_dist = 100 - task_sim
    code_dist = 100 - code_sim

    # cluster with precomputed distances
    clusterer = AgglomerativeClustering(
        n_clusters=num_clusters,
        metric='precomputed',
        linkage='average'
    )
    task_labels = clusterer.fit_predict(task_dist)
    code_labels = clusterer.fit_predict(code_dist)

    task_clusters = [[] for _ in range(num_clusters)]
    code_clusters = [[] for _ in range(num_clusters)]
    for idx, lab in enumerate(task_labels):
        task_clusters[lab].append(directory_paths[idx])
    for idx, lab in enumerate(code_labels):
        code_clusters[lab].append(directory_paths[idx])

    return task_clusters, code_clusters

if __name__ == "__main__":
    all_repos = sys.argv[1:-1]
    NUM_CLUSTERS = int(sys.argv[-1])

    embedding_task_clusters = get_embedding_clusters(all_repos, NUM_CLUSTERS)

    print("=== EMBEDDING TASK CLUSTERS ===")
    for cluster in embedding_task_clusters:
        print(",".join(p for p in cluster))

    string_task_clusters, string_code_clusters = get_string_clusters(all_repos, NUM_CLUSTERS)

    print("=== STRING TASK CLUSTERS ===")
    for cluster in string_task_clusters:
        print(",".join(p for p in cluster))

    print("=== STRING CODE CLUSTERS ===")
    for cluster in string_code_clusters:
        print(",".join(p for p in cluster))


# determine which generated personas to refactor tg: 
# python repo_similarity.py clitools_o4-mini_0/backend_dev/ clitools_o4-mini_0/cloud_infra_engineer/ clitools_o4-mini_0/data_scientist/ clitools_o4-mini_0/devops_engineer/ clitools_o4-mini_0/localization_manager/ clitools_o4-mini_0/opensource_maintainer/ clitools_o4-mini_0/ops_engineer/ clitools_o4-mini_0/plugin_developer/ clitools_o4-mini_0/qa_automation/ clitools_o4-mini_0/security_analyst/ clitools_o4-mini_0/translator/  3

# can also use to see that generated clusters would indeed cluster:
# python repo_similarity.py clitools_o4-mini_0/... micro_scheduler_o4-mini_0/...  2
