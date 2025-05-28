import os
import subprocess
import csv
import re
from pathlib import Path

# Constants
GITHUB_USERNAME = "justinchiu"
ORG_NAME = "code-refactor"
BASE_DIR = "projects"
OUTPUT_CSV = "repo_links_large.csv"
# Get token securely
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]

repo_links = []

for path in Path(BASE_DIR).glob("*/*"):
    library = path.parts[1]
    library_persona = path.stem
    persona = library_persona.removeprefix(library + "_")

    has_python_files = any(path.rglob("*.py"))
    if not has_python_files:
        continue

    new_repo_name = library_persona
    remote_url = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{ORG_NAME}/{new_repo_name}.git"
    public_url = f"https://github.com/{ORG_NAME}/{new_repo_name}"

    print(f"\n=== Setting up {new_repo_name} ===")

    # Git setup
    subprocess.run(["gh", "repo", "create", f"{ORG_NAME}/{new_repo_name}", "--public"], cwd=path)

    subprocess.run(["git", "init"], cwd=path)

    # Create .gitignore to skip unwanted files
    gitignore_path = os.path.join(path, ".gitignore")
    with open(gitignore_path, "w") as f:
        f.write("__pycache__/\n")
        f.write(".pytest_cache/\n")
        f.write("report.json\n")
        f.write("LIBRARYBENCH_metrics.json\n")
        f.write("test_output.txt\n")


    subprocess.run(["git", "add", "."], cwd=path)
    subprocess.run(["git", "commit", "-m", "initial commit"], cwd=path)

    # Add remote and push
    subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=path)
    subprocess.run(["git", "branch", "-M", "main"], cwd=path)
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=path)

    # Record
    repo_links.append((library, persona, public_url))

# Save to CSV
with open(OUTPUT_CSV, "w") as f:
    writer = csv.writer(f)
    writer.writerow(["library_name", "persona_name", "github_link"])
    writer.writerows(repo_links)

print(f"\n✅ Finished. CSV written to {OUTPUT_CSV}")

from datasets import Dataset
from huggingface_hub import HfApi, HfFolder
import pandas as pd

# === CONFIGURATION ===
HF_DATASET_REPO = "celinelee/minicode-repos" 
CSV_PATH = "repo_links_large.csv"
HF_TOKEN = os.environ["HF_TOKEN"]  # safer than hardcoding

# Optional: login to huggingface (if needed in script)
HfFolder.save_token(HF_TOKEN)

# === LOAD AND CONVERT CSV ===
df = pd.read_csv(CSV_PATH)
hf_dataset = Dataset.from_pandas(df)

# === PUSH TO HUB ===
hf_dataset.push_to_hub(HF_DATASET_REPO)
print(f"✅ Dataset pushed to https://huggingface.co/datasets/{HF_DATASET_REPO}")
