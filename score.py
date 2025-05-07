import asyncio
import re

import os
import argparse
from radon.complexity import cc_visit
from radon.raw import analyze

import json
import os
from tqdm.asyncio import tqdm
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential

# ---- Helpers ----
import ast

def remove_comments(source: str) -> str:
    """
    Remove comments and docstrings from Python source code by parsing and unparsing
    the AST. Note: Comments are not present in the AST, so this effectively removes
    both comments and docstrings (since docstrings appear as literal expressions in the AST).

    Args:
        source (str): The original Python source code.

    Returns:
        str: The source code with comments and docstrings removed.
    """
    # Parse the source into an AST.
    try:
        tree = ast.parse(source)
    except SyntaxError as se:
        raise ValueError("Invalid Python code provided") from se

    # Define a NodeTransformer that will remove docstrings.
    class DocstringRemover(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            self.generic_visit(node)
            if (node.body and isinstance(node.body[0], ast.Expr) and 
                isinstance(node.body[0].value, ast.Constant) and 
                isinstance(node.body[0].value.value, str)):
                # Remove function docstring.
                node.body.pop(0)
            return node

        def visit_AsyncFunctionDef(self, node):
            self.generic_visit(node)
            if (node.body and isinstance(node.body[0], ast.Expr) and 
                isinstance(node.body[0].value, ast.Constant) and 
                isinstance(node.body[0].value.value, str)):
                # Remove async function docstring.
                node.body.pop(0)
            return node

        def visit_ClassDef(self, node):
            self.generic_visit(node)
            if (node.body and isinstance(node.body[0], ast.Expr) and 
                isinstance(node.body[0].value, ast.Constant) and 
                isinstance(node.body[0].value.value, str)):
                # Remove class docstring.
                node.body.pop(0)
            return node

        def visit_Module(self, node):
            self.generic_visit(node)
            if (node.body and isinstance(node.body[0], ast.Expr) and 
                isinstance(node.body[0].value, ast.Constant) and 
                isinstance(node.body[0].value.value, str)):
                # Remove module-level docstring.
                node.body.pop(0)
            return node

    # Remove docstrings by transforming the AST.
    tree = DocstringRemover().visit(tree)
    ast.fix_missing_locations(tree)

    try:
        # Python 3.9+ provides ast.unparse.
        new_source = ast.unparse(tree)
    except AttributeError:
        # For earlier versions of Python, you might use the astor package:
        #   pip install astor
        import astor
        new_source = astor.to_source(tree)

    return new_source


# ---- Logprobs ----

from together import AsyncTogether
client = AsyncTogether(api_key=os.getenv("TOGETHER_API_KEY"))
semaphore = asyncio.Semaphore(16)

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
async def compute_logprob_together(text, model):
    async with semaphore:
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": text}],
            max_tokens=1,
            echo=True,
            logprobs=1,
        )
        logprobs = response.prompt[0].logprobs.token_logprobs[1:]
        tokens = response.prompt[0].logprobs.tokens[1:]
        return logprobs, tokens

    
# ---- Code Metrics ----

def compute_code_metrics(code: str):
    raw_metrics = analyze(code)
    complexity_metrics = cc_visit(code)

    return {
        "loc": raw_metrics.loc,     # total lines of code
        "sloc": raw_metrics.sloc,   # source lines of code (non-blank, non-comment)
        "lloc": raw_metrics.lloc,   # logical lines (statements, e.g. `if`, `for`, `return`)
        "comments": raw_metrics.comments,
        "multi": raw_metrics.multi,
        "blank": raw_metrics.blank,
        "cyclomatic": sum(block.complexity for block in complexity_metrics),
    }

# ---- Repo Metrics ----

