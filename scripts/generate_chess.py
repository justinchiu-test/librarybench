#!/usr/bin/env python
"""Script to generate solutions for chess problems in TACO dataset."""

import os
import asyncio
import argparse
from typing import Optional
from librarybench.generation import generate_solutions


async def main(
    model_type: str = "claude",
    model_name: Optional[str] = None,
    sample_size: int = 5,
    concurrency: int = 5,
    output_dir: str = "data",
):
    """Generate solutions for chess problems.

    Args:
        model_type: Type of model to use ("openai" or "claude")
        model_name: Specific model name (optional)
        sample_size: Number of examples to process
        concurrency: Number of concurrent requests
        output_dir: Directory for output files
    """
    # Check environment variables
    if model_type == "openai" and not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    if model_type == "claude" and not os.environ.get("ANTHROPIC_API_KEY"):
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
    cyber_url = os.environ.get("CYBER_URL")
    if not cyber_url:
        raise ValueError("CYBER_URL environment variable is not set")

    # Set default model name if not provided
    if model_name is None:
        if model_type == "openai":
            model_name = "o3-mini"
        else:
            model_name = "claude-3-7-sonnet-20250219"

    print(f"Generating chess problem solutions using {model_name}...")
    await generate_solutions(
        model_type=model_type,
        model_name=model_name,
        sample_size=sample_size,
        concurrency=concurrency,
        problem_types=["chess"],  # Only generate chess problems
        output_dir=output_dir,
    )

    print("\nGeneration complete!")
    model_key = model_name.replace("-", "_").replace(".", "_")
    print(f"Results saved to: {output_dir}/{model_key}_chess_solutions.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate solutions for chess problems in TACO"
    )
    parser.add_argument(
        "--model-type",
        choices=["openai", "claude"],
        default="claude",
        help="Type of model to use (openai or claude)",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        help="Specific model name (e.g., 'o3-mini' or 'claude-3-opus-20240229')",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=5,
        help="Number of examples to process",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=5,
        help="Number of concurrent requests",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data",
        help="Directory for output files",
    )

    args = parser.parse_args()

    asyncio.run(
        main(
            model_type=args.model_type,
            model_name=args.model_name,
            sample_size=args.sample_size,
            concurrency=args.concurrency,
            output_dir=args.output_dir,
        )
    )
