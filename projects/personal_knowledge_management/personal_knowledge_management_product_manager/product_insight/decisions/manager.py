"""
Decision management module for ProductInsight.

This module provides functionality for capturing, documenting, and retrieving
product decisions with full context and rationale.
"""

from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Union
from uuid import UUID

from pydantic import BaseModel, Field

from product_insight.models import Decision, Feature, StrategicObjective, Tag
from product_insight.storage import FileStorage, StorageInterface


class DecisionQuery(BaseModel):
    """Query parameters for searching decisions."""
    
    text: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    feature_ids: List[UUID] = Field(default_factory=list)
    objective_ids: List[UUID] = Field(default_factory=list)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    decided_by: List[UUID] = Field(default_factory=list)
    limit: int = 50


class DecisionTree(BaseModel):
    """Tree representation of related decisions."""
    
    root_decision: Decision
    related_decisions: List[Decision] = Field(default_factory=list)
    related_features: List[Feature] = Field(default_factory=list)
    related_objectives: List[StrategicObjective] = Field(default_factory=list)


class DecisionTimeline(BaseModel):
    """Timeline of decisions."""
    
    decisions: List[Tuple[datetime, Decision]] = Field(default_factory=list)


class DecisionOutcome(BaseModel):
    """Outcome of a decision."""
    
    decision_id: UUID
    outcome_notes: str
    outcome_date: datetime = Field(default_factory=datetime.now)
    success_rating: Optional[float] = None
    retrospective: Optional[str] = None


