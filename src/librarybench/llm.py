"""LLM interaction module for solution generation and improvement."""

import asyncio
import logging
from typing import Optional

from librarybench.models.llm_client import LlmClient

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Set up semaphore for API calls
LLM_SEMAPHORE = asyncio.Semaphore(5)


async def query_model(
    prompt: str,
    llm_client: LlmClient,
    system_prompt: str = "You are an expert Python programmer.",
    iteration: Optional[int] = None,
) -> str:
    """
    Send a query to the LLM and get a response.

    Args:
        prompt: The prompt to send to the model
        llm_client: The LLM client to use
        system_prompt: The system prompt to use
        iteration: Optional iteration number for logging

    Returns:
        The model's response
    """
    async with LLM_SEMAPHORE:
        # Log the request
        if iteration is not None:
            logger.info(f"Iteration {iteration} for LLM query")

        logger.info(
            f"Querying {llm_client.model_name} with prompt (length: {len(prompt)} chars)"
        )

        # Call the model
        try:
            response = await llm_client.generate_completion(prompt, system_prompt)
            return response
        except Exception as e:
            logger.error(f"Error querying model: {str(e)}")
            return ""
