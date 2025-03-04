import os
import requests

url = os.getenv("CYBER_URL")

generations = ["def f(): return 1", "def f(): return 2"]
tests = ["assert f() == 1", "assert f() == 2"]


def run_unit_tests(
    generations: list[str], tests: list[str]
) -> list[list[dict[str, str]]]:
    num_tests_per_generation = []
    outputs = []
    for generation in generations:
        num_tests_per_generation.append(len(tests))
        for test in tests:
            code_dict = {
                "code": generation,
                "test": test,
            }
            params = {
                "language": "python",
                "environment": "default",
                "timeout": 30,  # feel free to change this
                "generation_formatting": "true",
                "fill_missing_imports": "true",
            }
            response = requests.post(url, json=code_dict, params=params)
            outputs.append(response.json())
    # unflatten
    idx = 0
    generation_tests = []
    for num_tests in num_tests_per_generation:
        generation_tests.append([outputs[idx + i] for i in range(num_tests)])
        idx += num_tests
    return generation_tests


results = run_unit_tests(generations, tests)
import pdb

pdb.set_trace()

"""
(Pdb) response.json().keys()
dict_keys(['code', 'test', 'passed', 'exec_output', 'uncaught_exception'])
(Pdb) response.json()["test"]
'assert f() == 1\n'
(Pdb) response.json()["passed"]
True
(Pdb) response.json()["exec_output"]
{'run_output': {'stdout': '', 'stderr': '', 'exit_code': 0, 'timeout_expired': False, 'elapsed_time': 0.27522417900001983}, 'compile_output': None}
(Pdb) response.json()["uncaught_exception"]
'None'
"""
