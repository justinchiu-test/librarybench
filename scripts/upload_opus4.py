import os
import subprocess
import csv
import re
from pathlib import Path

# Constants
GITHUB_USERNAME = "justinchiu-cohere"
ORG_NAME = "code-refactor"
BASE_DIR = "projects"
OUTPUT_CSV = "repo_links_opus4.csv"
# Get token securely
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]

repo_links = []

# Claude 4 Opus projects from README
claude4opus_projects = [
    "archive_file_manager_film",
    "archive_file_manager_legal",
    "binary_file_format_parser_audio_researcher",
    "binary_file_format_parser_automotive_engineer",
    "code_dependency_analyzer_legacy-modernizer",
    "code_dependency_analyzer_performance-engineer",
    "code_pattern_detector_performance_engineer",
    "code_pattern_detector_security_auditor",
    "data_migration_framework_compliance_auditor",
    "data_migration_framework_startup_cto",
    "http_api_mock_server_blockchain",
    "http_api_mock_server_microservices",
    "memory_profiler_tool_embedded_engineer",
    "memory_profiler_tool_game_developer",
    "process_resource_monitor_hft_developer",
    "process_resource_monitor_k8s_engineer",
    "template_rendering_engine_email_marketing",
    "template_rendering_engine_report_generator",
    "terminal_game_engine_ascii_art",
    "terminal_game_engine_multiplayer"
]

for path in Path(BASE_DIR).glob("*/*"):
    library = path.parts[1]
    library_persona = path.stem
    persona = library_persona.removeprefix(library + "_")

    # Only process if this is a claude4opus project
    if library_persona not in claude4opus_projects:
        continue

    has_python_files = any(path.rglob("*.py"))
    if not has_python_files:
        continue

    new_repo_name = library_persona
    remote_url = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{ORG_NAME}/{new_repo_name}.git"
    public_url = f"https://github.com/{ORG_NAME}/{new_repo_name}"

    print(f"\n=== Setting up {new_repo_name} ===")

    # Check if repo already exists
    check_result = subprocess.run(
        ["gh", "repo", "view", f"{ORG_NAME}/{new_repo_name}", "--json", "name"],
        capture_output=True,
        text=True
    )
    
    if check_result.returncode == 0:
        print(f"Repository {ORG_NAME}/{new_repo_name} already exists. Skipping...")
    else:
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
CSV_PATH = OUTPUT_CSV
HF_TOKEN = os.environ["HF_TOKEN"]  # safer than hardcoding

# Optional: login to huggingface (if needed in script)
HfFolder.save_token(HF_TOKEN)

# === LOAD AND CONVERT CSV ===
df = pd.read_csv(CSV_PATH)

# Create claude4opus split
df_claude4opus = df[df['library_name'].str.cat(df['persona_name'], sep='_').isin(claude4opus_projects)]

# Load existing dataset to get current splits
from datasets import load_dataset, DatasetDict

try:
    # Load existing dataset
    existing_dataset = load_dataset(HF_DATASET_REPO, token=HF_TOKEN)
    
    # Only add claude4opus split if there are matching projects
    if len(df_claude4opus) > 0:
        # Create new dataset dict with existing splits plus claude4opus
        dataset_dict = DatasetDict({
            **existing_dataset,  # Keep all existing splits
            "claude4opus": Dataset.from_pandas(df_claude4opus)  # Add new split
        })
    else:
        print("No claude4opus projects found in CSV, keeping existing splits only")
        dataset_dict = existing_dataset
except Exception as e:
    raise e
    print(f"Could not load existing dataset, creating new one: {e}")
    # If can't load existing, create with just the new splits
    if len(df_claude4opus) > 0:
        dataset_dict = DatasetDict({
            "train": Dataset.from_pandas(df),
            "claude4opus": Dataset.from_pandas(df_claude4opus)
        })
    else:
        print("No claude4opus projects found in CSV, creating train split only")
        dataset_dict = DatasetDict({
            "train": Dataset.from_pandas(df)
        })

# === PUSH TO HUB ===
dataset_dict.push_to_hub(HF_DATASET_REPO, token=HF_TOKEN, create_pr=True)
print(f"✅ Dataset with splits pushed to https://huggingface.co/datasets/{HF_DATASET_REPO}")
