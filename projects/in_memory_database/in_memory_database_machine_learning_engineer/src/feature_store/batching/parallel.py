"""
Parallel processing capabilities for batch operations.
"""

import concurrent.futures
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union, Generic, cast

import numpy as np
from joblib import Parallel, delayed
from pydantic import BaseModel, Field

from feature_store.batching.batch_retriever import BatchOperation
from feature_store.vectors.base import VectorBase

# Type variables for generic functions
T = TypeVar('T')
U = TypeVar('U')


class ChunkResult(BaseModel, Generic[T]):
    """Results from processing a chunk of data."""
    
    chunk_index: int = Field(..., description="Index of the chunk")
    results: List[T] = Field(..., description="Results for this chunk")
    timing: Dict[str, float] = Field(default_factory=dict, description="Timing information")
    
    class Config:
        """Pydantic configuration."""
        
        arbitrary_types_allowed = True


class ParallelProcessor(BatchOperation):
    """
    Parallel processor for batch operations.
    
    This class provides parallel processing capabilities for batch operations,
    allowing efficient use of multiple cores.
    """

    n_jobs: int = Field(-1, description="Number of parallel jobs (-1 for all cores)")
    chunk_size: Optional[int] = Field(None, description="Size of each chunk (None for auto)")
    backend: str = Field("threading", description="Parallelization backend (threading or multiprocessing)")
    timeout: Optional[float] = Field(None, description="Timeout for parallel execution in seconds")
    log_timing: bool = Field(False, description="Whether to log timing information")
    
    def process_parallel(
        self,
        items: List[T],
        process_fn: Callable[[List[T]], List[U]],
        n_chunks: Optional[int] = None
    ) -> List[U]:
        """Process items in parallel.
        
        Args:
            items: List of items to process
            process_fn: Function to process each chunk of items
            n_chunks: Number of chunks to split items into (default: n_jobs)
            
        Returns:
            List of processed items
        """
        # Start timing
        start_time = time.time()
        timing = {}
        
        # Determine number of chunks
        if n_chunks is None:
            n_chunks = self.n_jobs if self.n_jobs > 0 else 4
        
        # Calculate chunk size
        chunk_size = self.chunk_size
        if chunk_size is None:
            chunk_size = max(1, len(items) // n_chunks)
        
        # Split items into chunks
        chunks = [items[i:i+chunk_size] for i in range(0, len(items), chunk_size)]
        
        # Record preparation time
        if self.log_timing:
            timing["prepare"] = time.time() - start_time
            timing["num_items"] = len(items)
            timing["num_chunks"] = len(chunks)
        
        # Process chunks in parallel
        parallel_start = time.time()
        
        if self.backend == "futures":
            # Use concurrent.futures
            results = self._process_with_futures(chunks, process_fn)
        else:
            # Use joblib
            results = self._process_with_joblib(chunks, process_fn)
        
        # Record parallel processing time
        if self.log_timing:
            timing["parallel_processing"] = time.time() - parallel_start
            timing["total"] = time.time() - start_time
        
        # Flatten results
        flat_results = []
        for chunk_result in results:
            flat_results.extend(chunk_result.results)
            
            # Update timing
            if self.log_timing:
                for k, v in chunk_result.timing.items():
                    if k in timing:
                        timing[k] += v
                    else:
                        timing[k] = v
        
        return flat_results
    
    def _process_with_joblib(
        self,
        chunks: List[List[T]],
        process_fn: Callable[[List[T]], List[U]]
    ) -> List[ChunkResult[U]]:
        """Process chunks using joblib.
        
        Args:
            chunks: List of chunks to process
            process_fn: Function to process each chunk
            
        Returns:
            List of ChunkResult objects
        """
        # Process each chunk in parallel
        chunk_results = Parallel(n_jobs=self.n_jobs, backend=self.backend, timeout=self.timeout)(
            delayed(self._process_chunk)(i, chunk, process_fn)
            for i, chunk in enumerate(chunks)
        )
        
        return chunk_results
    
    def _process_with_futures(
        self,
        chunks: List[List[T]],
        process_fn: Callable[[List[T]], List[U]]
    ) -> List[ChunkResult[U]]:
        """Process chunks using concurrent.futures.
        
        Args:
            chunks: List of chunks to process
            process_fn: Function to process each chunk
            
        Returns:
            List of ChunkResult objects
        """
        # Choose executor based on backend
        if self.backend == "threading":
            executor_cls = concurrent.futures.ThreadPoolExecutor
        else:
            executor_cls = concurrent.futures.ProcessPoolExecutor
        
        # Determine max workers
        max_workers = self.n_jobs if self.n_jobs > 0 else None
        
        # Process in parallel
        chunk_results = []
        with executor_cls(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self._process_chunk, i, chunk, process_fn)
                for i, chunk in enumerate(chunks)
            ]
            
            # Wait for completion with timeout if specified
            if self.timeout is not None:
                # Use wait with timeout
                done, not_done = concurrent.futures.wait(
                    futures, 
                    timeout=self.timeout,
                    return_when=concurrent.futures.ALL_COMPLETED
                )
                
                # Cancel any remaining futures
                for future in not_done:
                    future.cancel()
                
                # Get results from completed futures
                for future in done:
                    try:
                        chunk_results.append(future.result())
                    except Exception as e:
                        # Handle errors
                        print(f"Error processing chunk: {e}")
            else:
                # No timeout, wait for all to complete
                for future in concurrent.futures.as_completed(futures):
                    try:
                        chunk_results.append(future.result())
                    except Exception as e:
                        # Handle errors
                        print(f"Error processing chunk: {e}")
        
        # Sort by chunk index
        chunk_results.sort(key=lambda x: x.chunk_index)
        
        return chunk_results
    
    def _process_chunk(
        self,
        chunk_index: int,
        chunk: List[T],
        process_fn: Callable[[List[T]], List[U]]
    ) -> ChunkResult[U]:
        """Process a chunk of items.
        
        Args:
            chunk_index: Index of the chunk
            chunk: List of items in the chunk
            process_fn: Function to process the chunk
            
        Returns:
            ChunkResult with the results for this chunk
        """
        # Start timing
        start_time = time.time()
        
        # Process the chunk
        results = process_fn(chunk)
        
        # Record timing information
        timing = {
            "chunk_time": time.time() - start_time,
            "chunk_size": len(chunk),
            "result_size": len(results)
        }
        
        # Create result
        return ChunkResult(
            chunk_index=chunk_index,
            results=results,
            timing=timing
        )
    
    def map_vectors(
        self,
        vectors: Dict[str, VectorBase],
        map_fn: Callable[[VectorBase], VectorBase]
    ) -> Dict[str, VectorBase]:
        """Apply a function to a dictionary of vectors in parallel.
        
        Args:
            vectors: Dictionary of key to vector
            map_fn: Function to apply to each vector
            
        Returns:
            Dictionary of key to transformed vector
        """
        # Convert to list of (key, vector) pairs
        items = list(vectors.items())
        
        # Define function to process a chunk
        def process_chunk(chunk: List[Tuple[str, VectorBase]]) -> List[Tuple[str, VectorBase]]:
            return [(key, map_fn(vector)) for key, vector in chunk]
        
        # Process in parallel
        results = self.process_parallel(items, process_chunk)
        
        # Convert back to dictionary
        return dict(results)
    
    def batch_compute(
        self,
        inputs: List[T],
        compute_fn: Callable[[T], U],
        chunk_size: Optional[int] = None
    ) -> List[U]:
        """Compute a function on a list of inputs in parallel.
        
        Args:
            inputs: List of inputs
            compute_fn: Function to compute on each input
            chunk_size: Size of each chunk (default: auto)
            
        Returns:
            List of computed outputs
        """
        # Override chunk size if specified
        old_chunk_size = self.chunk_size
        if chunk_size is not None:
            self.chunk_size = chunk_size
        
        # Define function to process a chunk
        def process_chunk(chunk: List[T]) -> List[U]:
            return [compute_fn(item) for item in chunk]
        
        # Process in parallel
        results = self.process_parallel(inputs, process_chunk)
        
        # Restore chunk size
        self.chunk_size = old_chunk_size
        
        return results