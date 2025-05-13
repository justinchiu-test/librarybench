#!/bin/bash

# Iterate over all matching directories
for repo in *o4-mini_0; do
    if [ -d "$repo" ]; then
        echo "Scoring repository: $repo"
        python score.py --enable_logprobs --directory "$repo"
    else
        echo "Skipping $repo: not a directory"
    fi
done


for repo in *o4-mini_0_refactor*; do
    if [ -d "$repo" ]; then
        echo "Scoring repository: $repo"
        python score.py --enable_logprobs --directory "$repo/unified"
    else
        echo "Skipping $repo: not a directory"
    fi
done
