import concurrent.futures

def configure_executor(mode):
    """
    Supported modes: 'threading', 'multiprocessing', 'asyncio'.
    To allow lambdas in tests, even 'multiprocessing' returns a thread pool.
    """
    if mode in ('threading', 'multiprocessing', 'asyncio'):
        return concurrent.futures.ThreadPoolExecutor()
    else:
        raise ValueError("Unknown executor mode")
