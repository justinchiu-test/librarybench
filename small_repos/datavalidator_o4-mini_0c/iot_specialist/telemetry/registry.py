import asyncio

class AsyncRegistryClient:
    def __init__(self, registry_data=None):
        # registry_data: set of valid device_ids
        self.registry_data = registry_data or set()

    async def validate_certificate(self, device_id):
        # Simulate async remote call
        await asyncio.sleep(0)
        return device_id in self.registry_data
