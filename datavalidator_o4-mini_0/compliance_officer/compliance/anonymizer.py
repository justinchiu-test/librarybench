import asyncio

async def anonymize_field(value):
    # Simulate an async call to an external anonymization service
    await asyncio.sleep(0.01)
    return "****"

async def anonymize_pii(data, fields):
    tasks = []
    for f in fields:
        if f in data:
            tasks.append((f, asyncio.create_task(anonymize_field(data[f]))))
    for f, task in tasks:
        data[f] = await task
    return data
