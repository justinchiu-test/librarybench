import aiohttp
import asyncio

class WebhookClient:
    def __init__(self, url, max_retries=3, base_backoff=1):
        self.url = url
        self.max_retries = max_retries
        self.base_backoff = base_backoff
        # Delay session creation until first send (so __init__ can run without a running loop)
        self.session = None

    async def send(self, payload):
        # Lazily create the aiohttp session in an async context
        if self.session is None:
            self.session = aiohttp.ClientSession()
        for attempt in range(1, self.max_retries + 1):
            try:
                async with self.session.post(self.url, json=payload) as resp:
                    if resp.status < 400:
                        return True
            except Exception:
                pass
            # exponential backoff
            await asyncio.sleep(self.base_backoff * (2 ** (attempt - 1)))
        return False

    async def close(self):
        if self.session is not None:
            await self.session.close()
