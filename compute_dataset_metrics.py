import os
import glob
import subprocess
import json

path_to_big_repos = "projects_original"

unique_repo_names = set()
repo_to_metrics = {}
avg_locs_per_collection = []

for collection_path in glob.glob(os.path.join(path_to_big_repos, "*")):
    if not os.path.isdir(collection_path):
        continue

    collection_name = os.path.basename(collection_path.rstrip(os.path.sep))

    num_personas = 0
    loc_sum = 0.0

    # walk through each persona sub-folder
    for persona_path in glob.glob(os.path.join(collection_path, "*")):
        if not os.path.isdir(persona_path):
            continue

        # skip empty personas
        py_files = glob.glob(os.path.join(persona_path, "**", "*.py"), recursive=True)
        if not py_files:
            continue

        # ensure metrics exist
        metrics_file = os.path.join(persona_path, "LIBRARYBENCH_metrics_nolp.json")
        if not os.path.exists(metrics_file):
            result = subprocess.run(
                ["python", "score.py", "--directory", persona_path],
                # capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print(f"[ERROR] score.py failed for {persona_path}:\n{result.stderr}")
                continue
            

        # load the librarybench metrics
        try:
            with open(metrics_file) as f:
                metrics = json.load(f)
        except Exception as e:
            print(f"[ERROR] could not read {metrics_file}: {e}")
            continue

        total_loc = metrics.get("total_loc")
        if total_loc is None:
            print(f"[ERROR] 'total_loc' missing in {metrics_file}")
            continue

        # accumulate for this collection
        num_personas += 1
        loc_sum += total_loc
        repo_to_metrics[persona_path] = {
            "total_loc": total_loc,
        }

        # ensure pytest report exists
        report_file = os.path.join(persona_path, "pytest_results.json")
        if not os.path.exists(report_file): 
            print(f"[ERROR] no pytest in {persona_path}")
            continue

        # load pytest report
        try:
            with open(report_file) as f:
                report = json.load(f)
        except Exception as e:
            print(f"[ERROR] could not read {report_file}: {e}")
            continue

        num_tests = len(report.get("tests", []))
        repo_to_metrics[persona_path]["No. Tests"] = num_tests

    # after iterating personas, record this collection’s avg LOC
    if num_personas > 0:
        avg_locs_per_collection.append(loc_sum / num_personas)
        unique_repo_names.add(collection_name)

    else:
        print(f"Skipping collection {collection_name} (no valid personas)")

# final summary
print(f"NUM COLLECTIONS: {len(unique_repo_names)}")
print(f"NUM PROGRAMS (personas): {len(repo_to_metrics)}")

if avg_locs_per_collection:
    overall_avg_loc = sum(avg_locs_per_collection) / len(avg_locs_per_collection)
    print(f"AVG LOC per collection: {overall_avg_loc:.2f}")
else:
    print("No LOC data to average.")

if repo_to_metrics:
    divisor = 0
    overall_avg_tests = 0
    for m in repo_to_metrics.values():
        if "No. Tests" in m: 
            overall_avg_tests += m["No. Tests"]
            divisor += 1
    overall_avg_tests = overall_avg_tests / divisor
    print(f"AVG TESTS per program: {overall_avg_tests:.2f}")
else:
    print("No test data to average.")


# print("\n".join(repo_to_metrics.keys()))
# for key, metrics in repo_to_metrics.items():
#     print(f"---{key}---")
#     for metric, vlue in metrics.items():
#         print(f"\t{metric}:{vlue}")