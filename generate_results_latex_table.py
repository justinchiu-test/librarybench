# Walks through small_repos/*, finds all subdirs that have a refactor implementation, collects their LIBRRYBENCH_metrics.json, and generates the latex table.

import os, glob, re, json

table = r"""
\begin{table}[]
\begin{tabular}{@{}llcccccc@{}}
\toprule
\multicolumn{1}{c}{\textbf{Collection}} & \multicolumn{1}{c}{\textbf{Agent}} & \multicolumn{1}{c}{\textbf{LoC}} & \multicolumn{1}{c}{\textbf{SLoC}} & \multicolumn{1}{c}{\textbf{LLoC}} & \multicolumn{1}{c}{\textbf{Cyclocomplexity}} & \multicolumn{1}{c}{\textbf{logprobs}} & \multicolumn{1}{c}{\textbf{Token count}} \\ 
\midrule
"""

data_to_display = {} # collection name -> agent name or original -> metrics
for collection in glob.glob(os.path.join("small_repos", "*")):
    if not os.path.isdir(collection): continue
    foldername = os.path.basename(collection.rstrip(os.path.sep))
    collection_name = re.search(r'(.+)_o4-mini_0([abcd])', os.path.basename(foldername))
    collection_name = collection_name.group(1) + f" ({collection_name.group(2).upper()})"
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
    
    for metric_name in ["loc", "logprobs", "tokens", "sloc", "lloc", "cyclomatic"]:
        data_to_display[collection_name][agent_name][f"{agent_name}_{metric_name.upper()}"] = lb_metrics[f"total_{metric_name}"]

datarow_format = r"""\multirow{3}{*}{REPONAME} & original & ORIGINAL_LOC  & ORIGINAL_SLOC & ORIGINAL_LLOC  & ORIGINAL_CYCLOMATIC & ORIGINAL_LOGPROBS & ORIGINAL_TOKENS \\
 & Cl-Cl & CLCL_LOC  & CLCL_SLOC & CLCL_LLOC  & CLCL_CYCLOMATIC & CLCL_LOGPROBS & CLCL_TOKENS \\
 & Cl-Cx & CLCX_LOC  & CLCX_SLOC & CLCX_LLOC  & CLCX_CYCLOMATIC & CLCX_LOGPROBS & CLCX_TOKENS \\
"""

datarows = []
for collection_name, collection_info in data_to_display.items():
    if len(collection_info) < 2: continue
    datarow = datarow_format.replace("REPONAME", collection_name.replace("_", "\_"))
    for _, metrics in collection_info.items():
        for metric_name, metric_value in metrics.items():
            if type(metric_value) == float:
                datarow = datarow.replace(metric_name, f"{metric_value:.0f}")
            else:
                datarow = datarow.replace(metric_name, str(metric_value))
    datarows.append(datarow)

table += r"\midrule".join(datarows)
table += r"""
 \bottomrule
\end{tabular}
\caption{}
\label{tab:small_repo_results}
\end{table}
"""

print(table)