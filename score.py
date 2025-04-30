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

async def compute_metrics(directory, model):
    directory = Path(directory)

    total_logprob = 0.0
    total_tokens = 0
    failed_files = []
    logprobs_dict = {}
    metrics_dict = {}

    tasks = []
    program_names = []
    codes = {}
    for file in directory.glob("**/*.py"):
        if os.path.basename(file).startswith("test"): continue
        program_name = file.name.replace(".py", "")
        program_names.append(program_name)
        try:
            with open(file, "r") as f:
                code = f.read()
                codes[program_name] = code
            tasks.append(compute_logprob_together(code, model))
        except Exception as e:
            print(f"[ERROR] Failed to process {file.name}: {e}")
            failed_files.append(file.name)

    results = await tqdm.gather(*tasks)

    for program_name, result in zip(program_names, results):
        logprobs, tokens = result
        if logprobs is None:
            failed_files.append(f"{program_name}.py")
            continue

        sum_logprob = sum(logprobs)
        num_tokens = len(tokens)

        logprobs_dict[program_name] = sum_logprob
        metrics_dict[program_name] = compute_code_metrics(codes[program_name])

        total_logprob += sum_logprob
        total_tokens += num_tokens

        print(f"Processed {program_name}: logprob={sum_logprob:.2f}, tokens={num_tokens}")

    print("\n=== Summary ===")
    print(f"Total Log Probability: {total_logprob:.2f}")
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

    for program in all_programs:
        lp = logprobs.get(program, float('nan'))

        result[program] = {
            "logprobs": lp,
            "metrics": metrics.get(program, {}),
        }

    return result

async def main(args):
    parsed_experiment = re.search(r'(workflow_orchestration|document_editor|dependency_resolver|data_encoder)_(.+)', args.directory)

    output_file = f"{parsed_experiment.group(1)}_persona_metrics.json"
    branch_name = parsed_experiment.group(2)

    logprobs_dict, total_logprob, metrics_dict, total_tokens = await compute_metrics(args.directory, args.model)

    existing_metrics = json.load(open(output_file)) if os.path.exists(output_file) else {}
    existing_metrics[branch_name] = package_all_metrics(logprobs_dict, total_logprob, metrics_dict, total_tokens)
    json.dump(existing_metrics, open(output_file, 'w'), indent=2)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Python files in a folder.")
    parser.add_argument("--directory", type=str, help="Paths to .py files")
    parser.add_argument("--model", type=str, default="deepseek-ai/DeepSeek-V3", help="Name of the model hosted on vLLM")
    args = parser.parse_args()
    
    asyncio.run(main(args))

# ---- Example usage ----
# python score.py --directory workflow_orchestration_claude_refactor --output_file workflow_orchestration_metrics.json --model deepseek-ai/DeepSeek-V3 --branch_name claude_code