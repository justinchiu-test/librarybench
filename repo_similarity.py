import sys
import os
import glob
import itertools

from multiprocessing import Pool, cpu_count
from functools import partial
import hashlib
import json
import numpy as np
import math


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
    for idx, label in enumerate(labels):
        clusters[label].append(idx)
        # clusters[label].append(directory_paths[idx])
    return clusters, np.array(all_embeddings)

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
        task_clusters[lab].append(idx)
        # task_clusters[lab].append(directory_paths[idx])
    for idx, lab in enumerate(code_labels):
        code_clusters[lab].append(idx)
        # code_clusters[lab].append(directory_paths[idx])

    return (task_clusters, task_dist), (code_clusters, code_dist)

###### CLUSTERING HELPERS #####
def select_best_embedding_cluster(all_repos, embeddings, clusters):
    # compute centroid & avg distance per cluster
    centroids = [
        np.mean([embeddings[i] for i in cluster], axis=0)
        for cluster in clusters
    ]
    avg_dists = [
        sum(math.dist(embeddings[i], centroids[idx]) for i in cluster) / len(cluster)
        for idx, cluster in enumerate(clusters)
    ]
    best_idx = int(np.argmin(avg_dists))
    return best_idx, avg_dists

def select_best_string_cluster(clusters, dist_matrix):
    avg_dists = []
    for cluster in clusters:
        if len(cluster) < 2:
            avg_dists.append(float('inf'))
        else:
            pairs = list(itertools.combinations(cluster, 2))
            avg = sum(dist_matrix[i][j] for i,j in pairs) / len(pairs)
            avg_dists.append(avg)
    best_idx = int(np.argmin(avg_dists))
    return best_idx, avg_dists

if __name__ == "__main__":
    folders_of_repos = sys.argv[1:-1]
    all_repos = []
    for repo_folder in folders_of_repos:
        for subfolder in glob.glob(os.path.join(repo_folder, "*")):
            if os.path.isdir(subfolder) and "__pycache__" not in subfolder:
                all_repos.append(subfolder)

    NUM_CLUSTERS = int(sys.argv[-1])
    print(f"Clustering {' and '.join(all_repos)} into {NUM_CLUSTERS} clusters...")

    embedding_task_clusters, task_embeddings = get_embedding_clusters(all_repos, NUM_CLUSTERS)
    emb_i, emb_dists = select_best_embedding_cluster(all_repos, task_embeddings, embedding_task_clusters)
    print("=== EMBEDDING TASK CLUSTERS ===")
    for idx, cluster in enumerate(embedding_task_clusters):
        print(",".join(all_repos[cluster_i] for cluster_i in cluster) + f"{' (BEST)' if idx == emb_i else ''} {emb_dists[idx]}")

    (string_task_clusters, string_task_dist), (string_code_clusters, string_code_dist) = get_string_clusters(all_repos, NUM_CLUSTERS)

    task_i, task_dists = select_best_string_cluster(string_task_clusters, string_task_dist)
    print("=== STRING TASK CLUSTERS ===")
    for idx, cluster in enumerate(string_task_clusters):
        print(",".join(all_repos[cluster_i] for cluster_i in cluster) + f"{' (BEST)' if idx == task_i else ''} {task_dists[idx]}")

    code_i, code_dists = select_best_string_cluster(string_code_clusters, string_code_dist)
    print("=== STRING CODE CLUSTERS ===")
    for idx, cluster in enumerate(string_code_clusters):
        print(",".join(all_repos[cluster_i] for cluster_i in cluster) + f"{' (BEST)' if idx == code_i else ''} {code_dists[idx]}")


# determine which generated personas to refactor tg: 
# python repo_similarity.py clitools_o4-mini_0 3 > clitools_o4-mini_0/clusters.txt

# can also use to see that generated clusters would indeed cluster:
# python repo_similarity.py clitools_o4-mini_0a micro_scheduler_o4-mini_0ba 2
