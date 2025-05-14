import asyncio

class Simulator:
    def __init__(self, fsm):
        self.fsm = fsm
        self.events = []

    def feed(self, event):
        self.events.append(event)

    def stub(self, name, func):
        self.fsm.context[name] = func

    async def run(self):
        for ev in self.events:
            await self.fsm.trigger(ev)
        return self.fsm.state
