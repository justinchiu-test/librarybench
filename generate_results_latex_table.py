# Walks through small_repos/*, finds all subdirs that have a refactor implementation, collects their LIBRRYBENCH_metrics.json, and generates the latex table.

import os, glob, re, json

# table = r"""
# \begin{table}[]
# \begin{tabular}{@{}llcccccc@{}}
# \toprule
# \multicolumn{1}{c}{\textbf{Collection}} & \multicolumn{1}{c}{\textbf{Agent}} & \multicolumn{1}{c}{\textbf{LoC}} & \multicolumn{1}{c}{\textbf{SLoC}} & \multicolumn{1}{c}{\textbf{LLoC}} & \multicolumn{1}{c}{\textbf{Cyclocomplexity}} & \multicolumn{1}{c}{\textbf{logprobs}} & \multicolumn{1}{c}{\textbf{Token count}} \\ 
# \midrule
# """



table = r"""
\begin{table}[]
\begin{tabular}{@{}llcccc@{}}
\toprule
\multicolumn{1}{c}{\textbf{Collection}} & \multicolumn{1}{c}{\textbf{Agent}} & \multicolumn{1}{c}{\textbf{LLoC}} & \multicolumn{1}{c}{\textbf{CC}} & \multicolumn{1}{c}{\textbf{MDL ratio}} & \textbf{Pass rate} \\ 
\midrule
"""

data_to_display = {} # collection name -> agent name or original -> metrics
for collection in glob.glob(os.path.join("small_repos", "*")):
    if not os.path.isdir(collection): continue
    foldername = os.path.basename(collection.rstrip(os.path.sep))
    collection_name = re.search(r'(.+)_o4-mini_0([abcd])', os.path.basename(foldername))
    collection_name = (collection_name.group(1), collection_name.group(2))
    if collection_name not in data_to_display: 
        data_to_display[collection_name] = {}
    agent_name = re.search(r'_o4-mini_0[abcd](.*)', foldername).group(1)
    if agent_name == "": agent_name = "original"
    agent_name = agent_name.replace("_", "").replace("refactor", "").upper()
    if agent_name in data_to_display[collection_name]: continue # why would this happen?
    data_to_display[collection_name][agent_name] = {}
    
    if "refactor" in collection:
        lb_metrics = json.load(open(os.path.join(collection, "unified", "LIBRARYBENCH_metrics.json")))
    else:
        lb_metrics = json.load(open(os.path.join(collection, "LIBRARYBENCH_metrics.json")))
    
    for metric_name in ["logprobs", "lloc", "cyclomatic"]:
        data_to_display[collection_name][agent_name][metric_name] = lb_metrics[f"total_{metric_name}"]


datarow_format = r"""\multirow{3}{*}{REPONAME} & original & ORIGINAL_LLOC  & ORIGINAL_CYCLOMATIC & ORIGINAL_LOGPROBS & 1.0 \\
 & Cl-Cl & CLCL_LLOC  & CLCL_CYCLOMATIC & CLCL_LOGPROBS & CLCL_PR \\
 & Cl-Cx & CLCX_LLOC  & CLCX_CYCLOMATIC & CLCX_LOGPROBS & CLCX_PR \\
"""

datarows = []
for collection_name, collection_info in data_to_display.items():
    if len(collection_info) < 2: continue
    # first collect librarybench metrics
    datarow = datarow_format.replace("REPONAME", collection_name[0].replace("_", "\_"))
    for agent_name, metrics in collection_info.items():
        for metric_name, metric_value in metrics.items():
            if "logprob" in metric_name:
                datarow = datarow.replace(f"{agent_name}_{metric_name.upper()}", f"{metric_value/data_to_display[collection_name]["ORIGINAL"][metric_name]:.1f}")
            else:
                datarow = datarow.replace(f"{agent_name}_{metric_name.upper()}", str(metric_value))
    
        # then collect pass rate
        if agent_name == "ORIGINAL": 
            pytest_report_path = os.path.join(f"{collection_name[0]}_o4-mini_0{collection_name[1]}]", "report.json")
        else:
            if "CX" in agent_name: agent_extension = "_cl_cx"
            else: agent_extension = "_cl_cl"
            pytest_report_path = os.path.join("small_repos", f"{collection_name[0]}_o4-mini_0{collection_name[1]}_refactor{agent_extension}", "unified", "report.json")

            pytest_report = json.load(open(pytest_report_path))
            total_tests = len(pytest_report['tests'])
            if total_tests:
                datarow = datarow.replace(f"{agent_name}_PR", f"{pytest_report['summary']['passed']/total_tests:.1f}")
            else:
                datarow = datarow.replace(f"{agent_name}_PR", "failed")

    datarows.append(datarow)

table += r"\midrule".join(datarows)
table += r"""
 \bottomrule
\end{tabular}
\caption{}
\label{tab:small_repo_results}
\end{table}
"""

table = table.replace('clitools', 'cli\_tools')
print(table)