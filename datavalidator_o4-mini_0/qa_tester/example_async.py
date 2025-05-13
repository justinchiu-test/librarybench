import asyncio

async def tax_id_lookup(tax_id):
    # Simulate an external service lookup
    if tax_id == "timeout":
        # Will cause a timeout if timeout < 1
        await asyncio.sleep(1)
        return True
    await asyncio.sleep(0)  # instant for normal cases
    # Valid if starts with TX
    return isinstance(tax_id, str) and tax_id.startswith("TX")
