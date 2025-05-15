"""Node specialization management for the Render Farm Manager."""

import logging
import math
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

from render_farm_manager.core.interfaces import NodeSpecializationInterface
from render_farm_manager.core.models import (
    RenderJob,
    RenderJobStatus,
    RenderNode,
)
from render_farm_manager.utils.logging import AuditLogger, PerformanceMonitor


class NodeSpecializationManager(NodeSpecializationInterface):
    """
    Manager for matching rendering jobs to nodes based on specialization.
    
    This system optimizes rendering time by ensuring that jobs are executed on the
    most appropriate hardware based on job characteristics and historical performance.
    """
    
    def __init__(
        self,
        audit_logger: AuditLogger,
        performance_monitor: PerformanceMonitor,
        learning_rate: float = 0.2,
        history_weight: float = 0.3,
    ):
        """
        Initialize the node specialization manager.
        
        Args:
            audit_logger: Logger for audit trail events
            performance_monitor: Monitor for tracking manager performance
            learning_rate: Rate at which performance history is updated (0-1)
            history_weight: Weight given to historical performance vs. static matching
        """
        self.audit_logger = audit_logger
        self.performance_monitor = performance_monitor
        self.learning_rate = learning_rate
        self.history_weight = history_weight
        self.logger = logging.getLogger("render_farm.node_specialization")
        
        # Define job type to node specialization mappings
        self.job_type_specializations = {
            "animation": ["gpu_rendering"],
            "vfx": ["gpu_rendering", "high_memory"],
            "simulation": ["cpu_rendering", "simulation"],
            "lighting": ["gpu_rendering"],
            "compositing": ["cpu_rendering"],
            "texture_baking": ["gpu_rendering"],
            "cloth_sim": ["simulation", "physics"],
            "fluid_sim": ["simulation", "physics", "high_memory"],
            "scene_assembly": ["memory_intensive", "scene_assembly"],
            "character_rigging": ["cpu_rendering"],
            "motion_capture": ["cpu_rendering"],
        }
    
    def match_job_to_node(self, job: RenderJob, nodes: List[RenderNode]) -> Optional[str]:
        """
        Match a job to the most appropriate node based on job requirements and node capabilities.
        
        Args:
            job: The render job to match
            nodes: List of available render nodes
            
        Returns:
            ID of the matched node, or None if no suitable node is found
        """
        with self.performance_monitor.time_operation("match_job_to_node"):
            # Filter out nodes that don't meet basic requirements
            suitable_nodes = []
            for node in nodes:
                # Check if node is available
                if node.status != "online" or node.current_job_id is not None:
                    continue
                
                # Check GPU requirement
                if job.requires_gpu and (node.capabilities.gpu_count == 0 or not node.capabilities.gpu_model):
                    continue
                
                # Check memory requirement
                if job.memory_requirements_gb > node.capabilities.memory_gb:
                    continue
                
                # Check CPU requirement
                if job.cpu_requirements > node.capabilities.cpu_cores:
                    continue
                
                suitable_nodes.append(node)
            
            if not suitable_nodes:
                return None
            
            # Calculate performance scores for each suitable node
            node_scores: Dict[str, float] = {}
            for node in suitable_nodes:
                node_scores[node.id] = self.calculate_performance_score(job, node)
            
            # Pick the node with the highest score
            best_node_id = max(node_scores.items(), key=lambda x: x[1])[0]
            
            self.audit_logger.log_event(
                "job_node_matched",
                f"Job {job.id} ({job.job_type}) matched to node {best_node_id} with score {node_scores[best_node_id]:.2f}",
                job_id=job.id,
                node_id=best_node_id,
                job_type=job.job_type,
                score=node_scores[best_node_id],
            )
            
            return best_node_id
    
    def calculate_performance_score(self, job: RenderJob, node: RenderNode) -> float:
        """
        Calculate a performance score for a job on a specific node.
        
        Args:
            job: The render job to evaluate
            node: The render node to evaluate
            
        Returns:
            Performance score (higher is better)
        """
        # Base score starts at 1.0
        base_score = 1.0
        
        # Get specializations for this job type
        job_specializations = self.job_type_specializations.get(job.job_type, [])
        
        # Check for specialization match
        specialization_match = any(
            spec in node.capabilities.specialized_for for spec in job_specializations
        )
        
        if specialization_match:
            base_score *= 1.5
        
        # Add bonus for GPU capability if job requires it
        if job.requires_gpu and node.capabilities.gpu_count > 0:
            gpu_score = min(node.capabilities.gpu_count * job.scene_complexity / 5, 2.0)
            base_score *= (1.0 + gpu_score)
        
        # Add bonus for CPU capability
        cpu_score = min(
            node.capabilities.cpu_cores / job.cpu_requirements, 
            2.0
        ) - 1.0
        base_score *= (1.0 + (cpu_score * 0.5))
        
        # Add bonus for memory capacity
        memory_ratio = node.capabilities.memory_gb / job.memory_requirements_gb
        memory_score = min(memory_ratio, 3.0) - 1.0
        base_score *= (1.0 + (memory_score * 0.3))
        
        # Consider historical performance if available
        job_type_history_key = f"job_type:{job.job_type}"
        if job_type_history_key in node.performance_history:
            history_score = node.performance_history[job_type_history_key]
            
            # Blend historical score with base score
            combined_score = (
                (base_score * (1 - self.history_weight)) + 
                (history_score * self.history_weight)
            )
        else:
            combined_score = base_score
        
        return combined_score
    
    def update_performance_history(self, job: RenderJob, node: RenderNode, performance_metrics: Dict[str, float]) -> None:
        """
        Update performance history for a node based on completed job metrics.
        
        Args:
            job: The completed render job
            node: The render node that executed the job
            performance_metrics: Metrics about the job's performance
        """
        # Calculate a normalized performance score from metrics
        # Lower is better for metrics like render_time_per_frame
        if 'render_time_per_frame' in performance_metrics:
            # Normalize render time (lower is better, but score should be higher for better performance)
            # Assume 60 seconds per frame is a reference point
            reference_time = 60.0
            actual_time = performance_metrics['render_time_per_frame']
            
            if actual_time <= 0:
                actual_time = 0.1  # Avoid division by zero
            
            # Calculate score: higher value means better performance
            performance_score = reference_time / actual_time
            
            # Cap the score to a reasonable range
            performance_score = min(max(performance_score, 0.1), 10.0)
        else:
            # If no specific metrics are provided, use a generic positive score
            performance_score = 1.0
        
        # Update performance history for this job type
        job_type_key = f"job_type:{job.job_type}"
        
        if job_type_key in node.performance_history:
            # Update existing history with learning rate
            node.performance_history[job_type_key] = (
                (1 - self.learning_rate) * node.performance_history[job_type_key] +
                self.learning_rate * performance_score
            )
        else:
            # No history yet, set the initial value
            node.performance_history[job_type_key] = performance_score
        
        # Also track performance for specific job characteristics
        if job.requires_gpu:
            gpu_key = "requirement:gpu"
            if gpu_key in node.performance_history:
                node.performance_history[gpu_key] = (
                    (1 - self.learning_rate) * node.performance_history[gpu_key] +
                    self.learning_rate * performance_score
                )
            else:
                node.performance_history[gpu_key] = performance_score
        
        # Track performance based on memory usage
        memory_range_key = f"memory_range:{self._get_memory_range(job.memory_requirements_gb)}"
        if memory_range_key in node.performance_history:
            node.performance_history[memory_range_key] = (
                (1 - self.learning_rate) * node.performance_history[memory_range_key] +
                self.learning_rate * performance_score
            )
        else:
            node.performance_history[memory_range_key] = performance_score
        
        # Log the update
        self.audit_logger.log_event(
            "performance_history_updated",
            f"Performance history updated for node {node.id} with job {job.id} ({job.job_type}): score={performance_score:.2f}",
            job_id=job.id,
            node_id=node.id,
            job_type=job.job_type,
            performance_score=performance_score,
            metrics=performance_metrics,
        )
    
    def analyze_node_efficiency(self, nodes: List[RenderNode]) -> Dict[str, Dict[str, float]]:
        """
        Analyze node efficiency for different job types based on performance history.
        
        Args:
            nodes: List of render nodes
            
        Returns:
            Dictionary mapping node IDs to dictionaries of job types and efficiency scores
        """
        node_efficiency: Dict[str, Dict[str, float]] = {}
        
        for node in nodes:
            job_type_scores = {}
            
            # Extract job type scores from performance history
            for key, score in node.performance_history.items():
                if key.startswith("job_type:"):
                    job_type = key.split(":")[1]
                    job_type_scores[job_type] = score
            
            node_efficiency[node.id] = job_type_scores
        
        return node_efficiency
    
    def _get_memory_range(self, memory_gb: int) -> str:
        """
        Get a categorical range for memory requirements.
        
        Args:
            memory_gb: Memory requirement in GB
            
        Returns:
            String representing the memory range category
        """
        if memory_gb < 16:
            return "low"
        elif memory_gb < 64:
            return "medium"
        elif memory_gb < 256:
            return "high"
        else:
            return "extreme"