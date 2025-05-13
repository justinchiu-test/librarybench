"""
A minimal stub of aiohttp.ClientSession to support WebhookIntegration
and allow tests to monkeypatch ClientSession.
"""
class ClientSession:
    async def __aenter__(self):
        # return self as the session
        return self

    async def __aexit__(self, exc_type, exc, tb):
        # nothing to clean up
        pass

    async def post(self, url, json):
        """
        Default behavior: raise so that send() swallows the exception.
        Tests should monkeypatch ClientSession to provide their own behavior.
        """
        raise NotImplementedError("Stub ClientSession, please monkeypatch in tests")
