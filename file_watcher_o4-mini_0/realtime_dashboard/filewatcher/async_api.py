import asyncio

class AsyncIOAPI:
    def __init__(self, roots, filter_rules, event_detector, webhook=None):
        self.roots = roots
        self.filter_rules = filter_rules
        self.event_detector = event_detector
        self.webhook = webhook

    async def watch(self):
        # Simulated watch: yield one dummy event
        await asyncio.sleep(0)
        raw_event = {'event_type': 'created', 'src_path': self.roots[0] + '/file.txt'}
        if self.filter_rules.match(raw_event['src_path']):
            high = self.event_detector.detect(raw_event)
            if self.webhook:
                await self.webhook.post_event(high)
            yield high
