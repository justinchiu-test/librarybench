import asyncio
import aiohttp
import logging
import random

class WebhookIntegration:
    def __init__(
        self,
        endpoints: list,
        retry_attempts: int = 3,
        backoff_factor: float = 0.5,
        logger: logging.Logger = None,
    ):
        self.endpoints = endpoints
        self.retry_attempts = retry_attempts
        self.backoff_factor = backoff_factor
        self.logger = logger or logging.getLogger("WebhookIntegration")

    async def send(self, payload: dict):
        for url in self.endpoints:
            await self._post_with_retry(url, payload)

    async def _post_with_retry(self, url: str, payload: dict):
        attempt = 0
        while attempt < self.retry_attempts:
            try:
                # open a fresh session on each try
                async with aiohttp.ClientSession() as session:
                    # first await the post coroutine, then use its context manager
                    resp_ctx = await session.post(url, json=payload)
                    async with resp_ctx as resp:
                        if resp.status < 400:
                            self.logger.debug(f"Posted to {url}: {resp.status}")
                            return
                        else:
                            raise Exception(f"HTTP {resp.status}")
            except Exception as e:
                attempt += 1
                wait = self.backoff_factor * (2 ** (attempt - 1))
                self.logger.warning(f"Post failed to {url}: {e}, retry {attempt} in {wait}s")
                await asyncio.sleep(wait)
        self.logger.error(f"Failed to post to {url} after {self.retry_attempts} attempts")
