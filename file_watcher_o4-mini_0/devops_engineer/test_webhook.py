import asyncio
import pytest
import aiohttp
from aiohttp import web
from filewatcher.webhook import WebhookIntegration

@pytest.fixture
def aiohttp_server(loop, free_tcp_port_factory):
    def _make_server(app: web.Application):
        async def _serve():
            runner = web.AppRunner(app)
            await runner.setup()
            port = free_tcp_port_factory()
            site = web.TCPSite(runner, "127.0.0.1", port)
            await site.start()
            class Server:
                def make_url(self, path: str) -> str:
                    return f"http://127.0.0.1:{port}{path}"
            return Server()
        return _serve()
    return _make_server

@pytest.mark.asyncio
async def test_webhook_success(aiohttp_server):
    calls = []
    async def handler(request):
        data = await request.json()
        calls.append(data)
        return web.Response(text="ok")

    app = web.Application()
    app.router.add_post("/", handler)
    server = await aiohttp_server(app)
    url = str(server.make_url("/"))
    webhook = WebhookIntegration([url], retry_attempts=2, backoff_factor=0.01)
    payload = {"foo": "bar"}
    await webhook.send(payload)
    assert calls == [payload]

@pytest.mark.asyncio
async def test_webhook_retry(aiohttp_server):
    attempts = {"count": 0}
    async def handler(request):
        attempts["count"] += 1
        if attempts["count"] < 2:
            return web.Response(status=500)
        return web.Response(text="ok")

    app = web.Application()
    app.router.add_post("/", handler)
    server = await aiohttp_server(app)
    url = str(server.make_url("/"))
    webhook = WebhookIntegration([url], retry_attempts=3, backoff_factor=0.01)
    payload = {"x": 1}
    await webhook.send(payload)
    assert attempts["count"] == 2
