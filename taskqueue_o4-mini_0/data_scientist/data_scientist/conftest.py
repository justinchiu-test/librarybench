import sys, os
# Ensure that the data_scientist directory itself is on sys.path
# so that `ml_pipeline` and `cli` can be imported directly.
sys.path.insert(0, os.path.dirname(__file__))
