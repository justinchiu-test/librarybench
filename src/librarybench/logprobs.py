#!/usr/bin/env python
"""Script to get log probabilities from Together AI's OpenAI-compatible API."""

import os
import json
import asyncio
import argparse
from typing import Dict, List, Any, Optional

import aiohttp
from pydantic import BaseModel


class LogProbResult(BaseModel):
    """Result containing log probabilities from Together AI API."""

    text: list[str]
    logprobs: list[float]


async def get_log_probabilities(
    prompt: str,
    model: str = "Qwen/Qwen2.5-Coder-32B-Instruct",
    api_key: Optional[str] = None,
) -> LogProbResult:
    """Get log probabilities for a prompt using Together AI's API.

    Args:
        prompt: The prompt to get log probabilities for
        model: The model to use
        api_key: Together AI API key (defaults to TOGETHER_API_KEY env var)

    Returns:
        LogProbResult containing the text and log probabilities
    """
    api_key = api_key or os.environ.get("TOGETHER_API_KEY")
    if not api_key:
        raise ValueError("TOGETHER_API_KEY environment variable must be set")

    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    data = {
        "model": model,
        "stream": False,
        "max_tokens": 1,
        "messages": [{"role": "user", "content": prompt}],
        "logprobs": 1,
        "echo": True,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status != 200:
                error_text = await response.text()
                raise RuntimeError(f"API request failed: {response.status} - {error_text}")
            
            result = await response.json()
            
            # Extract text and logprobs from the response
            text = result["prompt"][0]["logprobs"]["tokens"][1:]
            logprobs_data = result["prompt"][0]["logprobs"]["token_logprobs"][1:]
            return LogProbResult(text=text, logprobs=logprobs_data)


async def main():
    """Run the script with command-line arguments."""
    parser = argparse.ArgumentParser(description="Get log probabilities from Together AI API")
    parser.add_argument("--prompt", type=str, default="write an async function in python",
                        help="Prompt to get log probabilities for")
    parser.add_argument("--model", type=str, default="Qwen/Qwen2.5-Coder-32B-Instruct",
                        help="Model to use")
    parser.add_argument("--max-tokens", type=int, default=10,
                        help="Maximum number of tokens to generate")
    parser.add_argument("--logprobs", type=int, default=1,
                        help="Number of most likely tokens to return for each position")
    parser.add_argument("--no-echo", action="store_false", dest="echo",
                        help="Don't include prompt in response")
    args = parser.parse_args()

    try:
        result = await get_log_probabilities(
            args.prompt,
            args.model,
            args.max_tokens,
            args.logprobs,
            args.echo,
        )
        
        # Pretty-print the result
        print("Text output:")
        print(result.text)
        print("\nLog probabilities:")
        print(json.dumps(result.logprobs, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