class DecisionManager:
    """Manages product decisions and their documentation."""
    
    def __init__(
        self,
        storage_dir: str,
        decision_storage: Optional[StorageInterface[Decision]] = None,
        feature_storage: Optional[StorageInterface[Feature]] = None,
        objective_storage: Optional[StorageInterface[StrategicObjective]] = None,
    ):
        """Initialize the decision manager.
        
        Args:
            storage_dir: Base directory for storing decision data
            decision_storage: Optional custom storage for decisions
            feature_storage: Optional custom storage for features
            objective_storage: Optional custom storage for objectives
        """
        self.decision_storage = decision_storage or FileStorage(
            entity_type=Decision,
            storage_dir=f"{storage_dir}/decisions",
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
    
    def add_decision(self, decision: Decision) -> Decision:
        """Add a new decision.
        
        Args:
            decision: Decision to add
            
        Returns:
            Added decision
        """
        return self.decision_storage.save(decision)
    
    def update_decision(self, decision: Decision) -> Decision:
        """Update an existing decision.
        
        Args:
            decision: Decision to update
            
        Returns:
            Updated decision
        """
        return self.decision_storage.save(decision)
    
    def get_decision(self, decision_id: UUID) -> Decision:
        """Get a decision by ID.
        
        Args:
            decision_id: ID of the decision to get
            
        Returns:
            Decision
        """
        return self.decision_storage.get(decision_id)
    
    def delete_decision(self, decision_id: UUID) -> bool:
        """Delete a decision.

        Args:
            decision_id: ID of the decision to delete

        Returns:
            True if the decision was deleted, False otherwise
        """
        return self.decision_storage.delete(decision_id)

    def list_decisions(self) -> List[Decision]:
        """List all decisions.

        Returns:
            List of all decisions
        """
        return self.decision_storage.list()

    def search_decisions(self, query: DecisionQuery) -> List[Decision]:
        """Search for decisions matching the query.
        
        Args:
            query: Search parameters
            
        Returns:
            List of matching decisions
        """
        all_decisions = self.decision_storage.list()
        matching_decisions = []
        
        for decision in all_decisions:
            # Apply filters
            
            # Text search
            if query.text:
                text_lower = query.text.lower()
                if not (
                    text_lower in decision.title.lower() or
                    text_lower in decision.description.lower() or
                    text_lower in decision.context.lower() or
                    text_lower in decision.rationale.lower() or
                    (decision.outcome_notes and text_lower in decision.outcome_notes.lower()) or
                    (decision.retrospective and text_lower in decision.retrospective.lower())
                ):
                    continue
            
            # Tags
            if query.tags:
                decision_tags = {tag.name.lower() for tag in decision.tags}
                query_tags = {tag.lower() for tag in query.tags}
                if not decision_tags.intersection(query_tags):
                    continue
            
            # Feature IDs
            if query.feature_ids and not set(query.feature_ids).intersection(set(decision.feature_ids)):
                continue
            
            # Objective IDs
            if query.objective_ids and not set(query.objective_ids).intersection(set(decision.objective_ids)):
                continue
            
            # Date range
            if query.start_date and decision.decision_date < query.start_date:
                continue
            if query.end_date and decision.decision_date > query.end_date:
                continue
            
            # Decided by
            if query.decided_by and not set(query.decided_by).intersection(set(decision.decided_by)):
                continue
            
            matching_decisions.append(decision)
        
        # Sort by date (newest first) and apply limit
        matching_decisions.sort(key=lambda d: d.decision_date, reverse=True)
        return matching_decisions[:query.limit]
    
    def add_decision_outcome(
        self, decision_id: UUID, outcome: DecisionOutcome
    ) -> Decision:
        """Add or update the outcome of a decision.
        
        Args:
            decision_id: ID of the decision
            outcome: Outcome information
            
        Returns:
            Updated decision
        """
        decision = self.decision_storage.get(decision_id)
        
        # Update outcome information
        decision.outcome_notes = outcome.outcome_notes
        decision.outcome_date = outcome.outcome_date
        
        if outcome.retrospective:
            decision.retrospective = outcome.retrospective
        
        # Update timestamp
        decision.updated_at = datetime.now()
        
        return self.decision_storage.save(decision)
    
    def get_decision_tree(self, decision_id: UUID) -> DecisionTree:
        """Get a tree of related decisions, features, and objectives.
        
        Args:
            decision_id: ID of the root decision
            
        Returns:
            DecisionTree with related entities
        """
        root_decision = self.decision_storage.get(decision_id)
        related_decisions = []
        related_features = []
        related_objectives = []
        
        # Get related features
        for feature_id in root_decision.feature_ids:
            try:
                feature = self.feature_storage.get(feature_id)
                related_features.append(feature)
            except Exception as e:
                print(f"Error getting feature {feature_id}: {e}")
        
        # Get related objectives
        for objective_id in root_decision.objective_ids:
            try:
                objective = self.objective_storage.get(objective_id)
                related_objectives.append(objective)
            except Exception as e:
                print(f"Error getting objective {objective_id}: {e}")
        
        # Find related decisions (decisions about the same features or objectives)
        all_decisions = self.decision_storage.list()
        
        for decision in all_decisions:
            if decision.id == root_decision.id:
                continue
            
            # Check for shared features or objectives
            if (
                set(decision.feature_ids).intersection(set(root_decision.feature_ids)) or
                set(decision.objective_ids).intersection(set(root_decision.objective_ids))
            ):
                related_decisions.append(decision)
        
        return DecisionTree(
            root_decision=root_decision,
            related_decisions=related_decisions,
            related_features=related_features,
            related_objectives=related_objectives
        )
    
    def get_decision_timeline(
        self, 
        feature_id: Optional[UUID] = None,
        objective_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> DecisionTimeline:
        """Get a timeline of decisions.
        
        Args:
            feature_id: Optional feature ID to filter by
            objective_id: Optional objective ID to filter by
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            DecisionTimeline with decisions sorted by date
        """
        all_decisions = self.decision_storage.list()
        filtered_decisions = []
        
        for decision in all_decisions:
            # Apply filters
            if feature_id and feature_id not in decision.feature_ids:
                continue
            
            if objective_id and objective_id not in decision.objective_ids:
                continue
            
            if start_date and decision.decision_date < start_date:
                continue
            
            if end_date and decision.decision_date > end_date:
                continue
            
            filtered_decisions.append((decision.decision_date, decision))
        
        # Sort by date
        filtered_decisions.sort(key=lambda x: x[0])
        
        return DecisionTimeline(decisions=filtered_decisions)
    
    def find_decisions_by_feature(self, feature_id: UUID) -> List[Decision]:
        """Find decisions related to a specific feature.
        
        Args:
            feature_id: Feature ID to search for
            
        Returns:
            List of related decisions
        """
        all_decisions = self.decision_storage.list()
        
        related_decisions = [
            decision for decision in all_decisions
            if feature_id in decision.feature_ids
        ]
        
        # Sort by date (newest first)
        related_decisions.sort(key=lambda d: d.decision_date, reverse=True)
        
        return related_decisions
    
    def find_decisions_by_objective(self, objective_id: UUID) -> List[Decision]:
        """Find decisions related to a specific objective.
        
        Args:
            objective_id: Objective ID to search for
            
        Returns:
            List of related decisions
        """
        all_decisions = self.decision_storage.list()
        
        related_decisions = [
            decision for decision in all_decisions
            if objective_id in decision.objective_ids
        ]
        
        # Sort by date (newest first)
        related_decisions.sort(key=lambda d: d.decision_date, reverse=True)
        
        return related_decisions
    
    def find_decisions_by_stakeholder(self, stakeholder_id: UUID) -> List[Decision]:
        """Find decisions involving a specific stakeholder.

        Args:
            stakeholder_id: Stakeholder ID to search for

        Returns:
            List of related decisions
        """
        all_decisions = self.decision_storage.list()
        stakeholder_id_str = str(stakeholder_id)

        related_decisions = [
            decision for decision in all_decisions
            if (stakeholder_id in decision.decided_by or stakeholder_id_str in decision.stakeholder_input)
        ]

        # Sort by date (newest first)
        related_decisions.sort(key=lambda d: d.decision_date, reverse=True)

        return related_decisions
    
    def generate_decision_report(
        self, decisions: List[Decision], format: str = "markdown"
    ) -> str:
        """Generate a report of decisions.
        
        Args:
            decisions: List of decisions to include
            format: Output format ("markdown" or "text")
            
        Returns:
            Report as a string
        """
        if format == "markdown":
            return self._generate_markdown_report(decisions)
        else:
            return self._generate_text_report(decisions)
    
    def _generate_markdown_report(self, decisions: List[Decision]) -> str:
        """Generate a Markdown report of decisions.
        
        Args:
            decisions: List of decisions to include
            
        Returns:
            Markdown report
        """
        report = "# Decision Report\n\n"
        report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += f"Number of decisions: {len(decisions)}\n\n"
        
        # Group by month
        decisions_by_month = {}
        for decision in decisions:
            month_key = decision.decision_date.strftime("%Y-%m")
            if month_key not in decisions_by_month:
                decisions_by_month[month_key] = []
            decisions_by_month[month_key].append(decision)
        
        # Generate report by month
        for month_key in sorted(decisions_by_month.keys(), reverse=True):
            month_decisions = decisions_by_month[month_key]
            month_name = datetime.strptime(month_key, "%Y-%m").strftime("%B %Y")
            
            report += f"## {month_name}\n\n"
            
            for decision in sorted(month_decisions, key=lambda d: d.decision_date, reverse=True):
                report += f"### {decision.title}\n\n"
                report += f"**Date:** {decision.decision_date.strftime('%Y-%m-%d')}\n\n"
                report += f"**Description:** {decision.description}\n\n"
                
                # Add context and rationale
                report += "#### Context\n\n"
                report += f"{decision.context}\n\n"
                
                report += "#### Rationale\n\n"
                report += f"{decision.rationale}\n\n"
                
                # Add alternatives if available
                if decision.alternatives:
                    report += "#### Alternatives Considered\n\n"
                    for i, alt in enumerate(decision.alternatives):
                        report += f"{i+1}. {alt}\n"
                    report += "\n"
                
                # Add outcome if available
                if decision.outcome_notes:
                    report += "#### Outcome\n\n"
                    report += f"{decision.outcome_notes}\n\n"
                    
                    if decision.outcome_date:
                        report += f"**Outcome Date:** {decision.outcome_date.strftime('%Y-%m-%d')}\n\n"
                    
                    if decision.retrospective:
                        report += "#### Retrospective\n\n"
                        report += f"{decision.retrospective}\n\n"
                
                # Add tags
                if decision.tags:
                    tags = ", ".join(tag.name for tag in decision.tags)
                    report += f"**Tags:** {tags}\n\n"
                
                report += "---\n\n"
        
        return report
    
    def _generate_text_report(self, decisions: List[Decision]) -> str:
        """Generate a text report of decisions.
        
        Args:
            decisions: List of decisions to include
            
        Returns:
            Text report
        """
        report = "DECISION REPORT\n\n"
        report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += f"Number of decisions: {len(decisions)}\n\n"
        
        # Sort by date (newest first)
        sorted_decisions = sorted(decisions, key=lambda d: d.decision_date, reverse=True)
        
        for decision in sorted_decisions:
            report += f"TITLE: {decision.title}\n"
            report += f"DATE: {decision.decision_date.strftime('%Y-%m-%d')}\n"
            report += f"DESCRIPTION: {decision.description}\n\n"
            
            # Add context and rationale
            report += "CONTEXT:\n"
            report += f"{decision.context}\n\n"
            
            report += "RATIONALE:\n"
            report += f"{decision.rationale}\n\n"
            
            # Add alternatives if available
            if decision.alternatives:
                report += "ALTERNATIVES CONSIDERED:\n"
                for i, alt in enumerate(decision.alternatives):
                    report += f"{i+1}. {alt}\n"
                report += "\n"
            
            # Add outcome if available
            if decision.outcome_notes:
                report += "OUTCOME:\n"
                report += f"{decision.outcome_notes}\n\n"
                
                if decision.outcome_date:
                    report += f"OUTCOME DATE: {decision.outcome_date.strftime('%Y-%m-%d')}\n\n"
                
                if decision.retrospective:
                    report += "RETROSPECTIVE:\n"
                    report += f"{decision.retrospective}\n\n"
            
            # Add tags
            if decision.tags:
                tags = ", ".join(tag.name for tag in decision.tags)
                report += f"TAGS: {tags}\n\n"
            
            report += "-" * 80 + "\n\n"
        
        return report