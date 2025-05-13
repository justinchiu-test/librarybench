import asyncio

async def default_external_validator(field, value):
    # Simulate external call latency
    await asyncio.sleep(0)
    return True
