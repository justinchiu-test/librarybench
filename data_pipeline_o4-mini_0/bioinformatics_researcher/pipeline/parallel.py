from concurrent.futures import ThreadPoolExecutor, as_completed
import os

class ParallelExecutor:
    def __init__(self, max_workers=None):
        self.max_workers = max_workers or os.cpu_count() or 1
    def map(self, func, items):
        results = [None] * len(items)
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(func, item): idx for idx, item in enumerate(items)}
            for fut in as_completed(futures):
                idx = futures[fut]
                results[idx] = fut.result()
        return results
