import json
from librarybench.types import ProblemDescriptions

path = "data/codecontests_graph_descriptions.json"

with open(path, "r") as f:
    problems = json.load(f)

problems = [ProblemDescriptions.model_validate(x) for x in problems]
import ipdb; ipdb.set_trace()
