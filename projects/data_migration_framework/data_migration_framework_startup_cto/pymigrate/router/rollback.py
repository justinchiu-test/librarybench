"""Rollback management for traffic routing."""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import uuid4
import json

from pymigrate.models.service import RouteConfig

logger = logging.getLogger(__name__)


class RollbackManager:
    """Manages rollback capabilities for traffic routing."""
    
    def __init__(self):
        """Initialize rollback manager."""
        self._checkpoints: Dict[str, List[Dict[str, Any]]] = {}
        self._active_checkpoints: Dict[str, str] = {}
        
    async def create_checkpoint(
        self,
        service_name: str,
        route_config: RouteConfig,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a rollback checkpoint."""
        checkpoint_id = str(uuid4())
        
        checkpoint = {
            "id": checkpoint_id,
            "service_name": service_name,
            "timestamp": datetime.utcnow(),
            "route_config": route_config.model_dump(),
            "metadata": metadata or {}
        }
        
        # Store checkpoint
        if service_name not in self._checkpoints:
            self._checkpoints[service_name] = []
            
        self._checkpoints[service_name].append(checkpoint)
        
        # Keep only last 10 checkpoints per service
        if len(self._checkpoints[service_name]) > 10:
            self._checkpoints[service_name] = self._checkpoints[service_name][-10:]
            
        logger.info(
            f"Created checkpoint {checkpoint_id} for service {service_name} "
            f"at {route_config.percentage}% traffic"
        )
        
        return checkpoint_id
        
    async def get_rollback_config(
        self,
        service_name: str,
        checkpoint_id: Optional[str] = None
    ) -> Optional[RouteConfig]:
        """Get configuration for rollback."""
        checkpoints = self._checkpoints.get(service_name, [])
        
        if not checkpoints:
            return None
            
        if checkpoint_id:
            # Find specific checkpoint
            for checkpoint in checkpoints:
                if checkpoint["id"] == checkpoint_id:
                    return RouteConfig(**checkpoint["route_config"])
        else:
            # Get last stable checkpoint (before current)
            if len(checkpoints) >= 2:
                # Return second to last checkpoint
                checkpoint = checkpoints[-2]
                return RouteConfig(**checkpoint["route_config"])
            elif checkpoints:
                # Only one checkpoint, return it
                checkpoint = checkpoints[0]
                return RouteConfig(**checkpoint["route_config"])
                
        return None
        
    async def execute_rollback(
        self,
        service_name: str,
        checkpoint_id: Optional[str] = None,
        reason: str = "unspecified"
    ) -> Dict[str, Any]:
        """Execute a rollback to a previous checkpoint."""
        logger.warning(
            f"Executing rollback for service {service_name}, reason: {reason}"
        )
        
        rollback_config = await self.get_rollback_config(service_name, checkpoint_id)
        
        if not rollback_config:
            return {
                "success": False,
                "error": "No checkpoint found for rollback",
                "service": service_name
            }
            
        # Record rollback event
        rollback_event = {
            "timestamp": datetime.utcnow(),
            "service": service_name,
            "checkpoint_id": checkpoint_id,
            "reason": reason,
            "from_percentage": None,  # Would be current percentage
            "to_percentage": rollback_config.percentage
        }
        
        # In a real implementation, this would:
        # 1. Update the actual routing configuration
        # 2. Clear any caches
        # 3. Notify monitoring systems
        # 4. Log the rollback event
        
        return {
            "success": True,
            "service": service_name,
            "checkpoint_id": checkpoint_id or "latest",
            "new_config": rollback_config.model_dump(),
            "event": rollback_event
        }
        
    def get_checkpoint_history(
        self,
        service_name: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get checkpoint history for a service."""
        checkpoints = self._checkpoints.get(service_name, [])
        
        # Return most recent checkpoints
        return [
            {
                "id": cp["id"],
                "timestamp": cp["timestamp"].isoformat(),
                "traffic_percentage": cp["route_config"]["percentage"],
                "strategy": cp["route_config"]["strategy"],
                "metadata": cp["metadata"]
            }
            for cp in checkpoints[-limit:]
        ]
        
    async def create_rollback_plan(
        self,
        service_name: str,
        target_percentage: float,
        steps: int = 5
    ) -> List[Dict[str, Any]]:
        """Create a rollback plan with multiple steps."""
        current_config = await self.get_latest_checkpoint(service_name)
        
        if not current_config:
            return []
            
        current_percentage = current_config.percentage
        
        # Calculate step size
        step_size = (current_percentage - target_percentage) / steps
        
        plan = []
        for i in range(steps):
            percentage = current_percentage - (step_size * (i + 1))
            
            plan.append({
                "step": i + 1,
                "percentage": max(0, min(100, percentage)),
                "wait_seconds": 60 * (i + 1),  # Increasing wait times
                "health_check_required": True,
                "auto_rollback_on_failure": True
            })
            
        return plan
        
    async def get_latest_checkpoint(
        self,
        service_name: str
    ) -> Optional[RouteConfig]:
        """Get the latest checkpoint for a service."""
        checkpoints = self._checkpoints.get(service_name, [])
        
        if checkpoints:
            return RouteConfig(**checkpoints[-1]["route_config"])
            
        return None
        
    def mark_checkpoint_stable(
        self,
        service_name: str,
        checkpoint_id: str
    ) -> None:
        """Mark a checkpoint as stable."""
        checkpoints = self._checkpoints.get(service_name, [])
        
        for checkpoint in checkpoints:
            if checkpoint["id"] == checkpoint_id:
                checkpoint["metadata"]["stable"] = True
                checkpoint["metadata"]["marked_stable_at"] = datetime.utcnow().isoformat()
                logger.info(
                    f"Marked checkpoint {checkpoint_id} as stable for {service_name}"
                )
                break
                
    def get_stable_checkpoints(
        self,
        service_name: str
    ) -> List[Dict[str, Any]]:
        """Get all stable checkpoints for a service."""
        checkpoints = self._checkpoints.get(service_name, [])
        
        return [
            cp for cp in checkpoints
            if cp["metadata"].get("stable", False)
        ]
        
    async def export_checkpoints(
        self,
        service_name: Optional[str] = None
    ) -> str:
        """Export checkpoints as JSON."""
        if service_name:
            data = {service_name: self._checkpoints.get(service_name, [])}
        else:
            data = self._checkpoints
            
        # Convert datetime objects to strings
        def serialize(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj
            
        return json.dumps(data, default=serialize, indent=2)
        
    async def import_checkpoints(
        self,
        json_data: str
    ) -> None:
        """Import checkpoints from JSON."""
        data = json.loads(json_data)
        
        for service_name, checkpoints in data.items():
            # Convert string timestamps back to datetime
            for checkpoint in checkpoints:
                if isinstance(checkpoint["timestamp"], str):
                    checkpoint["timestamp"] = datetime.fromisoformat(
                        checkpoint["timestamp"]
                    )
                    
            self._checkpoints[service_name] = checkpoints
            
        logger.info(f"Imported checkpoints for {len(data)} services")