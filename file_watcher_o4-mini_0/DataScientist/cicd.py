import asyncio

class CiCdTrigger:
    def __init__(self, command):
        self.command = command

    async def trigger(self, path, event_type):
        proc = await asyncio.create_subprocess_shell(
            f"{self.command} {path} {event_type}"
        )
        await proc.wait()
        return proc.returncode
