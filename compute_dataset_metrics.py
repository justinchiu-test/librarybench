import os
import glob
import re
import subprocess
import json

path_to_small_repos = "small_repos"

unique_repo_names = set()
repo_to_metrics = {}
avg_loc = []

for small_repo in glob.glob(os.path.join(path_to_small_repos, "*")):
    if not os.path.isdir(small_repo): continue
    if "refactor" in small_repo: continue

    small_repo_name = os.path.basename(small_repo.rstrip(os.path.sep))
    repo_name = re.match(r'(.+)_o4-mini', small_repo_name).group(1)
    unique_repo_names.add(repo_name)

    metrics_file = os.path.join(small_repo, "LIBRARYBENCH_metrics.json")
    if not os.path.exists(metrics_file): 
        subprocess.run(
            ["python", "score.py", "--directory", small_repo, "--enable_logprobs"]
        )
    librarybench_metrics = json.load(open(metrics_file))

    num_personas = 0
    for persona in glob.glob(os.path.join(small_repo, "*")):
        if not os.path.isdir(persona): continue
        test_report_path = os.path.join(persona, "report.json")
        if not os.path.exists(test_report_path): 
            subprocess.run(
                ["pytest", ".", "--json-report", "--json-report-file=report.json", "--continue-on-collection-errors"],
                cwd=persona
            )
        pytest_report = json.load(open(test_report_path))
        no_tests = len(pytest_report['tests'])

        repo_to_metrics[persona] = {
            "No. Tests": no_tests
        }
        num_personas += 1
    avg_loc.append(librarybench_metrics["total_loc"] / num_personas)

print(f"NUM PROGRAMS: {len(repo_to_metrics)}")
print(f"NUM COLLECTIONS: {len(unique_repo_names)}")
print(f"AVG LOC: {sum(avg_loc) / len(avg_loc)}")
print(f"AVG TESTS: {sum(repo_metrics['No. Tests'] for repo_metrics in repo_to_metrics.values()) / len(repo_to_metrics)}")