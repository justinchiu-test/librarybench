"""Main entry point for PyMockAPI."""

import asyncio
import sys

from .mock_server import MockServer


async def main():
    """Run the mock server."""
    server = MockServer()
    print(f"Starting PyMockAPI on {server.host}:{server.port}")
    
    try:
        await server.start()
        # Keep server running
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())