"""Parallelization utilities for query language interpreters."""

import concurrent.futures
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

T = TypeVar("T")
U = TypeVar("U")


def parallel_process(
    items: List[T],
    process_func: Callable[[T], U],
    max_workers: int = None,
    timeout: Optional[float] = None,
    use_processes: bool = False,
) -> List[U]:
    """Process items in parallel.

    Args:
        items: Items to process
        process_func: Function to apply to each item
        max_workers: Maximum number of workers (None for default)
        timeout: Timeout in seconds (None for no timeout)
        use_processes: Whether to use processes instead of threads

    Returns:
        List[U]: Processed results

    Raises:
        concurrent.futures.TimeoutError: If timeout is reached
    """
    executor_class = (
        concurrent.futures.ProcessPoolExecutor
        if use_processes
        else concurrent.futures.ThreadPoolExecutor
    )

    with executor_class(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_item = {executor.submit(process_func, item): item for item in items}

        # Collect results as they complete
        results = []
        for future in concurrent.futures.as_completed(
            future_to_item.keys(), timeout=timeout
        ):
            result = future.result()
            results.append(result)

        return results


def parallel_map(
    func: Callable[[T], U],
    items: List[T],
    max_workers: int = None,
    chunk_size: int = 1,
    use_processes: bool = False,
) -> List[U]:
    """Apply a function to items in parallel.

    Args:
        func: Function to apply
        items: Items to process
        max_workers: Maximum number of workers (None for default)
        chunk_size: Items per task
        use_processes: Whether to use processes instead of threads

    Returns:
        List[U]: Results
    """
    executor_class = (
        concurrent.futures.ProcessPoolExecutor
        if use_processes
        else concurrent.futures.ThreadPoolExecutor
    )

    with executor_class(max_workers=max_workers) as executor:
        return list(executor.map(func, items, chunksize=chunk_size))


class BatchProcessor:
    """Process items in batches."""

    def __init__(
        self,
        batch_size: int = 100,
        max_workers: int = None,
        use_processes: bool = False,
    ):
        """Initialize a batch processor.

        Args:
            batch_size: Size of each batch
            max_workers: Maximum number of workers
            use_processes: Whether to use processes instead of threads
        """
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.use_processes = use_processes

    def process(
        self,
        items: List[T],
        process_func: Callable[[List[T]], List[U]],
    ) -> List[U]:
        """Process items in batches.

        Args:
            items: Items to process
            process_func: Function to apply to each batch

        Returns:
            List[U]: Processed results
        """
        # Split items into batches
        batches = [
            items[i : i + self.batch_size]
            for i in range(0, len(items), self.batch_size)
        ]

        # Process batches in parallel
        batch_results = parallel_process(
            batches,
            process_func,
            max_workers=self.max_workers,
            use_processes=self.use_processes,
        )

        # Flatten results
        results = []
        for batch_result in batch_results:
            results.extend(batch_result)

        return results
