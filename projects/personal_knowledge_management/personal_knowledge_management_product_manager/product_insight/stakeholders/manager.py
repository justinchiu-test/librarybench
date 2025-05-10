"""
Stakeholder management module for ProductInsight.

This module provides functionality for managing stakeholders, their perspectives,
and relationships.
"""

from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Union
from uuid import UUID

from pydantic import BaseModel, Field

from product_insight.models import (
    Feature,
    InfluenceEnum,
    SentimentEnum,
    Stakeholder,
    StakeholderPerspective,
    StakeholderRoleEnum,
    StrategicObjective,
)
from product_insight.storage import FileStorage, StorageInterface


class StakeholderQuery(BaseModel):
    """Query parameters for searching stakeholders."""
    
    text: Optional[str] = None
    roles: List[StakeholderRoleEnum] = Field(default_factory=list)
    influence_levels: List[InfluenceEnum] = Field(default_factory=list)
    feature_ids: List[UUID] = Field(default_factory=list)
    objective_ids: List[UUID] = Field(default_factory=list)
    limit: int = 50


class StakeholderGroup(BaseModel):
    """Group of stakeholders with common characteristics."""
    
    name: str
    description: Optional[str] = None
    stakeholder_ids: List[UUID] = Field(default_factory=list)


class StakeholderAlignment(BaseModel):
    """Alignment of stakeholders with objectives or features."""
    
    stakeholder_id: UUID
    stakeholder_name: str
    alignment_scores: Dict[str, float] = Field(default_factory=dict)
    overall_alignment: float = 0.0


class StakeholderNetwork(BaseModel):
    """Network of stakeholder relationships."""
    
    nodes: List[Dict] = Field(default_factory=list)
    links: List[Dict] = Field(default_factory=list)


