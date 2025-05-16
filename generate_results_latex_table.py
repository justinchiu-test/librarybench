# Walks through projects_original/*, finds all subdirs that have a refactor implementation, collects their LIBRRYBENCH_metrics.json, and generates the latex table.

import os, glob, re, json, subprocess


for collection in glob.glob(os.path.join("projects_original", "*")):
    if not os.path.isdir(collection): continue
    foldername = os.path.basename(collection.rstrip(os.path.sep))
    for persona in glob.glob(os.path.join(collection, "*")):
        if not os.path.isdir(persona): continue


table = r"""
\begin{table}[]
\begin{tabular}{@{}llcccc@{}}
\toprule
\multicolumn{1}{c}{\textbf{Collection}} &  & \multicolumn{1}{c}{\textbf{LLoC}} & \multicolumn{1}{c}{\textbf{CC}} & \multicolumn{1}{c}{\textbf{MDL ratio}} & \textbf{Pass rate} \\ 
\midrule
"""

data_to_display = {} # collection name -> persona -> metrics
for collection in glob.glob(os.path.join("projects_original", "*")):
    if not os.path.isdir(collection): continue
    collection_name = os.path.basename(collection.rstrip(os.path.sep))
    if collection_name not in data_to_display: 
        data_to_display[collection_name] = {}
    for persona in glob.glob(os.path.join(collection, "*")):
        if not os.path.isdir(persona): continue

        # skip empty personas
        py_files = glob.glob(os.path.join(persona, "**", "*.py"), recursive=True)
        if not py_files:
            continue

        # Run tests for the original project
        if not os.path.exists(os.path.join(persona, "report.json")):
            try:
                original_dir = os.getcwd()
                os.chdir(persona)
                subprocess.run(["uv", "venv"], check=True)
                subprocess.run(["source .venv/bin/activate && uv pip install -e . && uv pip install pytest pytest-cov pytest-json-report && pytest --json-report --json-report-file=report.json --continue-on-collection-errors"], check=True, shell=True)
                subprocess.run(["deactivate"], check=True)
                os.chdir(original_dir)
            except subprocess.CalledProcessError as e:
                print(f"Error running tests for {persona}: {e}")
                os.chdir(original_dir)

        persona_name = re.search(collection_name + r'_(.+)', os.path.basename(persona)).group(1)
        data_to_display[collection_name]["ORIGINAL"] = {}
        
        lb_metrics_file = os.path.join(persona, "LIBRARYBENCH_metrics.json")
        if not os.path.exists(lb_metrics_file):
            try:
                persona_path = persona
                subprocess.run(["python", "score.py", "--directory", persona_path, "--enable_logprobs"], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error generating metrics for {persona_path}: {e}")
        lb_metrics = json.load(open(lb_metrics_file))
        
        for metric_name in ["logprobs", "lloc", "cyclomatic"]:
            data_to_display[collection_name]["ORIGINAL"][metric_name] = data_to_display[collection_name]["ORIGINAL"].get(metric_name, 0) + lb_metrics[f"total_{metric_name}"]

refactored_to_display = {}
for collection in glob.glob(os.path.join("projects", "*")):
    if not os.path.isdir(collection): continue
    collection_name = os.path.basename(collection.rstrip(os.path.sep))
    if not os.path.exists(os.path.join(collection, "unified")): continue
    if collection_name not in data_to_display: 
        data_to_display[collection_name] = {}
    # Run tests for the refactored project
    if not os.path.exists(os.path.join(collection, "unified", "report.json")):
        try:
            original_dir = os.getcwd()
            unified_path = os.path.join(collection, "unified")
            os.chdir(unified_path)
            subprocess.run(["uv", "venv"], check=True)
            subprocess.run(["source .venv/bin/activate && uv pip install -e . && uv pip install pytest pytest-cov pytest-json-report && pytest --json-report --json-report-file=report.json --continue-on-collection-errors"], check=True, shell=True)
            subprocess.run(["deactivate"], check=True)
            os.chdir(original_dir)
        except subprocess.CalledProcessError as e:
            print(f"Error running tests for {unified_path}: {e}")
            os.chdir(original_dir)

    data_to_display[collection_name]["REFACTORED"] = {}
    
    lb_metrics_file = os.path.join(collection, "unified", "LIBRARYBENCH_metrics.json")
    if not os.path.exists(lb_metrics_file):
        try:
            unified_dir = f"{collection}/unified"
            subprocess.run(["python", "score.py", "--directory", unified_dir, "--enable_logprobs"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error generating metrics for {unified_dir}: {e}")
    lb_metrics = json.load(open(lb_metrics_file))
    
    for metric_name in ["logprobs", "lloc", "cyclomatic"]:
        data_to_display[collection_name]["REFACTORED"][metric_name] = data_to_display[collection_name]["REFACTORED"].get(metric_name, 0) + lb_metrics[f"total_{metric_name}"]


datarow_format = r"""\multirow{3}{*}{REPONAME} & original & ORIGINAL_LLOC  & ORIGINAL_CYCLOMATIC & ORIGINAL_LOGPROBS & 1.0 \\
 & refactored & REFACTORED_LLOC  & REFACTORED_CYCLOMATIC & REFACTORED_LOGPROBS & REFACTORED_PR \\
"""

datarows = []
for collection_name, collection_info in data_to_display.items():
    if len(collection_info) < 2: continue
    # first collect librarybench metrics
    datarow = datarow_format.replace("REPONAME", collection_name.replace("_", "\_"))
    for label, metrics in collection_info.items():
        for metric_name, metric_value in metrics.items():
            if "logprob" in metric_name:
                datarow = datarow.replace(f"{label}_{metric_name.upper()}", f"{metric_value/data_to_display[collection_name]["ORIGINAL"][metric_name]:.1f}")
            else:
                datarow = datarow.replace(f"{label}_{metric_name.upper()}", str(metric_value))
    
        # then collect pass rate
        if label == "ORIGINAL": 
            tests_passed, total_tests = 0, 0
            for persona in glob.glob(os.path.join("projects_original", collection_name, f"{collection_name}_*")):
                pytest_report_path = os.path.join(persona, "report.json")
                if not os.path.exists(pytest_report_path): continue
                pytest_report = json.load(open(pytest_report_path))
                if "passed" in pytest_report['summary']: 
                    tests_passed += pytest_report['summary']['passed']
                if "tests" in pytest_report: 
                    total_tests += len(pytest_report['tests'])
        else:
            pytest_report_path = os.path.join("projects", collection_name, "unified", "report.json")

            pytest_report = json.load(open(pytest_report_path))
            total_tests = len(pytest_report['tests']) if 'tests' in pytest_report else 0
            tests_passed = pytest_report['summary']['passed'] if 'passed' in pytest_report['summary'] else 0
        if not total_tests: 
            datarow = datarow.replace(f"{label}_PR", "failed")
        else:
            datarow = datarow.replace(f"{label}_PR", f"{tests_passed/total_tests:.1f}")

    datarows.append(datarow)

table += r"\midrule".join(datarows)
table += r"""
 \bottomrule
\end{tabular}
\caption{}
\label{tab:big_repo_results}
\end{table}
"""

table = table.replace('clitools', 'cli\_tools')
print(table)