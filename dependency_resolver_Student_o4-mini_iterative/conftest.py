import os
import sys

# look for the one and only student‐implementation folder under the repo root
ROOT = os.path.dirname(__file__)
for name in os.listdir(ROOT):
    candidate = os.path.join(ROOT, name)
    if os.path.isdir(candidate) and os.path.isdir(os.path.join(candidate, "env_manager")):
        # insert it first so "import env_manager" will find your code
        sys.path.insert(0, candidate)
        break
