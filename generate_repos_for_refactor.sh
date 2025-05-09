#!/usr/bin/env bash
set -euo pipefail

MODEL="o4-mini"
LIBRARY_GEN_COUNT=2
PERSONA_GEN_COUNT=3

# 1. Snapshot existing top-level dirs
pre_dirs=()
for d in */; do
  [ -d "$d" ] && pre_dirs+=("${d%/}")
done

# 2. Propose libraries (this should create new repos)
python llm_repo_refactor.py \
  --model "$MODEL" \
  --task propose_libraries \
  --num_new_generations "$LIBRARY_GEN_COUNT"

# 3. Snapshot again & diff to find new dirs
post_dirs=()
for d in */; do
  [ -d "$d" ] && post_dirs+=("${d%/}")
done

new_repos=()
for dir in "${post_dirs[@]}"; do
  skip=false
  for old in "${pre_dirs[@]}"; do
    if [[ "$dir" == "$old" ]]; then
      skip=true
      break
    fi
  done
  if ! $skip; then
    new_repos+=("$dir")
  fi
done

if [ ${#new_repos[@]} -eq 0 ]; then
  echo "❌ No new repositories found after propose_libraries"
  exit 1
fi

# 4. Loop each new repo through the remaining tasks
for repo in "${new_repos[@]}"; do
  echo
  echo "➡️  Processing starter‐repo: $repo"

  # a) make_personas
  python llm_repo_refactor.py \
    --model "$MODEL" \
    --task make_personas \
    --num_new_generations "$PERSONA_GEN_COUNT" \
    --starter-repo-path "$repo"

  # b) implement
  python llm_repo_refactor.py \
    --model "$MODEL" \
    --task implement \
    --starter-repo-path "$repo"

  # c) setup_for_refactor on the implemented output
  new_repo="${repo}_${MODEL}_0"
  python llm_repo_refactor.py \
    --model "$MODEL" \
    --task setup_for_refactor \
    --starter-repo-path "$new_repo"
done

echo
echo "✅ All done!"
