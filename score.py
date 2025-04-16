import os
import argparse
from radon.complexity import cc_visit
from radon.raw import analyze

import json
import os

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

# Setup Together API
from together import Together

client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

def compute_logprob_together(text, model) -> float:
    """
    Compute log probability of text using Together API.

    Args:
        text (str): The input text to compute logprob for.
        model (str): The Together.ai model name.

    Returns:
        float: Average log probability across all tokens.
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": text}],
            max_tokens=0,
            echo=True,
            logprobs=1,
        )
        sum_logprobs = sum(response.choices[0].logprobs.token_logprobs)
        num_toks = len(response.choices[0].logprobs.token_logprobs)

    except Exception as e:
        print(f"[ERROR] Failed to compute logprobs: {e}")
        return float('nan'), float('nan')

    return sum_logprobs, num_toks
    
# ---- Code Metrics ----

def analyze_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()

    raw_metrics = analyze(code)

    cc_blocks = cc_visit(code)
    cyclomatic_total = sum(block.complexity for block in cc_blocks)

    return {
        'code': code,
        'loc': raw_metrics.loc,
        'sloc': raw_metrics.sloc,
        'lloc': raw_metrics.lloc,
        'cyclomatic_complexity': cyclomatic_total,
    }

# ---- Repo Metrics ----
def analyze_repo(files, logprob_mode, model):
    results = {}
    all_codes = []

    for filepath in files: 
        if filepath.endswith('.py'):
            file_metrics = analyze_file(filepath)
            all_codes.append(file_metrics["code"])

            # Compute per-file logprob if needed
            if logprob_mode == "individual":
                file_metrics["log_prob"], file_metrics["num_toks"] = compute_logprob_together(file_metrics["code"], model)
                code_lloc = remove_comments(file_metrics["code"])
                file_metrics["lloc_log_prob"], file_metrics["num_lloc_toks"] = compute_logprob_together(code_lloc, model)

            results[str(filepath)] = file_metrics

    # ---- Aggregate metrics ----
    aggregate = {
        "loc": 0,
        "sloc": 0,
        "lloc": 0,
        "cyclomatic_complexity": 0,
        "log_prob": 0.0,
        "num_toks": 0.0,
        "lloc_log_prob": 0.0,
        "num_lloc_toks": 0.0,
    }

    for metrics in results.values():
        aggregate["loc"] += metrics["loc"]
        aggregate["sloc"] += metrics["sloc"]
        aggregate["lloc"] += metrics["lloc"]
        aggregate["cyclomatic_complexity"] += metrics["cyclomatic_complexity"]

        if logprob_mode == "individual":
            aggregate["log_prob"] += metrics["log_prob"]
            aggregate["num_toks"] += metrics["num_toks"]
            aggregate["lloc_log_prob"] += metrics["lloc_log_prob"]
            aggregate["num_lloc_toks"] += metrics["num_lloc_toks"]


    # if concatenated mode
    if logprob_mode == "concat":
        full_code = "\n\n".join(all_codes)
        aggregate["log_prob"], aggregate["num_toks"] = compute_logprob_together(full_code, model)
        code_lloc = remove_comments(full_code)
        aggregate["lloc_log_prob"], aggregate["num_lloc_toks"] = compute_logprob_together(code_lloc, model)


    return {
        "per_file": results,
        "aggregate": aggregate
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Python files in a folder.")
    parser.add_argument("--files", type=str, nargs='+', help="Paths to .py files")
    parser.add_argument("--logprob-mode", choices=["individual", "concat"], default="individual",
                        help="Whether to compute logprobs per file and sum them, or on a single concatenated string")
    parser.add_argument("--model", type=str, default="Qwen2.5-Instruct", help="Name of the model hosted on vLLM")
    parser.add_argument("--output_file", type=str, help="Name of file to write to")
    parser.add_argument("--branch_name", type=str, help="Name of the branch we're on (this isn't automated!)")
    args = parser.parse_args()
    
    repo_metrics = {}
    if os.path.exists(args.output_file):
        repo_metrics = json.load(open(args.output_file))
    repo_metrics[args.branch_name] = analyze_repo(args.files, logprob_mode=args.logprob_mode, model=args.model)
    json.dump(repo_metrics, open(args.output_file, 'w'), indent=2)


# ---- Example usage ----
# python score.py --files workflow_orchestration_claude_refactor/workflow.py --output_file workflow_orchestration_metrics.json --model deepseek-ai/DeepSeek-V3 --branch_name claude_code