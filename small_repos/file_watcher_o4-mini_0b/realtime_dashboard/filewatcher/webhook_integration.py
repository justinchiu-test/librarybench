import json
import asyncio

class WebhookIntegration:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self._last_event = None

    async def post_event(self, event: dict) -> bool:
        # Simulated async post to HTTP-to-Kafka bridge
        await asyncio.sleep(0)  # yield control
        # Ensure Enums (and other weird types) are serialized by .value
        self._last_event = json.dumps(event, default=lambda o: getattr(o, 'value', o))
        return True

    def last_event(self):
        return self._last_event