class StakeholderManager:
    """Manages stakeholders and their perspectives."""
    
    def __init__(
        self,
        storage_dir: str,
        stakeholder_storage: Optional[StorageInterface[Stakeholder]] = None,
        perspective_storage: Optional[StorageInterface[StakeholderPerspective]] = None,
        feature_storage: Optional[StorageInterface[Feature]] = None,
        objective_storage: Optional[StorageInterface[StrategicObjective]] = None,
    ):
        """Initialize the stakeholder manager.
        
        Args:
            storage_dir: Base directory for storing stakeholder data
            stakeholder_storage: Optional custom storage for stakeholders
            perspective_storage: Optional custom storage for stakeholder perspectives
            feature_storage: Optional custom storage for features
            objective_storage: Optional custom storage for objectives
        """
        self.stakeholder_storage = stakeholder_storage or FileStorage(
            entity_type=Stakeholder,
            storage_dir=f"{storage_dir}/stakeholders",
            format="json"
        )
        
        self.perspective_storage = perspective_storage or FileStorage(
            entity_type=StakeholderPerspective,
            storage_dir=f"{storage_dir}/stakeholder_perspectives",
            format="json"
        )
        
        self.feature_storage = feature_storage or FileStorage(
            entity_type=Feature,
            storage_dir=f"{storage_dir}/features",
            format="json"
        )
        
        self.objective_storage = objective_storage or FileStorage(
            entity_type=StrategicObjective,
            storage_dir=f"{storage_dir}/objectives",
            format="json"
        )
    
    def add_stakeholder(self, stakeholder: Stakeholder) -> Stakeholder:
        """Add a new stakeholder.
        
        Args:
            stakeholder: Stakeholder to add
            
        Returns:
            Added stakeholder
        """
        return self.stakeholder_storage.save(stakeholder)
    
    def update_stakeholder(self, stakeholder: Stakeholder) -> Stakeholder:
        """Update an existing stakeholder.
        
        Args:
            stakeholder: Stakeholder to update
            
        Returns:
            Updated stakeholder
        """
        return self.stakeholder_storage.save(stakeholder)
    
    def get_stakeholder(self, stakeholder_id: UUID) -> Stakeholder:
        """Get a stakeholder by ID.
        
        Args:
            stakeholder_id: ID of the stakeholder to get
            
        Returns:
            Stakeholder
        """
        return self.stakeholder_storage.get(stakeholder_id)
    
    def delete_stakeholder(self, stakeholder_id: UUID) -> bool:
        """Delete a stakeholder.
        
        Args:
            stakeholder_id: ID of the stakeholder to delete
            
        Returns:
            True if the stakeholder was deleted, False otherwise
        """
        # Delete associated perspectives
        try:
            perspectives = self.perspective_storage.list()
            for perspective in perspectives:
                if perspective.stakeholder_id == stakeholder_id:
                    self.perspective_storage.delete(perspective.id)
        except Exception as e:
            print(f"Error deleting stakeholder perspectives: {e}")
        
        # Delete the stakeholder
        return self.stakeholder_storage.delete(stakeholder_id)
    
    def search_stakeholders(self, query: StakeholderQuery) -> List[Stakeholder]:
        """Search for stakeholders matching the query.
        
        Args:
            query: Search parameters
            
        Returns:
            List of matching stakeholders
        """
        all_stakeholders = self.stakeholder_storage.list()
        matching_stakeholders = []
        
        for stakeholder in all_stakeholders:
            # Apply filters
            
            # Text search
            if query.text:
                text_lower = query.text.lower()
                if not (
                    text_lower in stakeholder.name.lower() or
                    (stakeholder.organization and text_lower in stakeholder.organization.lower()) or
                    (stakeholder.notes and text_lower in stakeholder.notes.lower()) or
                    any(text_lower in concern.lower() for concern in stakeholder.key_concerns)
                ):
                    continue
            
            # Role filter
            if query.roles and stakeholder.role not in query.roles:
                continue
            
            # Influence filter
            if query.influence_levels and stakeholder.influence not in query.influence_levels:
                continue
            
            # Feature filter
            if query.feature_ids and not any(fid in stakeholder.feature_preferences for fid in query.feature_ids):
                continue
            
            # Objective filter
            if query.objective_ids and not any(oid in stakeholder.objective_alignment for oid in query.objective_ids):
                continue
            
            matching_stakeholders.append(stakeholder)
        
        # Sort by influence and name
        matching_stakeholders.sort(
            key=lambda s: (
                -self._influence_to_value(s.influence),
                s.name
            )
        )
        
        return matching_stakeholders[:query.limit]
    
    def _influence_to_value(self, influence: InfluenceEnum) -> int:
        """Convert influence level to a numeric value for sorting."""
        values = {
            InfluenceEnum.HIGH: 3,
            InfluenceEnum.MEDIUM: 2,
            InfluenceEnum.LOW: 1
        }
        return values.get(influence, 0)
    
    def add_stakeholder_perspective(
        self, perspective: StakeholderPerspective
    ) -> StakeholderPerspective:
        """Add a new stakeholder perspective.
        
        Args:
            perspective: Stakeholder perspective to add
            
        Returns:
            Added stakeholder perspective
        """
        # Verify the stakeholder exists
        self.stakeholder_storage.get(perspective.stakeholder_id)
        
        # Add the perspective
        return self.perspective_storage.save(perspective)
    
    def get_stakeholder_perspectives(
        self, stakeholder_id: UUID
    ) -> List[StakeholderPerspective]:
        """Get all perspectives for a stakeholder.
        
        Args:
            stakeholder_id: ID of the stakeholder
            
        Returns:
            List of stakeholder perspectives
        """
        all_perspectives = self.perspective_storage.list()
        
        # Filter and sort by date (newest first)
        perspectives = [
            p for p in all_perspectives if p.stakeholder_id == stakeholder_id
        ]
        perspectives.sort(key=lambda p: p.date_recorded, reverse=True)
        
        return perspectives
    
    def get_perspectives_on_feature(
        self, feature_id: UUID
    ) -> List[Tuple[Stakeholder, StakeholderPerspective]]:
        """Get all stakeholder perspectives on a feature.
        
        Args:
            feature_id: ID of the feature
            
        Returns:
            List of (stakeholder, perspective) tuples
        """
        all_perspectives = self.perspective_storage.list()
        all_stakeholders = {s.id: s for s in self.stakeholder_storage.list()}
        
        # Filter and sort by stakeholder influence
        results = []
        
        for perspective in all_perspectives:
            if feature_id in perspective.related_feature_ids:
                stakeholder = all_stakeholders.get(perspective.stakeholder_id)
                if stakeholder:
                    results.append((stakeholder, perspective))
        
        # Sort by stakeholder influence (high to low) and date (newest first)
        results.sort(
            key=lambda x: (
                -self._influence_to_value(x[0].influence),
                x[1].date_recorded
            ),
            reverse=True
        )
        
        return results
    
    def get_perspectives_on_objective(
        self, objective_id: UUID
    ) -> List[Tuple[Stakeholder, StakeholderPerspective]]:
        """Get all stakeholder perspectives on an objective.
        
        Args:
            objective_id: ID of the objective
            
        Returns:
            List of (stakeholder, perspective) tuples
        """
        all_perspectives = self.perspective_storage.list()
        all_stakeholders = {s.id: s for s in self.stakeholder_storage.list()}
        
        # Filter and sort by stakeholder influence
        results = []
        
        for perspective in all_perspectives:
            if objective_id in perspective.related_objective_ids:
                stakeholder = all_stakeholders.get(perspective.stakeholder_id)
                if stakeholder:
                    results.append((stakeholder, perspective))
        
        # Sort by stakeholder influence (high to low) and date (newest first)
        results.sort(
            key=lambda x: (
                -self._influence_to_value(x[0].influence),
                x[1].date_recorded
            ),
            reverse=True
        )
        
        return results
    
    def get_stakeholders_by_feature(self, feature_id: UUID) -> List[Stakeholder]:
        """Get stakeholders with preferences for a feature.
        
        Args:
            feature_id: ID of the feature
            
        Returns:
            List of stakeholders sorted by influence
        """
        all_stakeholders = self.stakeholder_storage.list()
        
        # Filter stakeholders with preferences for this feature
        stakeholders = [
            s for s in all_stakeholders if feature_id in s.feature_preferences
        ]
        
        # Sort by feature preference score (high to low) and influence
        stakeholders.sort(
            key=lambda s: (
                -(s.feature_preferences.get(feature_id, 0)),
                -self._influence_to_value(s.influence)
            )
        )
        
        return stakeholders
    
    def get_stakeholders_by_objective(self, objective_id: UUID) -> List[Stakeholder]:
        """Get stakeholders with alignment on an objective.
        
        Args:
            objective_id: ID of the objective
            
        Returns:
            List of stakeholders sorted by alignment
        """
        all_stakeholders = self.stakeholder_storage.list()
        
        # Filter stakeholders with alignment for this objective
        stakeholders = [
            s for s in all_stakeholders if objective_id in s.objective_alignment
        ]
        
        # Sort by objective alignment score (high to low) and influence
        stakeholders.sort(
            key=lambda s: (
                -(s.objective_alignment.get(objective_id, 0)),
                -self._influence_to_value(s.influence)
            )
        )
        
        return stakeholders
    
    def get_stakeholders_by_role(self, role: StakeholderRoleEnum) -> List[Stakeholder]:
        """Get stakeholders with a specific role.
        
        Args:
            role: Role to filter by
            
        Returns:
            List of stakeholders with the role
        """
        all_stakeholders = self.stakeholder_storage.list()
        
        # Filter by role and sort by influence
        stakeholders = [s for s in all_stakeholders if s.role == role]
        stakeholders.sort(key=lambda s: -self._influence_to_value(s.influence))
        
        return stakeholders
    
    def create_stakeholder_groups(
        self, all_stakeholders: Optional[List[Stakeholder]] = None
    ) -> List[StakeholderGroup]:
        """Create stakeholder groups based on roles and characteristics.
        
        Args:
            all_stakeholders: Optional list of stakeholders to group
            
        Returns:
            List of stakeholder groups
        """
        if all_stakeholders is None:
            all_stakeholders = self.stakeholder_storage.list()
        
        # Create groups by role
        role_groups = {}
        for stakeholder in all_stakeholders:
            role = stakeholder.role.value
            if role not in role_groups:
                role_groups[role] = StakeholderGroup(
                    name=f"{role.capitalize()}",
                    description=f"Stakeholders with {role} role",
                    stakeholder_ids=[]
                )
            role_groups[role].stakeholder_ids.append(stakeholder.id)
        
        # Create groups by influence
        influence_groups = {}
        for stakeholder in all_stakeholders:
            influence = stakeholder.influence.value
            if influence not in influence_groups:
                influence_groups[influence] = StakeholderGroup(
                    name=f"{influence.capitalize()} Influence",
                    description=f"Stakeholders with {influence} influence",
                    stakeholder_ids=[]
                )
            influence_groups[influence].stakeholder_ids.append(stakeholder.id)
        
        # Create groups by organization
        org_groups = {}
        for stakeholder in all_stakeholders:
            if not stakeholder.organization:
                continue
            
            org = stakeholder.organization
            if org not in org_groups:
                org_groups[org] = StakeholderGroup(
                    name=org,
                    description=f"Stakeholders from {org}",
                    stakeholder_ids=[]
                )
            org_groups[org].stakeholder_ids.append(stakeholder.id)
        
        # Combine all groups
        all_groups = list(role_groups.values())
        all_groups.extend(influence_groups.values())
        all_groups.extend(org_groups.values())
        
        return all_groups
    
    def calculate_stakeholder_alignment(
        self, objective_ids: List[UUID], stakeholders: Optional[List[Stakeholder]] = None
    ) -> List[StakeholderAlignment]:
        """Calculate stakeholder alignment with objectives.
        
        Args:
            objective_ids: List of objective IDs to measure alignment with
            stakeholders: Optional list of stakeholders to analyze
            
        Returns:
            List of StakeholderAlignment with alignment scores
        """
        if stakeholders is None:
            stakeholders = self.stakeholder_storage.list()
        
        # Get objective names for the report
        objectives = {}
        for obj_id in objective_ids:
            try:
                obj = self.objective_storage.get(obj_id)
                objectives[str(obj_id)] = obj.name
            except Exception:
                objectives[str(obj_id)] = f"Objective {obj_id}"
        
        # Calculate alignment for each stakeholder
        alignments = []
        
        for stakeholder in stakeholders:
            alignment = StakeholderAlignment(
                stakeholder_id=stakeholder.id,
                stakeholder_name=stakeholder.name,
                alignment_scores={},
                overall_alignment=0.0
            )
            
            total_score = 0.0
            num_objectives = 0
            
            for obj_id in objective_ids:
                score = stakeholder.objective_alignment.get(obj_id, 0.0)
                alignment.alignment_scores[str(obj_id)] = score
                total_score += score
                num_objectives += 1
            
            if num_objectives > 0:
                alignment.overall_alignment = total_score / num_objectives
            
            alignments.append(alignment)
        
        # Sort by overall alignment (high to low)
        alignments.sort(key=lambda a: a.overall_alignment, reverse=True)
        
        return alignments
    
    def create_stakeholder_network(
        self, stakeholders: Optional[List[Stakeholder]] = None
    ) -> StakeholderNetwork:
        """Create a network visualization of stakeholder relationships.
        
        Args:
            stakeholders: Optional list of stakeholders to include
            
        Returns:
            StakeholderNetwork with nodes and links
        """
        if stakeholders is None:
            stakeholders = self.stakeholder_storage.list()
        
        network = StakeholderNetwork()
        
        # Add stakeholder nodes
        for stakeholder in stakeholders:
            network.nodes.append({
                "id": str(stakeholder.id),
                "name": stakeholder.name,
                "role": stakeholder.role.value,
                "organization": stakeholder.organization,
                "influence": stakeholder.influence.value
            })
        
        # Create a map for quick lookups
        stakeholder_map = {str(s.id): s for s in stakeholders}
        
        # Add links based on shared features and objectives
        for i, s1 in enumerate(stakeholders):
            s1_features = set(s1.feature_preferences.keys())
            s1_objectives = set(s1.objective_alignment.keys())
            
            for j, s2 in enumerate(stakeholders[i+1:], i+1):
                s2_features = set(s2.feature_preferences.keys())
                s2_objectives = set(s2.objective_alignment.keys())
                
                # Calculate shared interests
                shared_features = s1_features.intersection(s2_features)
                shared_objectives = s1_objectives.intersection(s2_objectives)
                
                if shared_features or shared_objectives:
                    # Calculate relationship strength (0.0 to 1.0)
                    strength = len(shared_features) * 0.1 + len(shared_objectives) * 0.2
                    strength = min(1.0, strength)
                    
                    if strength > 0.2:  # Threshold to reduce noise
                        network.links.append({
                            "source": str(s1.id),
                            "target": str(s2.id),
                            "type": "interest",
                            "strength": strength,
                            "label": (
                                f"{len(shared_features)} features, "
                                f"{len(shared_objectives)} objectives"
                            )
                        })
                
                # Add organizational links
                if (
                    s1.organization and 
                    s2.organization and 
                    s1.organization == s2.organization
                ):
                    network.links.append({
                        "source": str(s1.id),
                        "target": str(s2.id),
                        "type": "organization",
                        "strength": 0.8,
                        "label": s1.organization
                    })
        
        return network
    
    def add_engagement_history(
        self, stakeholder_id: UUID, engagement: str
    ) -> Stakeholder:
        """Add an engagement history entry for a stakeholder.
        
        Args:
            stakeholder_id: ID of the stakeholder
            engagement: Engagement history entry
            
        Returns:
            Updated stakeholder
        """
        stakeholder = self.stakeholder_storage.get(stakeholder_id)
        
        # Add timestamp to the entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"[{timestamp}] {engagement}"
        
        # Add to history
        stakeholder.engagement_history.append(entry)
        
        # Update timestamp
        stakeholder.updated_at = datetime.now()
        
        return self.stakeholder_storage.save(stakeholder)
    
    def update_feature_preference(
        self, stakeholder_id: UUID, feature_id: UUID, preference: float
    ) -> Stakeholder:
        """Update a stakeholder's preference for a feature.
        
        Args:
            stakeholder_id: ID of the stakeholder
            feature_id: ID of the feature
            preference: Preference score (0.0 to 1.0)
            
        Returns:
            Updated stakeholder
        """
        stakeholder = self.stakeholder_storage.get(stakeholder_id)
        
        # Verify the feature exists
        self.feature_storage.get(feature_id)
        
        # Update preference
        stakeholder.feature_preferences[feature_id] = max(0.0, min(1.0, preference))
        
        # Update timestamp
        stakeholder.updated_at = datetime.now()
        
        return self.stakeholder_storage.save(stakeholder)
    
    def update_objective_alignment(
        self, stakeholder_id: UUID, objective_id: UUID, alignment: float
    ) -> Stakeholder:
        """Update a stakeholder's alignment with an objective.
        
        Args:
            stakeholder_id: ID of the stakeholder
            objective_id: ID of the objective
            alignment: Alignment score (0.0 to 1.0)
            
        Returns:
            Updated stakeholder
        """
        stakeholder = self.stakeholder_storage.get(stakeholder_id)
        
        # Verify the objective exists
        self.objective_storage.get(objective_id)
        
        # Update alignment
        stakeholder.objective_alignment[objective_id] = max(0.0, min(1.0, alignment))
        
        # Update timestamp
        stakeholder.updated_at = datetime.now()
        
        return self.stakeholder_storage.save(stakeholder)
    
    def generate_stakeholder_report(
        self, stakeholders: List[Stakeholder], format: str = "markdown"
    ) -> str:
        """Generate a report of stakeholders.
        
        Args:
            stakeholders: List of stakeholders to include
            format: Output format ("markdown" or "text")
            
        Returns:
            Report as a string
        """
        if format == "markdown":
            return self._generate_markdown_report(stakeholders)
        else:
            return self._generate_text_report(stakeholders)
    
    def _generate_markdown_report(self, stakeholders: List[Stakeholder]) -> str:
        """Generate a Markdown report of stakeholders.
        
        Args:
            stakeholders: List of stakeholders to include
            
        Returns:
            Markdown report
        """
        report = "# Stakeholder Report\n\n"
        report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += f"Number of stakeholders: {len(stakeholders)}\n\n"
        
        # Group by role
        stakeholders_by_role = {}
        for stakeholder in stakeholders:
            role = stakeholder.role.value
            if role not in stakeholders_by_role:
                stakeholders_by_role[role] = []
            stakeholders_by_role[role].append(stakeholder)
        
        # Generate report by role
        for role in sorted(stakeholders_by_role.keys()):
            role_stakeholders = stakeholders_by_role[role]
            
            report += f"## {role.capitalize()}\n\n"
            
            for stakeholder in sorted(role_stakeholders, key=lambda s: s.name):
                report += f"### {stakeholder.name}\n\n"
                
                # Add basic info
                if stakeholder.organization:
                    report += f"**Organization:** {stakeholder.organization}\n\n"
                
                report += f"**Influence:** {stakeholder.influence.value}\n\n"
                
                if stakeholder.email:
                    report += f"**Email:** {stakeholder.email}\n\n"
                
                # Add key concerns
                if stakeholder.key_concerns:
                    report += "**Key Concerns:**\n\n"
                    for concern in stakeholder.key_concerns:
                        report += f"- {concern}\n"
                    report += "\n"
                
                # Add communication preferences
                if stakeholder.communication_preferences:
                    report += f"**Communication Preferences:**\n\n{stakeholder.communication_preferences}\n\n"
                
                # Add feature preferences
                if stakeholder.feature_preferences:
                    report += "**Feature Preferences:**\n\n"
                    report += "| Feature | Preference |\n"
                    report += "|---------|------------|\n"
                    
                    # Get feature names
                    feature_names = {}
                    for feature_id in stakeholder.feature_preferences:
                        try:
                            feature = self.feature_storage.get(feature_id)
                            feature_names[feature_id] = feature.name
                        except Exception:
                            feature_names[feature_id] = f"Feature {feature_id}"
                    
                    # Sort by preference (high to low)
                    sorted_preferences = sorted(
                        stakeholder.feature_preferences.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )
                    
                    for feature_id, preference in sorted_preferences:
                        feature_name = feature_names.get(feature_id, f"Feature {feature_id}")
                        report += f"| {feature_name} | {preference:.2f} |\n"
                    
                    report += "\n"
                
                # Add notes
                if stakeholder.notes:
                    report += f"**Notes:**\n\n{stakeholder.notes}\n\n"
                
                report += "---\n\n"
        
        return report
    
    def _generate_text_report(self, stakeholders: List[Stakeholder]) -> str:
        """Generate a text report of stakeholders.
        
        Args:
            stakeholders: List of stakeholders to include
            
        Returns:
            Text report
        """
        report = "STAKEHOLDER REPORT\n\n"
        report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += f"Number of stakeholders: {len(stakeholders)}\n\n"
        
        # Group by role
        stakeholders_by_role = {}
        for stakeholder in stakeholders:
            role = stakeholder.role.value
            if role not in stakeholders_by_role:
                stakeholders_by_role[role] = []
            stakeholders_by_role[role].append(stakeholder)
        
        # Generate report by role
        for role in sorted(stakeholders_by_role.keys()):
            role_stakeholders = stakeholders_by_role[role]
            
            report += f"{role.upper()}\n"
            report += "=" * len(role) + "\n\n"
            
            for stakeholder in sorted(role_stakeholders, key=lambda s: s.name):
                report += f"{stakeholder.name}\n"
                report += "-" * len(stakeholder.name) + "\n\n"
                
                # Add basic info
                if stakeholder.organization:
                    report += f"Organization: {stakeholder.organization}\n"
                
                report += f"Influence: {stakeholder.influence.value}\n"
                
                if stakeholder.email:
                    report += f"Email: {stakeholder.email}\n"
                
                report += "\n"
                
                # Add key concerns
                if stakeholder.key_concerns:
                    report += "Key Concerns:\n"
                    for concern in stakeholder.key_concerns:
                        report += f"- {concern}\n"
                    report += "\n"
                
                # Add communication preferences
                if stakeholder.communication_preferences:
                    report += f"Communication Preferences:\n{stakeholder.communication_preferences}\n\n"
                
                # Add feature preferences
                if stakeholder.feature_preferences:
                    report += "Feature Preferences:\n"
                    
                    # Get feature names
                    feature_names = {}
                    for feature_id in stakeholder.feature_preferences:
                        try:
                            feature = self.feature_storage.get(feature_id)
                            feature_names[feature_id] = feature.name
                        except Exception:
                            feature_names[feature_id] = f"Feature {feature_id}"
                    
                    # Sort by preference (high to low)
                    sorted_preferences = sorted(
                        stakeholder.feature_preferences.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )
                    
                    for feature_id, preference in sorted_preferences:
                        feature_name = feature_names.get(feature_id, f"Feature {feature_id}")
                        report += f"- {feature_name}: {preference:.2f}\n"
                    
                    report += "\n"
                
                # Add notes
                if stakeholder.notes:
                    report += f"Notes:\n{stakeholder.notes}\n\n"
                
                report += "\n" + "-" * 80 + "\n\n"
        
        return report