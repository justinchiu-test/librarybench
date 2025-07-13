"""Tick rate management for game server"""

import asyncio
import time
from typing import Callable, Optional, List
from pydantic import BaseModel, Field


class TickManager(BaseModel):
    """Manages game server tick rate"""
    target_tick_rate: int = Field(60, description="Target ticks per second")
    tick_interval: float = Field(description="Seconds between ticks")
    current_tick: int = Field(0, description="Current tick number")
    last_tick_time: float = Field(default_factory=time.time)
    running: bool = Field(False)
    tick_callbacks: List[Callable] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if "tick_interval" not in data:
            data["tick_interval"] = 1.0 / data.get("target_tick_rate", 60)
        super().__init__(**data)
    
    def add_callback(self, callback: Callable):
        """Add a callback to be called on each tick"""
        if callback not in self.tick_callbacks:
            self.tick_callbacks.append(callback)
    
    def remove_callback(self, callback: Callable):
        """Remove a tick callback"""
        if callback in self.tick_callbacks:
            self.tick_callbacks.remove(callback)
    
    async def start(self):
        """Start the tick manager"""
        self.running = True
        self.last_tick_time = time.time()
        asyncio.create_task(self._tick_loop())
    
    async def stop(self):
        """Stop the tick manager"""
        self.running = False
    
    async def _tick_loop(self):
        """Main tick loop"""
        while self.running:
            start_time = time.time()
            
            # Calculate delta time
            delta_time = start_time - self.last_tick_time
            self.last_tick_time = start_time
            
            # Execute tick callbacks
            for callback in self.tick_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(self.current_tick, delta_time)
                    else:
                        callback(self.current_tick, delta_time)
                except Exception:
                    pass  # Continue even if callback fails
            
            # Increment tick
            self.current_tick += 1
            
            # Calculate sleep time to maintain tick rate
            elapsed = time.time() - start_time
            sleep_time = max(0, self.tick_interval - elapsed)
            
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
    
    def get_tick_rate(self) -> float:
        """Get current actual tick rate"""
        if self.current_tick == 0:
            return 0.0
        
        total_time = time.time() - self.last_tick_time
        return self.current_tick / total_time if total_time > 0 else 0.0
    
    def get_tick_stats(self) -> dict:
        """Get tick statistics"""
        return {
            "current_tick": self.current_tick,
            "target_tick_rate": self.target_tick_rate,
            "actual_tick_rate": self.get_tick_rate(),
            "tick_interval": self.tick_interval,
            "running": self.running
        }