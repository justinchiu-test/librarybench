"""
Data Engineer domain-specific Scheduler wrapping the unified core.
"""
from scheduler.scheduler import Scheduler as CoreScheduler

class Scheduler(CoreScheduler):
    def __init__(self, persist_path=None, leader_lock_file=None):
        super().__init__(persist_path=persist_path, leader_lock_file=leader_lock_file)