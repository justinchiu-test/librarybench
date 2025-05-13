import os
import asyncio
from .async_api import AsyncIOAPI
from .utils import normalize_event

class RecursiveDirectoryWatch(AsyncIOAPI):
    async def watch(self):
        # Very basic recursive scan simulation
        for root in self.roots:
            for dirpath, dirnames, filenames in os.walk(root):
                for fname in filenames:
                    path = os.path.join(dirpath, fname)
                    raw = normalize_event({'event_type': 'modified', 'src_path': path})
                    if self.filter_rules.match(path):
                        high = self.event_detector.detect(raw)
                        if self.webhook:
                            await self.webhook.post_event(high)
                        yield high
        # final yield barrier
        await asyncio.sleep(0)
