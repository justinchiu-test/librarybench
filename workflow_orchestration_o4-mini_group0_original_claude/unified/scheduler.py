"""
Scheduler for time-based task execution.
"""
import threading
import time
import uuid
from typing import Callable, Dict, List, Any, Optional

from unified.logger import default_logger


class ScheduleEntry:
    """
    Represents a scheduled task.
    """
    def __init__(
        self,
        schedule_id: str,
        interval_seconds: float,
        callback: Callable,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a schedule entry.
        
        :param schedule_id: Unique identifier for the schedule
        :param interval_seconds: Interval between executions
        :param callback: Function to call
        :param args: Positional arguments for the callback
        :param kwargs: Keyword arguments for the callback
        """
        self.schedule_id = schedule_id
        self.interval_seconds = interval_seconds
        self.callback = callback
        self.args = args or []
        self.kwargs = kwargs or {}
        self.last_run: Optional[float] = None
        self.is_active = True
    
    def should_run(self, current_time: float) -> bool:
        """
        Check if this schedule should run at the current time.
        
        :param current_time: Current time in seconds
        :return: True if schedule should run, False otherwise
        """
        if not self.is_active:
            return False
            
        if self.last_run is None:
            return True
            
        return (current_time - self.last_run) >= self.interval_seconds
    
    def mark_run(self, current_time: float):
        """
        Mark the schedule as having run at the current time.
        
        :param current_time: Current time in seconds
        """
        self.last_run = current_time


class Scheduler:
    """
    Manages scheduled tasks that need to run at specific intervals.
    """
    def __init__(self, check_interval: float = 1.0):
        """
        Initialize a scheduler.
        
        :param check_interval: How often to check schedules (seconds)
        """
        self.schedules: Dict[str, ScheduleEntry] = {}
        self.lock = threading.Lock()
        self.running = False
        self.thread = None
        self.check_interval = check_interval
        self.logger = default_logger
    
    def add_schedule(
        self,
        callback: Callable,
        interval_seconds: float,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        schedule_id: Optional[str] = None
    ) -> str:
        """
        Add a new schedule.
        
        :param callback: Function to call
        :param interval_seconds: Interval between executions
        :param args: Positional arguments for the callback
        :param kwargs: Keyword arguments for the callback
        :param schedule_id: Unique identifier (auto-generated if not provided)
        :return: Schedule ID
        """
        schedule_id = schedule_id or str(uuid.uuid4())
        
        with self.lock:
            if schedule_id in self.schedules:
                raise ValueError(f"Schedule with ID {schedule_id} already exists")
            
            entry = ScheduleEntry(
                schedule_id=schedule_id,
                interval_seconds=interval_seconds,
                callback=callback,
                args=args,
                kwargs=kwargs
            )
            
            self.schedules[schedule_id] = entry
            self.logger.info(f"Added schedule {schedule_id} with interval {interval_seconds}s")
        
        return schedule_id
    
    def remove_schedule(self, schedule_id: str) -> bool:
        """
        Remove a schedule.
        
        :param schedule_id: Schedule ID to remove
        :return: True if schedule was found and removed, False otherwise
        """
        with self.lock:
            if schedule_id not in self.schedules:
                return False
            
            del self.schedules[schedule_id]
            self.logger.info(f"Removed schedule {schedule_id}")
            return True
    
    def pause_schedule(self, schedule_id: str) -> bool:
        """
        Pause a schedule without removing it.
        
        :param schedule_id: Schedule ID to pause
        :return: True if schedule was found and paused, False otherwise
        """
        with self.lock:
            if schedule_id not in self.schedules:
                return False
            
            self.schedules[schedule_id].is_active = False
            self.logger.info(f"Paused schedule {schedule_id}")
            return True
    
    def resume_schedule(self, schedule_id: str) -> bool:
        """
        Resume a paused schedule.
        
        :param schedule_id: Schedule ID to resume
        :return: True if schedule was found and resumed, False otherwise
        """
        with self.lock:
            if schedule_id not in self.schedules:
                return False
            
            self.schedules[schedule_id].is_active = True
            self.logger.info(f"Resumed schedule {schedule_id}")
            return True
    
    def start(self):
        """
        Start the scheduler.
        """
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(
            target=self._run_loop,
            daemon=True
        )
        self.thread.start()
        self.logger.info("Scheduler started")
    
    def stop(self):
        """
        Stop the scheduler.
        """
        if not self.running:
            return
        
        self.running = False
        if self.thread:
            self.thread.join()
            self.thread = None
        self.logger.info("Scheduler stopped")
    
    def _run_loop(self):
        """
        Main scheduler loop.
        """
        while self.running:
            current_time = time.time()
            to_execute = []
            
            with self.lock:
                for schedule_id, entry in self.schedules.items():
                    if entry.should_run(current_time):
                        to_execute.append((schedule_id, entry))
                        entry.mark_run(current_time)
            
            for schedule_id, entry in to_execute:
                self._execute_schedule(schedule_id, entry)
            
            time.sleep(self.check_interval)
    
    def _execute_schedule(self, schedule_id: str, entry: ScheduleEntry):
        """
        Execute a scheduled task.
        
        :param schedule_id: Schedule ID
        :param entry: Schedule entry
        """
        try:
            thread = threading.Thread(
                target=entry.callback,
                args=entry.args,
                kwargs=entry.kwargs,
                daemon=True
            )
            thread.start()
            self.logger.info(f"Executed schedule {schedule_id}")
        except Exception as e:
            self.logger.error(f"Error executing schedule {schedule_id}: {str(e)}")
    
    def get_all_schedules(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all schedules.
        
        :return: Dictionary mapping schedule IDs to information
        """
        with self.lock:
            return {
                schedule_id: {
                    "interval": entry.interval_seconds,
                    "is_active": entry.is_active,
                    "last_run": entry.last_run
                }
                for schedule_id, entry in self.schedules.items()
            }