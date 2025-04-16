### conda activate openai_0.28
import os
import argparse
from radon.complexity import cc_visit
from radon.metrics import h_visit
from radon.raw import analyze

import openai
import json

# ---- Logprob via vLLM OpenAI-compatible API ----
openai.api_base = os.getenv("OPENAI_API_BASE", "http://nlplarge-compute-01:9646/v1") # change badfellow --> gpu-node name | 9649 --> forwarding number
# openai.api_base = os.getenv("OPENAI_API_BASE", "http://rush-compute-03:9646/v1") # change badfellow --> gpu-node name | 9649 --> forwarding number
# openai.api_base = os.getenv("OPENAI_API_BASE", "http://0.0.0.0:9646/v1") # change badfellow --> gpu-node name | 9649 --> forwarding number
openai.api_key = os.getenv("OPENAI_API_KEY")

# change `model` based on the name in vLLM serve
def compute_logprob_vllm(text, model="Qwen2.5-Instruct", chunk_size=2048*3) -> float:
    # import tiktoken  
    # tokenizer = tiktoken.encoding_for_model(model)
    # tokens = tokenizer.encode(text)

    total_logprob = 0.0
    for i in range(0, len(text), chunk_size):
        # chunk_tokens = tokens[i:i + chunk_size]
        # chunk_text = tokenizer.decode(chunk_tokens)
        chunk_text = text[i:i+chunk_size]
        
        try:
            response = openai.Completion.create(
                model=model,
                prompt=chunk_text,
                echo=True,
                logprobs=1,
                max_tokens=1
            )
            logprobs = response['choices'][0]['logprobs']['token_logprobs']
            total_logprob += sum(lp for lp in logprobs if lp is not None)
        except Exception as e:
            print(f"[ERROR] Failed at chunk {i}: {e}")
            return float('nan')

    return total_logprob
    

# ---- Code Metrics ----

def analyze_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()

    raw_metrics = analyze(code)

    cc_blocks = cc_visit(code)
    cyclomatic_total = sum(block.complexity for block in cc_blocks)

    # Halstead Metrics (just found this, migth be useful)
    # h_metrics = h_visit(code).total  # This is a HalsteadReport namedtuple
    # halstead_dict = h_metrics._asdict()  

    return {
        'code': code,
        'loc': raw_metrics.loc,
        'sloc': raw_metrics.sloc,
        'lloc': raw_metrics.lloc,
        'cyclomatic_complexity': cyclomatic_total,
        # 'halstead': halstead_dict
    }

from collections import defaultdict
# ---- Repo Metrics ----
def analyze_repo(files, logprob_mode="individual", model="Qwen2.5-Instruct"):
    results = {}
    all_codes = []

    for filepath in files: #os.listdir(folder_path):
        if filepath.endswith('.py'):
            # filepath = os.path.join(folder_path, filename)
            file_metrics = analyze_file(filepath)
            all_codes.append(file_metrics["code"])

            # Compute per-file logprob if needed
            if logprob_mode == "individual":
                file_metrics["log_prob"] = compute_logprob_vllm(file_metrics["code"], model)

            results[str(filepath)] = file_metrics

    # ---- Aggregate metrics ----
    aggregate = {
        "loc": 0,
        "sloc": 0,
        "lloc": 0,
        "cyclomatic_complexity": 0,
        "log_prob": 0.0,
        # "halstead": defaultdict(float) # will be all 0 if there is no operands or operators
    }

    for metrics in results.values():
        aggregate["loc"] += metrics["loc"]
        aggregate["sloc"] += metrics["sloc"]
        aggregate["lloc"] += metrics["lloc"]
        aggregate["cyclomatic_complexity"] += metrics["cyclomatic_complexity"]

        if logprob_mode == "individual":
            aggregate["log_prob"] += metrics["log_prob"]

        # for key, val in metrics["halstead"].items():
        #     aggregate["halstead"][key] += val

    # if concatenated mode
    if logprob_mode == "concat":
        full_code = "\n\n".join(all_codes)
        aggregate["log_prob"] = compute_logprob_vllm(full_code, model)

    # aggregate["halstead"] = dict(aggregate["halstead"])

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
# 1. serve vLLM, I do `vllm serve Qwen/Qwen2.5-1.5B-Instruct --host 0.0.0.0 --port 9646 --served-model-name Qwen2.5-Instruct`
# 2. python score.py ./folder_path --output_file folder_path_metrics.json --logprob-mode individual (or concat) (optional) --model Qwen2.5-Instruct
# RETURNS: dictionary with per-file metrics and aggregate metrics