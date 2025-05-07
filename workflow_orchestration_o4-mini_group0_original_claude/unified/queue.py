"""
Task queue implementation for the unified workflow orchestration system.
"""
import heapq
import threading
import queue
from typing import Any, Dict, List, Optional, TypeVar, Generic

T = TypeVar('T')

class PriorityQueue(Generic[T]):
    """
    Priority queue implementation for tasks.
    """
    def __init__(self):
        self._queue: List[T] = []
        self._lock = threading.Lock()
    
    def push(self, item: T):
        """
        Add an item to the queue.
        
        :param item: Item to add (must support __lt__ comparison)
        """
        with self._lock:
            heapq.heappush(self._queue, item)
    
    def pop(self) -> Optional[T]:
        """
        Remove and return the highest priority item.
        
        :return: Highest priority item or None if queue is empty
        """
        with self._lock:
            if not self._queue:
                return None
            return heapq.heappop(self._queue)
    
    def peek(self) -> Optional[T]:
        """
        Return the highest priority item without removing it.
        
        :return: Highest priority item or None if queue is empty
        """
        with self._lock:
            if not self._queue:
                return None
            return self._queue[0]
    
    def __len__(self) -> int:
        """
        Return the number of items in the queue.
        
        :return: Number of items
        """
        with self._lock:
            return len(self._queue)
    
    def is_empty(self) -> bool:
        """
        Check if the queue is empty.
        
        :return: True if empty, False otherwise
        """
        with self._lock:
            return len(self._queue) == 0


class FIFOQueue(Generic[T]):
    """
    First-in, first-out queue implementation.
    """
    def __init__(self):
        self._queue = queue.Queue()
    
    def push(self, item: T):
        """
        Add an item to the queue.
        
        :param item: Item to add
        """
        self._queue.put(item)
    
    def pop(self) -> T:
        """
        Remove and return the next item.
        
        :return: Next item
        """
        return self._queue.get()
    
    def task_done(self):
        """
        Indicate that a formerly enqueued task is complete.
        """
        self._queue.task_done()
    
    def join(self):
        """
        Block until all items in the queue have been processed.
        """
        self._queue.join()
    
    def __len__(self) -> int:
        """
        Return the approximate number of items in the queue.
        
        :return: Approximate number of items
        """
        return self._queue.qsize()
    
    def is_empty(self) -> bool:
        """
        Check if the queue is empty.
        
        :return: True if empty, False otherwise
        """
        return self._queue.empty()