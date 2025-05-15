"""
Stakeholder Insight Manager - Tool for balancing diverse perspectives.

This module provides capabilities for:
- Stakeholder classification with organizational context
- Perspective recording with priority and influence weighting
- Conflict detection between competing stakeholder needs
- Consensus building support through overlap identification
- Integration of perspectives into decision-making processes
"""
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Union
from uuid import UUID
import json
import os
import math
import itertools

import numpy as np

from productmind.models import (
    Stakeholder,
    Perspective,
    StakeholderRelationship,
    StakeholderType,
    Priority
)


class StakeholderInsightManager:
    """
    Manager for recording and analyzing stakeholder perspectives.
    
    This class provides methods to:
    - Classify stakeholders and their organizational contexts
    - Record stakeholder perspectives with priority and influence
    - Detect conflicts between stakeholder needs
    - Support consensus building through overlap identification
    - Integrate stakeholder insights into decision-making
    """
    
    def __init__(self, storage_dir: str = "./data"):
        """
        Initialize the stakeholder insight manager.
        
        Args:
            storage_dir: Directory to store stakeholder data
        """
        self.storage_dir = storage_dir
        self._stakeholders_cache = {}
        self._perspectives_cache = {}
        self._relationships_cache = {}
        
        # Create storage directories
        os.makedirs(os.path.join(storage_dir, "stakeholders"), exist_ok=True)
        os.makedirs(os.path.join(storage_dir, "perspectives"), exist_ok=True)
        os.makedirs(os.path.join(storage_dir, "stakeholder_relationships"), exist_ok=True)
    
    def add_stakeholder(self, stakeholder: Union[Stakeholder, List[Stakeholder]]) -> List[str]:
        """
        Add a new stakeholder or list of stakeholders to the system.
        
        Args:
            stakeholder: Stakeholder or list of stakeholders to add
            
        Returns:
            List of stakeholder IDs
        """
        if isinstance(stakeholder, Stakeholder):
            stakeholder = [stakeholder]
        
        stakeholder_ids = []
        for item in stakeholder:
            self._store_stakeholder(item)
            stakeholder_ids.append(str(item.id))
        
        return stakeholder_ids
    
    def _store_stakeholder(self, stakeholder: Stakeholder) -> None:
        """
        Store a stakeholder in cache and on disk.
        
        Args:
            stakeholder: Stakeholder to store
        """
        # Store in memory cache
        self._stakeholders_cache[str(stakeholder.id)] = stakeholder
        
        # Store on disk
        stakeholder_path = os.path.join(
            self.storage_dir, "stakeholders", f"{stakeholder.id}.json"
        )
        with open(stakeholder_path, "w") as f:
            f.write(stakeholder.model_dump_json())
    
    def add_perspective(self, perspective: Union[Perspective, List[Perspective]]) -> List[str]:
        """
        Add a new perspective or list of perspectives to the system.
        
        Args:
            perspective: Perspective or list of perspectives to add
            
        Returns:
            List of perspective IDs
        """
        if isinstance(perspective, Perspective):
            perspective = [perspective]
        
        perspective_ids = []
        for item in perspective:
            self._store_perspective(item)
            
            # Update stakeholder with perspective ID
            stakeholder = self.get_stakeholder(str(item.stakeholder_id))
            if stakeholder:
                # Always store the UUID objects for perspective IDs in the stakeholder model
                if item.id not in stakeholder.perspectives:
                    stakeholder.perspectives.append(item.id)
                    self._store_stakeholder(stakeholder)
            
            perspective_ids.append(str(item.id))
        
        return perspective_ids
    
    def _store_perspective(self, perspective: Perspective) -> None:
        """
        Store a perspective in cache and on disk.
        
        Args:
            perspective: Perspective to store
        """
        # Store in memory cache
        self._perspectives_cache[str(perspective.id)] = perspective
        
        # Store on disk
        perspective_path = os.path.join(
            self.storage_dir, "perspectives", f"{perspective.id}.json"
        )
        with open(perspective_path, "w") as f:
            f.write(perspective.model_dump_json())
    
    def add_relationship(
        self, 
        relationship: Union[StakeholderRelationship, List[StakeholderRelationship]]
    ) -> List[str]:
        """
        Add a new stakeholder relationship or list of relationships to the system.
        
        Args:
            relationship: Relationship or list of relationships to add
            
        Returns:
            List of relationship IDs
        """
        if isinstance(relationship, StakeholderRelationship):
            relationship = [relationship]
        
        relationship_ids = []
        for item in relationship:
            self._store_relationship(item)
            relationship_ids.append(str(item.id))
        
        return relationship_ids
    
    def _store_relationship(self, relationship: StakeholderRelationship) -> None:
        """
        Store a stakeholder relationship in cache and on disk.
        
        Args:
            relationship: Stakeholder relationship to store
        """
        # Store in memory cache
        self._relationships_cache[str(relationship.id)] = relationship
        
        # Store on disk
        relationship_path = os.path.join(
            self.storage_dir, "stakeholder_relationships", f"{relationship.id}.json"
        )
        with open(relationship_path, "w") as f:
            f.write(relationship.model_dump_json())
    
    def get_stakeholder(self, stakeholder_id: Union[str, UUID]) -> Optional[Stakeholder]:
        """
        Retrieve a stakeholder by ID.

        Args:
            stakeholder_id: ID of the stakeholder to retrieve (string or UUID)

        Returns:
            Stakeholder if found, None otherwise
        """
        # Convert to string for consistent handling
        stakeholder_id_str = str(stakeholder_id)

        # Try to get from cache first
        if stakeholder_id_str in self._stakeholders_cache:
            return self._stakeholders_cache[stakeholder_id_str]

        # Try to load from disk
        stakeholder_path = os.path.join(
            self.storage_dir, "stakeholders", f"{stakeholder_id_str}.json"
        )
        if os.path.exists(stakeholder_path):
            with open(stakeholder_path, "r") as f:
                stakeholder_data = json.load(f)
                stakeholder = Stakeholder.model_validate(stakeholder_data)
                self._stakeholders_cache[stakeholder_id_str] = stakeholder
                return stakeholder

        return None
    
    def get_perspective(self, perspective_id: Union[str, UUID]) -> Optional[Perspective]:
        """
        Retrieve a perspective by ID.

        Args:
            perspective_id: ID of the perspective to retrieve (string or UUID)

        Returns:
            Perspective if found, None otherwise
        """
        # Convert to string for consistent handling
        perspective_id_str = str(perspective_id)

        # Try to get from cache first
        if perspective_id_str in self._perspectives_cache:
            return self._perspectives_cache[perspective_id_str]

        # Try to load from disk
        perspective_path = os.path.join(
            self.storage_dir, "perspectives", f"{perspective_id_str}.json"
        )
        if os.path.exists(perspective_path):
            with open(perspective_path, "r") as f:
                perspective_data = json.load(f)
                perspective = Perspective.model_validate(perspective_data)
                self._perspectives_cache[perspective_id_str] = perspective
                return perspective

        return None
    
    def get_relationship(self, relationship_id: Union[str, UUID]) -> Optional[StakeholderRelationship]:
        """
        Retrieve a stakeholder relationship by ID.

        Args:
            relationship_id: ID of the relationship to retrieve (string or UUID)

        Returns:
            Stakeholder relationship if found, None otherwise
        """
        # Convert to string for consistent handling
        relationship_id_str = str(relationship_id)

        # Try to get from cache first
        if relationship_id_str in self._relationships_cache:
            return self._relationships_cache[relationship_id_str]

        # Try to load from disk
        relationship_path = os.path.join(
            self.storage_dir, "stakeholder_relationships", f"{relationship_id_str}.json"
        )
        if os.path.exists(relationship_path):
            with open(relationship_path, "r") as f:
                relationship_data = json.load(f)
                relationship = StakeholderRelationship.model_validate(relationship_data)
                self._relationships_cache[relationship_id_str] = relationship
                return relationship

        return None
    
    def get_all_stakeholders(self) -> List[Stakeholder]:
        """
        Retrieve all stakeholders.
        
        Returns:
            List of all stakeholders
        """
        stakeholders = []
        stakeholders_dir = os.path.join(self.storage_dir, "stakeholders")
        
        if not os.path.exists(stakeholders_dir):
            return stakeholders
        
        for filename in os.listdir(stakeholders_dir):
            if filename.endswith(".json"):
                stakeholder_id = filename.replace(".json", "")
                stakeholder = self.get_stakeholder(stakeholder_id)
                if stakeholder:
                    stakeholders.append(stakeholder)
        
        return stakeholders
    
    def get_all_perspectives(self) -> List[Perspective]:
        """
        Retrieve all perspectives.
        
        Returns:
            List of all perspectives
        """
        perspectives = []
        perspectives_dir = os.path.join(self.storage_dir, "perspectives")
        
        if not os.path.exists(perspectives_dir):
            return perspectives
        
        for filename in os.listdir(perspectives_dir):
            if filename.endswith(".json"):
                perspective_id = filename.replace(".json", "")
                perspective = self.get_perspective(perspective_id)
                if perspective:
                    perspectives.append(perspective)
        
        return perspectives
    
    def get_all_relationships(self) -> List[StakeholderRelationship]:
        """
        Retrieve all stakeholder relationships.
        
        Returns:
            List of all stakeholder relationships
        """
        relationships = []
        relationships_dir = os.path.join(self.storage_dir, "stakeholder_relationships")
        
        if not os.path.exists(relationships_dir):
            return relationships
        
        for filename in os.listdir(relationships_dir):
            if filename.endswith(".json"):
                relationship_id = filename.replace(".json", "")
                relationship = self.get_relationship(relationship_id)
                if relationship:
                    relationships.append(relationship)
        
        return relationships
    
    def get_stakeholder_perspectives(self, stakeholder_id: str) -> List[Perspective]:
        """
        Get all perspectives for a stakeholder.
        
        Args:
            stakeholder_id: ID of the stakeholder
            
        Returns:
            List of perspectives for the stakeholder
        """
        stakeholder = self.get_stakeholder(stakeholder_id)
        if not stakeholder:
            return []
        
        perspectives = []
        for pid in stakeholder.perspectives:
            # Convert UUID to string if necessary
            perspective_id = str(pid)
            perspective = self.get_perspective(perspective_id)
            if perspective:
                perspectives.append(perspective)

        return perspectives
    
    def get_perspectives_by_topic(self, topic: str) -> List[Perspective]:
        """
        Get all perspectives on a specific topic.
        
        Args:
            topic: Topic to filter by
            
        Returns:
            List of perspectives on the topic
        """
        all_perspectives = self.get_all_perspectives()
        return [p for p in all_perspectives if p.topic.lower() == topic.lower()]
    
    def get_stakeholder_relationships(self, stakeholder_id: str) -> List[Dict]:
        """
        Get all relationships for a stakeholder.
        
        Args:
            stakeholder_id: ID of the stakeholder
            
        Returns:
            List of relationships with stakeholder details
        """
        all_relationships = self.get_all_relationships()
        stakeholder_relationships = []
        
        for relationship in all_relationships:
            if str(relationship.stakeholder1_id) == stakeholder_id or str(relationship.stakeholder2_id) == stakeholder_id:
                # Get the other stakeholder in the relationship
                other_stakeholder_id = str(relationship.stakeholder2_id) if str(relationship.stakeholder1_id) == stakeholder_id else str(relationship.stakeholder1_id)
                other_stakeholder = self.get_stakeholder(other_stakeholder_id)
                
                if other_stakeholder:
                    stakeholder_relationships.append({
                        "relationship_id": str(relationship.id),
                        "relationship_type": relationship.relationship_type,
                        "alignment_level": relationship.alignment_level,
                        "notes": relationship.notes,
                        "stakeholder": {
                            "id": other_stakeholder_id,
                            "name": other_stakeholder.name,
                            "title": other_stakeholder.title,
                            "department": other_stakeholder.department,
                            "type": other_stakeholder.type
                        }
                    })
        
        return stakeholder_relationships
    
    def detect_conflicts(self, topic: Optional[str] = None) -> List[Dict]:
        """
        Detect conflicting perspectives between stakeholders.
        
        Args:
            topic: Topic to filter by (if None, check all topics)
            
        Returns:
            List of conflicts with stakeholder details
        """
        # Get all perspectives
        all_perspectives = self.get_all_perspectives()
        
        # Filter by topic if provided
        if topic:
            perspectives = [p for p in all_perspectives if p.topic.lower() == topic.lower()]
        else:
            perspectives = all_perspectives
        
        # Group perspectives by topic
        perspectives_by_topic = defaultdict(list)
        for perspective in perspectives:
            perspectives_by_topic[perspective.topic].append(perspective)
        
        # Detect conflicts by topic
        conflicts = []
        
        for topic, topic_perspectives in perspectives_by_topic.items():
            # Need at least 2 perspectives to have a conflict
            if len(topic_perspectives) < 2:
                continue
            
            # Check all pairs of perspectives for conflicts
            for p1, p2 in itertools.combinations(topic_perspectives, 2):
                stakeholder1 = self.get_stakeholder(p1.stakeholder_id)
                stakeholder2 = self.get_stakeholder(p2.stakeholder_id)
                
                if not stakeholder1 or not stakeholder2:
                    continue
                
                # Check if perspectives agree
                agreement_level = p1.agreement_level * p2.agreement_level
                
                # If agreement level is low, consider it a conflict
                if agreement_level < 0.5:
                    # Calculate the weighted importance of the conflict
                    importance = (
                        p1.influence_level * stakeholder1.influence_level * 
                        self._priority_to_value(p1.priority) +
                        p2.influence_level * stakeholder2.influence_level * 
                        self._priority_to_value(p2.priority)
                    )
                    
                    conflicts.append({
                        "topic": topic,
                        "stakeholder1": {
                            "id": str(stakeholder1.id),
                            "name": stakeholder1.name,
                            "type": stakeholder1.type,
                            "department": stakeholder1.department,
                            "influence": stakeholder1.influence_level,
                            "perspective_id": str(p1.id),
                            "perspective_priority": p1.priority,
                            "perspective_influence": p1.influence_level
                        },
                        "stakeholder2": {
                            "id": str(stakeholder2.id),
                            "name": stakeholder2.name,
                            "type": stakeholder2.type,
                            "department": stakeholder2.department,
                            "influence": stakeholder2.influence_level,
                            "perspective_id": str(p2.id),
                            "perspective_priority": p2.priority,
                            "perspective_influence": p2.influence_level
                        },
                        "agreement_level": agreement_level,
                        "importance": importance
                    })
        
        # Sort conflicts by importance (descending)
        conflicts.sort(key=lambda x: x["importance"], reverse=True)
        
        return conflicts
    
    def _priority_to_value(self, priority: Priority) -> float:
        """
        Convert priority enum to numeric value.
        
        Args:
            priority: Priority enum value
            
        Returns:
            Numeric value for priority
        """
        priority_values = {
            Priority.CRITICAL: 4.0,
            Priority.HIGH: 3.0,
            Priority.MEDIUM: 2.0,
            Priority.LOW: 1.0
        }
        return priority_values.get(priority, 1.0)
    
    def identify_consensus(self, topic: str) -> Dict:
        """
        Identify areas of consensus on a topic.
        
        Args:
            topic: Topic to analyze
            
        Returns:
            Dictionary with consensus analysis
        """
        # Get perspectives on the topic
        perspectives = self.get_perspectives_by_topic(topic)
        
        if not perspectives:
            return {
                "topic": topic,
                "perspectives_count": 0,
                "average_agreement": 0.0,
                "consensus_level": 0.0,
                "stakeholders": []
            }
        
        # Calculate average agreement level
        agreement_levels = [p.agreement_level for p in perspectives]
        avg_agreement = sum(agreement_levels) / len(agreement_levels)
        
        # Calculate consensus level (higher when agreement levels are similar)
        if len(agreement_levels) > 1:
            std_dev = np.std(agreement_levels)
            consensus_level = 1.0 - (std_dev / 1.0)  # Normalized to 0-1
            consensus_level = max(0.0, min(consensus_level, 1.0))  # Clamp to 0-1
        else:
            consensus_level = 1.0
        
        # Get stakeholder details
        stakeholders_analysis = []
        for perspective in perspectives:
            stakeholder = self.get_stakeholder(perspective.stakeholder_id)
            if stakeholder:
                weighted_influence = perspective.influence_level * stakeholder.influence_level
                stakeholders_analysis.append({
                    "stakeholder_id": str(stakeholder.id),
                    "name": stakeholder.name,
                    "type": stakeholder.type,
                    "department": stakeholder.department,
                    "agreement_level": perspective.agreement_level,
                    "influence_level": stakeholder.influence_level,
                    "perspective_influence": perspective.influence_level,
                    "weighted_influence": weighted_influence,
                    "priority": perspective.priority
                })
        
        # Sort by weighted influence
        stakeholders_analysis.sort(key=lambda x: x["weighted_influence"], reverse=True)
        
        return {
            "topic": topic,
            "perspectives_count": len(perspectives),
            "average_agreement": avg_agreement,
            "consensus_level": consensus_level,
            "stakeholders": stakeholders_analysis
        }
    
    def integrate_perspectives(
        self, 
        topic: str, 
        weighting_strategy: str = "influence"
    ) -> Dict:
        """
        Integrate perspectives on a topic for decision making.
        
        Args:
            topic: Topic to analyze
            weighting_strategy: Strategy for weighting perspectives
                                ("influence", "priority", "balanced")
            
        Returns:
            Dictionary with integrated perspective
        """
        # Get perspectives on the topic
        perspectives = self.get_perspectives_by_topic(topic)
        
        if not perspectives:
            return {
                "topic": topic,
                "perspectives_count": 0,
                "agreement_summary": {"average": 0, "min": 0, "max": 0},
                "integrated_value": 0.0,
                "confidence": 0.0,
                "stakeholder_perspectives": []
            }
        
        # Get stakeholder details and calculate weights
        stakeholder_perspectives = []
        total_weight = 0.0
        weighted_agreement_sum = 0.0
        
        for perspective in perspectives:
            stakeholder = self.get_stakeholder(perspective.stakeholder_id)
            if not stakeholder:
                continue
                
            # Calculate weight based on strategy
            if weighting_strategy == "influence":
                weight = perspective.influence_level * stakeholder.influence_level
            elif weighting_strategy == "priority":
                weight = self._priority_to_value(perspective.priority)
            else:  # balanced
                weight = (
                    (perspective.influence_level * stakeholder.influence_level) +
                    self._priority_to_value(perspective.priority)
                ) / 2
            
            total_weight += weight
            weighted_agreement_sum += perspective.agreement_level * weight
            
            stakeholder_perspectives.append({
                "stakeholder_id": str(stakeholder.id),
                "name": stakeholder.name,
                "type": stakeholder.type,
                "agreement_level": perspective.agreement_level,
                "weight": weight,
                "priority": perspective.priority,
                "perspective_id": str(perspective.id)
            })
        
        # Calculate integrated agreement value
        integrated_value = weighted_agreement_sum / total_weight if total_weight > 0 else 0.0
        
        # Calculate confidence based on perspective count and variance
        agreement_levels = [p.agreement_level for p in perspectives]
        agreement_min = min(agreement_levels) if agreement_levels else 0
        agreement_max = max(agreement_levels) if agreement_levels else 0
        agreement_std = np.std(agreement_levels) if len(agreement_levels) > 1 else 0
        
        # Higher confidence with more perspectives and lower variance
        perspective_count_factor = min(1.0, len(perspectives) / 10.0)  # Max out at 10 perspectives
        variance_factor = 1.0 - (agreement_std / 1.0)  # Lower variance gives higher factor
        
        confidence = (perspective_count_factor + variance_factor) / 2.0
        
        # Sort stakeholder perspectives by weight
        stakeholder_perspectives.sort(key=lambda x: x["weight"], reverse=True)
        
        return {
            "topic": topic,
            "perspectives_count": len(perspectives),
            "agreement_summary": {
                "average": sum(agreement_levels) / len(agreement_levels) if agreement_levels else 0,
                "min": agreement_min,
                "max": agreement_max,
                "std_dev": agreement_std
            },
            "integrated_value": integrated_value,
            "confidence": confidence,
            "stakeholder_perspectives": stakeholder_perspectives
        }
    
    def generate_stakeholder_map(self) -> Dict:
        """
        Generate a stakeholder map showing relationships and influence.
        
        Returns:
            Dictionary with stakeholder map data
        """
        stakeholders = self.get_all_stakeholders()
        relationships = self.get_all_relationships()
        
        if not stakeholders:
            return {"nodes": [], "links": []}
        
        # Create nodes
        nodes = []
        for stakeholder in stakeholders:
            nodes.append({
                "id": str(stakeholder.id),
                "name": stakeholder.name,
                "department": stakeholder.department,
                "type": stakeholder.type,
                "influence": stakeholder.influence_level
            })
        
        # Create links
        links = []
        for relationship in relationships:
            links.append({
                "source": str(relationship.stakeholder1_id),
                "target": str(relationship.stakeholder2_id),
                "type": relationship.relationship_type,
                "alignment": relationship.alignment_level
            })
        
        # Group nodes by department
        departments = defaultdict(list)
        for node in nodes:
            departments[node["department"]].append(node["id"])
        
        # Group nodes by stakeholder type
        types = defaultdict(list)
        for node in nodes:
            types[node["type"]].append(node["id"])
        
        return {
            "nodes": nodes,
            "links": links,
            "departments": [
                {"name": dept, "stakeholders": stakeholders}
                for dept, stakeholders in departments.items()
            ],
            "types": [
                {"type": stype, "stakeholders": stakeholders}
                for stype, stakeholders in types.items()
            ]
        }
    
    def analyze_stakeholder_influence(self) -> Dict:
        """
        Analyze stakeholder influence by type and department.
        
        Returns:
            Dictionary with influence analysis
        """
        stakeholders = self.get_all_stakeholders()
        
        if not stakeholders:
            return {
                "total_stakeholders": 0,
                "influence_by_type": {},
                "influence_by_department": {},
                "stakeholders_by_influence": []
            }
        
        # Calculate influence by type
        influence_by_type = defaultdict(list)
        for stakeholder in stakeholders:
            influence_by_type[stakeholder.type].append(stakeholder.influence_level)
        
        type_influence = {}
        for stype, influences in influence_by_type.items():
            type_influence[stype] = {
                "count": len(influences),
                "total_influence": sum(influences),
                "average_influence": sum(influences) / len(influences),
                "min_influence": min(influences),
                "max_influence": max(influences)
            }
        
        # Calculate influence by department
        influence_by_dept = defaultdict(list)
        for stakeholder in stakeholders:
            influence_by_dept[stakeholder.department].append(stakeholder.influence_level)
        
        dept_influence = {}
        for dept, influences in influence_by_dept.items():
            dept_influence[dept] = {
                "count": len(influences),
                "total_influence": sum(influences),
                "average_influence": sum(influences) / len(influences),
                "min_influence": min(influences),
                "max_influence": max(influences)
            }
        
        # Sort stakeholders by influence
        stakeholders_by_influence = [
            {
                "id": str(s.id),
                "name": s.name,
                "title": s.title,
                "department": s.department,
                "type": s.type,
                "influence": s.influence_level
            }
            for s in sorted(stakeholders, key=lambda s: s.influence_level, reverse=True)
        ]
        
        return {
            "total_stakeholders": len(stakeholders),
            "influence_by_type": type_influence,
            "influence_by_department": dept_influence,
            "stakeholders_by_influence": stakeholders_by_influence
        }
    
    def generate_stakeholder_matrix(self) -> Dict:
        """
        Generate a power/interest stakeholder matrix.
        
        Returns:
            Dictionary with stakeholder matrix data
        """
        stakeholders = self.get_all_stakeholders()
        perspectives = self.get_all_perspectives()
        
        if not stakeholders:
            return {
                "high_power_high_interest": [],
                "high_power_low_interest": [],
                "low_power_high_interest": [],
                "low_power_low_interest": []
            }
        
        # Calculate interest level based on number and priority of perspectives
        interest_levels = {}
        
        for stakeholder in stakeholders:
            # Get stakeholder perspectives
            stakeholder_perspectives = [
                p for p in perspectives 
                if str(p.stakeholder_id) == str(stakeholder.id)
            ]
            
            if not stakeholder_perspectives:
                interest_level = 0.5  # Default interest level
            else:
                # Calculate weighted interest level
                total_weight = 0
                weighted_sum = 0
                
                for perspective in stakeholder_perspectives:
                    weight = self._priority_to_value(perspective.priority)
                    total_weight += weight
                    weighted_sum += weight * 1.0  # Each perspective indicates interest
                
                interest_level = weighted_sum / total_weight if total_weight > 0 else 0.5
            
            interest_levels[str(stakeholder.id)] = interest_level
        
        # Classify stakeholders into matrix quadrants
        high_power_high_interest = []
        high_power_low_interest = []
        low_power_high_interest = []
        low_power_low_interest = []
        
        for stakeholder in stakeholders:
            sid = str(stakeholder.id)
            power = stakeholder.influence_level
            interest = interest_levels[sid]
            
            stakeholder_info = {
                "id": sid,
                "name": stakeholder.name,
                "title": stakeholder.title,
                "department": stakeholder.department,
                "type": stakeholder.type,
                "power": power,
                "interest": interest
            }
            
            # Classify based on power and interest levels
            if power >= 0.5 and interest >= 0.5:
                high_power_high_interest.append(stakeholder_info)
            elif power >= 0.5 and interest < 0.5:
                high_power_low_interest.append(stakeholder_info)
            elif power < 0.5 and interest >= 0.5:
                low_power_high_interest.append(stakeholder_info)
            else:
                low_power_low_interest.append(stakeholder_info)
        
        return {
            "high_power_high_interest": high_power_high_interest,
            "high_power_low_interest": high_power_low_interest,
            "low_power_high_interest": low_power_high_interest,
            "low_power_low_interest": low_power_low_interest
        }
    
    def analyze_perspective_alignment(self, topic: Optional[str] = None) -> Dict:
        """
        Analyze alignment of perspectives across stakeholders.
        
        Args:
            topic: Topic to filter by (if None, analyze all topics)
            
        Returns:
            Dictionary with alignment analysis
        """
        perspectives = self.get_all_perspectives()
        
        # Filter by topic if provided
        if topic:
            perspectives = [p for p in perspectives if p.topic.lower() == topic.lower()]
        
        if not perspectives:
            return {
                "topics": [],
                "overall_alignment": 0.0,
                "topics_alignment": {},
                "stakeholder_agreement": {}
            }
        
        # Group perspectives by topic
        topics = {}
        topics_perspectives = defaultdict(list)
        
        for perspective in perspectives:
            topics_perspectives[perspective.topic].append(perspective)
            
            if perspective.topic not in topics:
                topics[perspective.topic] = {
                    "perspective_count": 0,
                    "total_agreement": 0.0,
                    "stakeholders": set()
                }
            
            topics[perspective.topic]["perspective_count"] += 1
            topics[perspective.topic]["total_agreement"] += perspective.agreement_level
            topics[perspective.topic]["stakeholders"].add(str(perspective.stakeholder_id))
        
        # Calculate alignment by topic
        topics_alignment = {}
        for topic, data in topics.items():
            if data["perspective_count"] > 0:
                avg_agreement = data["total_agreement"] / data["perspective_count"]
                topics_alignment[topic] = {
                    "perspective_count": data["perspective_count"],
                    "stakeholder_count": len(data["stakeholders"]),
                    "average_agreement": avg_agreement
                }
        
        # Calculate stakeholder agreement
        stakeholder_agreement = {}
        for perspective in perspectives:
            sid = str(perspective.stakeholder_id)
            if sid not in stakeholder_agreement:
                stakeholder_agreement[sid] = {
                    "perspective_count": 0,
                    "total_agreement": 0.0,
                    "topics": set()
                }
            
            stakeholder_agreement[sid]["perspective_count"] += 1
            stakeholder_agreement[sid]["total_agreement"] += perspective.agreement_level
            stakeholder_agreement[sid]["topics"].add(perspective.topic)
        
        # Calculate average agreement by stakeholder
        stakeholder_avg_agreement = {}
        for sid, data in stakeholder_agreement.items():
            stakeholder = self.get_stakeholder(sid)
            if stakeholder and data["perspective_count"] > 0:
                avg_agreement = data["total_agreement"] / data["perspective_count"]
                stakeholder_avg_agreement[sid] = {
                    "name": stakeholder.name,
                    "department": stakeholder.department,
                    "type": stakeholder.type,
                    "average_agreement": avg_agreement,
                    "perspective_count": data["perspective_count"],
                    "topics_count": len(data["topics"])
                }
        
        # Calculate overall alignment
        total_agreement = sum(p.agreement_level for p in perspectives)
        overall_alignment = total_agreement / len(perspectives) if perspectives else 0.0
        
        return {
            "topics": list(topics_alignment.keys()),
            "overall_alignment": overall_alignment,
            "topics_alignment": topics_alignment,
            "stakeholder_agreement": stakeholder_avg_agreement
        }