async def compute_metrics(directory, model, codebank_file=None):
    directory = Path(directory)

    total_logprob = 0.0
    total_tokens = 0
    failed_files = []
    logprobs_dict = {}
    metrics_dict = {}

    tasks = []
    program_names = []
    codes = {}
    codebank_logprobs, codebank_tokens = 0., []
    if codebank_file:
        try:
            with open(os.path.join(directory, codebank_file), "r") as f:
                codebank = f.read()
                codes[codebank_file] = codebank
            # Create task for codebank logprobs to be awaited later
            codebank_task = compute_logprob_together(codebank, model)
        except Exception as e:
            print(f"[ERROR] Failed to process {codebank_file}: {e}")
            failed_files.append(codebank_file)
    

    # If we have a codebank file, await its task first to get logprobs and tokens
    if codebank_file and 'codebank_task' in locals():
        try:
            codebank_logprobs, codebank_tokens = await codebank_task
            print(f"Processed codebank {codebank_file}: logprob={sum(codebank_logprobs):.2f}, tokens={len(codebank_tokens)}")
        except Exception as e:
            print(f"[ERROR] Failed to process codebank {codebank_file}: {e}")
            failed_files.append(codebank_file)
            codebank_logprobs, codebank_tokens = [], []

    # Store codebank results separately
    codebank_result = None
    
    for file in directory.glob("**/*.py"):
        if os.path.basename(file).startswith("test"): continue
        program_name = os.path.join(*file.parts[1:])
        program_names.append(program_name)
        if program_name == codebank_file:
            # Store codebank result separately instead of adding to tasks
            codebank_result = (codebank_logprobs, codebank_tokens)
            continue
        try:
            with open(file, "r") as f:
                code = f.read()
                codes[program_name] = code
            if codebank_file: 
                full_code = codes[codebank_file].rstrip() + "\n\n" + code
            else:
                full_code = code
            tasks.append(compute_logprob_together(full_code, model))
        except Exception as e:
            print(f"[ERROR] Failed to process {file.name}: {e}")
            failed_files.append(file.name)

    # Gather all non-codebank tasks
    other_results = await tqdm.gather(*tasks) if tasks else []
    
    # Combine results, inserting codebank result at the right position
    results = []
    task_index = 0
    for name in program_names:
        if name == codebank_file:
            results.append(codebank_result)
        else:
            if task_index < len(other_results):
                results.append(other_results[task_index])
                task_index += 1

    for program_name, result in zip(program_names, results):
        logprobs, tokens = result
        if logprobs is None or len(logprobs) == 0:
            failed_files.append(f"{program_name}.py")
            continue
        
        if program_name != codebank_file and codebank_file and len(codebank_tokens) > 0:
            # If we're processing a file that's conditioned on the codebank,
            # only count the logprobs after the codebank tokens
            sum_logprob = sum(logprobs[len(codebank_tokens)+1:]) if len(logprobs) > len(codebank_tokens)+1 else 0
            num_tokens = len(tokens[len(codebank_tokens)+1:]) if len(tokens) > len(codebank_tokens)+1 else 0
        else:
            sum_logprob = sum(logprobs)
            num_tokens = len(tokens)

        logprobs_dict[program_name] = sum_logprob
        metrics_dict[program_name] = compute_code_metrics(codes[program_name])

        total_logprob += sum_logprob
        total_tokens += num_tokens

        print(f"Processed {program_name}: logprob={sum_logprob:.2f}, tokens={num_tokens}")

    print("\n=== Summary ===")
    print(f"Full Repo Log Probability: {total_logprob:.2f}")
    print(f"Total Tokens: {total_tokens}")
    total_lloc = sum(m["lloc"] for m in metrics_dict.values())
    total_sloc = sum(m["sloc"] for m in metrics_dict.values())
    total_cyclomatic = sum(m["cyclomatic"] for m in metrics_dict.values())

    print(f"Total Logical LOC (LLOC): {total_lloc}")
    print(f"Total Source LOC (SLOC): {total_sloc}")
    print(f"Total Cyclomatic Complexity: {total_cyclomatic}")
    
    if failed_files:
        print(f"Failed files: {failed_files}")

    return logprobs_dict, total_logprob, metrics_dict, total_tokens

def package_all_metrics(logprobs, total_lp, metrics, total_tokens):
    result = {"total_logprobs": total_lp, "total_tokens": total_tokens}
    all_programs = set(logprobs) | set(metrics) 

    total_loc = 0
    total_sloc = 0
    total_lloc = 0
    total_comments = 0
    total_multi = 0
    total_blank = 0
    total_cyclomatic = 0

    for program in all_programs:
        lp = logprobs.get(program, float('nan'))
        program_metrics = metrics.get(program, {})
        result[program] = {
            "logprobs": lp,
            "metrics": program_metrics,
        }
        total_loc += program_metrics["loc"]
        total_sloc += program_metrics["sloc"]
        total_lloc += program_metrics["lloc"]
        total_comments += program_metrics["comments"]
        total_multi += program_metrics["multi"]
        total_blank += program_metrics["blank"]
        total_cyclomatic += program_metrics["cyclomatic"]
    
    result["total_loc"] = total_loc
    result["total_sloc"] = total_sloc
    result["total_lloc"] = total_lloc
    result["total_comments"] = total_comments
    result["total_multi"] = total_multi
    result["total_blank"] = total_blank
    result["total_cyclomatic"] = total_cyclomatic

    return result

async def main(args):
    parsed_experiment = re.search(r'(workflow_orchestration|document_editor|dependency_resolver|data_encoder)_(.+)', args.directory)

    output_file = f"{parsed_experiment.group(1)}_metrics.json"
    if args.branch_name is None:
        branch_name = parsed_experiment.group(2)
    else:
        branch_name = args.branch_name

    logprobs_dict, total_logprob, metrics_dict, total_tokens = await compute_metrics(args.directory, args.model, args.codebank_file)

    existing_metrics = json.load(open(output_file)) if os.path.exists(output_file) else {}
    existing_metrics[branch_name] = package_all_metrics(logprobs_dict, total_logprob, metrics_dict, total_tokens)
    json.dump(existing_metrics, open(output_file, 'w'), indent=2)

    results = {}
    if os.path.exists(os.path.join(args.directory, "results.json")):
        results = json.load(open(os.path.join(args.directory, "results.json")))
    
    results["metrics"] = existing_metrics[branch_name]
    with open(os.path.join(args.directory, "results.json"), 'w') as wf:
        json.dump(results, wf, indent=4)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Python files in a folder.")
    parser.add_argument("--directory", type=str, help="Paths to .py files")
    parser.add_argument("--model", type=str, default="deepseek-ai/DeepSeek-V3", help="Name of the model hosted on vLLM")
    parser.add_argument("--branch_name", type=str, default=None, help="What key to log the metrics under")
    parser.add_argument("--codebank_file", type=str, default=None, help="Codebank file to condition on")
    args = parser.parse_args()
    
    asyncio.run(main(args))

# ---- Example usage ----
# python score.py --directory workflow_orchestration_claude_refactor --output_file workflow_orchestration_metrics.json --model deepseek-ai/DeepSeek-V3 --branch_name claude_code