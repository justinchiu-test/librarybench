import sys
import os

# pytest runs from the project root, but all of your code/tests live under ./data_scientist/
# so we add that directory to sys.path up front.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'data_scientist'))
