"""
Knowledge insights module for ProductInsight.

This module provides functionality for generating insights across different
knowledge domains and identifying non-obvious connections.
"""

from collections import Counter
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Union, Any
from uuid import UUID

from pydantic import BaseModel, Field

from product_insight.models import (
    Competitor,
    Decision,
    Feature,
    FeedbackCluster,
    FeedbackItem,
    PriorityEnum,
    StatusEnum,
    Stakeholder,
    StakeholderPerspective,
    StrategicObjective,
    Tag,
)
from product_insight.storage import FileStorage, StorageInterface


class Insight(BaseModel):
    """An insight derived from knowledge data."""
    
    title: str
    description: str
    confidence: float  # 0.0 to 1.0
    source_entities: List[Dict[str, Any]] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.now)
    insight_type: str = "general"
    tags: List[str] = Field(default_factory=list)


class InsightGroup(BaseModel):
    """A group of related insights."""
    
    title: str
    insights: List[Insight] = Field(default_factory=list)
    insight_type: str = "general"


class TrendData(BaseModel):
    """Data for trend analysis."""
    
    title: str
    time_periods: List[str] = Field(default_factory=list)
    series: Dict[str, List[float]] = Field(default_factory=dict)


class TrendPoint(BaseModel):
    """A single point in a trend."""
    
    value: float
    date: datetime
    entity_ids: List[UUID] = Field(default_factory=list)


class InsightEngine:
    """Engine for generating insights from knowledge data."""
    
    def __init__(
        self,
        storage_dir: str,
        feedback_storage: Optional[StorageInterface[FeedbackItem]] = None,
        feedback_cluster_storage: Optional[StorageInterface[FeedbackCluster]] = None,
        feature_storage: Optional[StorageInterface[Feature]] = None,
        objective_storage: Optional[StorageInterface[StrategicObjective]] = None,
        decision_storage: Optional[StorageInterface[Decision]] = None,
        competitor_storage: Optional[StorageInterface[Competitor]] = None,
        stakeholder_storage: Optional[StorageInterface[Stakeholder]] = None,
        perspective_storage: Optional[StorageInterface[StakeholderPerspective]] = None,
    ):
        """Initialize the insight engine.
        
        Args:
            storage_dir: Base directory for storing data
            feedback_storage: Optional custom storage for feedback
            feedback_cluster_storage: Optional custom storage for feedback clusters
            feature_storage: Optional custom storage for features
            objective_storage: Optional custom storage for objectives
            decision_storage: Optional custom storage for decisions
            competitor_storage: Optional custom storage for competitors
            stakeholder_storage: Optional custom storage for stakeholders
            perspective_storage: Optional custom storage for stakeholder perspectives
        """
        self.feedback_storage = feedback_storage or FileStorage(
            entity_type=FeedbackItem,
            storage_dir=f"{storage_dir}/feedback",
            format="json"
        )
        
        self.feedback_cluster_storage = feedback_cluster_storage or FileStorage(
            entity_type=FeedbackCluster,
            storage_dir=f"{storage_dir}/feedback_clusters",
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
        
        self.decision_storage = decision_storage or FileStorage(
            entity_type=Decision,
            storage_dir=f"{storage_dir}/decisions",
            format="json"
        )
        
        self.competitor_storage = competitor_storage or FileStorage(
            entity_type=Competitor,
            storage_dir=f"{storage_dir}/competitors",
            format="json"
        )
        
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
    
    def generate_feedback_insights(self) -> List[Insight]:
        """Generate insights from feedback data.
        
        Returns:
            List of insights
        """
        insights = []
        
        # Get data
        feedback_items = self.feedback_storage.list()
        clusters = self.feedback_cluster_storage.list()
        features = self.feature_storage.list()
        
        # Only proceed if we have data
        if not feedback_items:
            return insights
        
        # Insight 1: High impact feedback without linked features
        high_impact_feedback = [
            fb for fb in feedback_items
            if fb.impact_score and fb.impact_score >= 0.7 and not fb.extracted_features
        ]
        
        if high_impact_feedback:
            source_entities = [
                {
                    "id": str(fb.id),
                    "type": "feedback",
                    "text": fb.content[:100],
                    "impact": fb.impact_score
                }
                for fb in high_impact_feedback[:5]
            ]
            
            insight = Insight(
                title="High Impact Feedback Without Feature Mapping",
                description=(
                    f"Found {len(high_impact_feedback)} high-impact feedback items "
                    f"that are not mapped to any specific feature requests. "
                    f"These may represent unaddressed user needs."
                ),
                confidence=0.8,
                source_entities=source_entities,
                insight_type="feedback_gap",
                tags=["feedback", "gaps", "opportunities"]
            )
            
            insights.append(insight)
        
        # Insight 2: Common tags in feedback clusters
        if clusters:
            all_tags = []
            for cluster in clusters:
                for tag in cluster.tags:
                    all_tags.append(tag.name)
            
            tag_counts = Counter(all_tags)
            common_tags = [tag for tag, count in tag_counts.most_common(5) if count > 1]
            
            if common_tags:
                related_clusters = [
                    c for c in clusters
                    if any(tag.name in common_tags for tag in c.tags)
                ]
                
                source_entities = [
                    {
                        "id": str(c.id),
                        "type": "feedback_cluster",
                        "name": c.name,
                        "size": c.volume,
                        "tags": [t.name for t in c.tags]
                    }
                    for c in related_clusters[:5]
                ]
                
                insight = Insight(
                    title="Common Themes Across Feedback Clusters",
                    description=(
                        f"Identified {len(common_tags)} recurring themes across multiple feedback clusters: "
                        f"{', '.join(common_tags)}. These represent consistent user interests or pain points."
                    ),
                    confidence=0.75,
                    source_entities=source_entities,
                    insight_type="feedback_theme",
                    tags=["feedback", "themes", "patterns"]
                )
                
                insights.append(insight)
        
        # Insight 3: Negative sentiment trends
        negative_sentiment_count = sum(
            1 for fb in feedback_items
            if fb.sentiment and (fb.sentiment.value == "negative" or fb.sentiment.value == "very_negative")
        )
        
        negative_ratio = negative_sentiment_count / len(feedback_items) if feedback_items else 0
        
        if negative_ratio >= 0.3:  # If at least 30% negative sentiment
            negative_feedback = [
                fb for fb in feedback_items
                if fb.sentiment and (fb.sentiment.value == "negative" or fb.sentiment.value == "very_negative")
            ]
            
            source_entities = [
                {
                    "id": str(fb.id),
                    "type": "feedback",
                    "text": fb.content[:100],
                    "sentiment": fb.sentiment.value if fb.sentiment else "unknown"
                }
                for fb in negative_feedback[:5]
            ]
            
            insight = Insight(
                title="High Negative Sentiment Ratio",
                description=(
                    f"{negative_sentiment_count} out of {len(feedback_items)} feedback items "
                    f"({negative_ratio:.0%}) have negative sentiment. This may indicate "
                    f"underlying product issues that need attention."
                ),
                confidence=0.85,
                source_entities=source_entities,
                insight_type="sentiment_issue",
                tags=["feedback", "sentiment", "issues"]
            )
            
            insights.append(insight)
        
        # Insight 4: Feedback clusters without linked features
        if clusters:
            unlinked_clusters = [
                c for c in clusters
                if not c.feature_requests and c.impact_score and c.impact_score >= 0.6
            ]
            
            if unlinked_clusters:
                source_entities = [
                    {
                        "id": str(c.id),
                        "type": "feedback_cluster",
                        "name": c.name,
                        "size": c.volume,
                        "impact": c.impact_score
                    }
                    for c in unlinked_clusters[:5]
                ]
                
                insight = Insight(
                    title="High Impact Feedback Clusters Without Features",
                    description=(
                        f"Found {len(unlinked_clusters)} high-impact feedback clusters "
                        f"that are not linked to any feature requests. "
                        f"These represent potentially valuable feature opportunities."
                    ),
                    confidence=0.8,
                    source_entities=source_entities,
                    insight_type="opportunity",
                    tags=["feedback", "clusters", "opportunities"]
                )
                
                insights.append(insight)
        
        return insights
    
    def generate_feature_insights(self) -> List[Insight]:
        """Generate insights from feature data.
        
        Returns:
            List of insights
        """
        insights = []
        
        # Get data
        features = self.feature_storage.list()
        stakeholders = self.stakeholder_storage.list()
        
        # Only proceed if we have data
        if not features:
            return insights
        
        # Insight 1: High value features with low priority
        high_value_low_priority = [
            f for f in features
            if f.value_estimate and f.value_estimate >= 8.0 and
            f.priority_score and f.priority_score < 0.5
        ]
        
        if high_value_low_priority:
            source_entities = [
                {
                    "id": str(f.id),
                    "type": "feature",
                    "name": f.name,
                    "value": f.value_estimate,
                    "priority": f.priority_score
                }
                for f in high_value_low_priority[:5]
            ]
            
            insight = Insight(
                title="High-Value Features with Low Priority",
                description=(
                    f"Identified {len(high_value_low_priority)} features with high estimated value "
                    f"but relatively low priority scores. These may represent overlooked opportunities."
                ),
                confidence=0.75,
                source_entities=source_entities,
                insight_type="priority_mismatch",
                tags=["features", "priority", "opportunity"]
            )
            
            insights.append(insight)
        
        # Insight 2: Features with no linked objectives
        features_no_objectives = [
            f for f in features
            if not f.objective_ids and f.status != StatusEnum.COMPLETED and f.status != StatusEnum.CANCELLED
        ]
        
        if features_no_objectives:
            source_entities = [
                {
                    "id": str(f.id),
                    "type": "feature",
                    "name": f.name,
                    "status": f.status.value if f.status else "unknown"
                }
                for f in features_no_objectives[:5]
            ]
            
            insight = Insight(
                title="Features Without Strategic Alignment",
                description=(
                    f"Found {len(features_no_objectives)} active features that are not linked "
                    f"to any strategic objectives. These features may not be aligned with "
                    f"the product strategy."
                ),
                confidence=0.8,
                source_entities=source_entities,
                insight_type="alignment_gap",
                tags=["features", "strategy", "alignment"]
            )
            
            insights.append(insight)
        
        # Insight 3: Features with dependency bottlenecks
        dependency_counts = Counter()
        for feature in features:
            for dependency in feature.dependencies:
                dependency_counts[dependency] += 1
        
        bottlenecks = [
            (dep_id, count) for dep_id, count in dependency_counts.most_common(5)
            if count >= 3
        ]
        
        if bottlenecks:
            bottleneck_entities = []
            for dep_id, count in bottlenecks:
                # Find the bottleneck feature
                for feature in features:
                    if feature.id == dep_id:
                        bottleneck_entities.append({
                            "id": str(feature.id),
                            "type": "feature",
                            "name": feature.name,
                            "dependent_count": count,
                            "status": feature.status.value if feature.status else "unknown"
                        })
                        break
            
            insight = Insight(
                title="Feature Dependency Bottlenecks",
                description=(
                    f"Identified {len(bottlenecks)} features that are dependencies for "
                    f"multiple other features. These may be bottlenecks in your development process."
                ),
                confidence=0.85,
                source_entities=bottleneck_entities,
                insight_type="dependency_bottleneck",
                tags=["features", "dependencies", "bottlenecks"]
            )
            
            insights.append(insight)
        
        # Insight 4: Feature interest mismatches between stakeholders
        if stakeholders:
            feature_interest = {}
            high_influence_stakeholders = [
                s for s in stakeholders if s.influence.value == "high"
            ]
            
            for feature in features:
                if feature.status == StatusEnum.PLANNED or feature.status == StatusEnum.IN_PROGRESS:
                    # Check if high-influence stakeholders have different opinions
                    high_interest = []
                    low_interest = []
                    
                    for stakeholder in high_influence_stakeholders:
                        preference = stakeholder.feature_preferences.get(feature.id, 0.5)
                        if preference >= 0.8:
                            high_interest.append(stakeholder)
                        elif preference <= 0.3:
                            low_interest.append(stakeholder)
                    
                    if high_interest and low_interest:
                        feature_interest[feature.id] = {
                            "feature": feature,
                            "high_interest": high_interest,
                            "low_interest": low_interest
                        }
            
            if feature_interest:
                mismatch_features = list(feature_interest.values())[:5]
                source_entities = []
                
                for info in mismatch_features:
                    feature = info["feature"]
                    source_entities.append({
                        "id": str(feature.id),
                        "type": "feature",
                        "name": feature.name,
                        "high_interest_stakeholders": [s.name for s in info["high_interest"]],
                        "low_interest_stakeholders": [s.name for s in info["low_interest"]]
                    })
                
                insight = Insight(
                    title="Stakeholder Interest Conflicts",
                    description=(
                        f"Identified {len(feature_interest)} features where high-influence stakeholders "
                        f"have conflicting interests. These may require careful stakeholder management."
                    ),
                    confidence=0.7,
                    source_entities=source_entities,
                    insight_type="stakeholder_conflict",
                    tags=["features", "stakeholders", "conflicts"]
                )
                
                insights.append(insight)
        
        return insights
    
    def generate_objective_insights(self) -> List[Insight]:
        """Generate insights from objective data.
        
        Returns:
            List of insights
        """
        insights = []
        
        # Get data
        objectives = self.objective_storage.list()
        features = self.feature_storage.list()
        
        # Only proceed if we have data
        if not objectives:
            return insights
        
        # Insight 1: Objectives without linked features
        objectives_no_features = [
            obj for obj in objectives
            if not obj.feature_ids and obj.status != StatusEnum.COMPLETED and obj.status != StatusEnum.CANCELLED
        ]
        
        if objectives_no_features:
            source_entities = [
                {
                    "id": str(obj.id),
                    "type": "objective",
                    "name": obj.name,
                    "status": obj.status.value if obj.status else "unknown"
                }
                for obj in objectives_no_features[:5]
            ]
            
            insight = Insight(
                title="Objectives Without Implementation Features",
                description=(
                    f"Found {len(objectives_no_features)} active strategic objectives that "
                    f"don't have any linked implementation features. These objectives "
                    f"risk not being fulfilled."
                ),
                confidence=0.85,
                source_entities=source_entities,
                insight_type="implementation_gap",
                tags=["objectives", "features", "gaps"]
            )
            
            insights.append(insight)
        
        # Insight 2: Low progress on high priority objectives
        high_priority_low_progress = [
            obj for obj in objectives
            if obj.priority in (PriorityEnum.CRITICAL, PriorityEnum.HIGH) and
            obj.metric_current is not None and obj.metric_target is not None and
            obj.metric_target > 0 and (obj.metric_current / obj.metric_target) < 0.3 and
            obj.status != StatusEnum.COMPLETED and obj.status != StatusEnum.CANCELLED
        ]
        
        if high_priority_low_progress:
            source_entities = [
                {
                    "id": str(obj.id),
                    "type": "objective",
                    "name": obj.name,
                    "priority": obj.priority.value if obj.priority else "unknown",
                    "progress": (
                        f"{(obj.metric_current / obj.metric_target) * 100:.0f}%"
                        if obj.metric_current is not None and obj.metric_target is not None and obj.metric_target > 0
                        else "unknown"
                    )
                }
                for obj in high_priority_low_progress[:5]
            ]
            
            insight = Insight(
                title="High Priority Objectives with Low Progress",
                description=(
                    f"Identified {len(high_priority_low_progress)} high-priority objectives "
                    f"with less than 30% progress toward their targets. These may need "
                    f"increased focus and resources."
                ),
                confidence=0.8,
                source_entities=source_entities,
                insight_type="priority_progress_mismatch",
                tags=["objectives", "priority", "progress"]
            )
            
            insights.append(insight)
        
        # Insight 3: Objectives nearing timeframe end with low progress
        current_date = datetime.now()
        approaching_deadlines = [
            obj for obj in objectives
            if obj.timeframe_end and obj.timeframe_end > current_date and
            obj.timeframe_end < (current_date + timedelta(days=30)) and
            obj.metric_current is not None and obj.metric_target is not None and
            obj.metric_target > 0 and (obj.metric_current / obj.metric_target) < 0.7 and
            obj.status != StatusEnum.COMPLETED and obj.status != StatusEnum.CANCELLED
        ]
        
        if approaching_deadlines:
            source_entities = [
                {
                    "id": str(obj.id),
                    "type": "objective",
                    "name": obj.name,
                    "deadline": obj.timeframe_end.strftime("%Y-%m-%d"),
                    "progress": (
                        f"{(obj.metric_current / obj.metric_target) * 100:.0f}%"
                        if obj.metric_current is not None and obj.metric_target is not None and obj.metric_target > 0
                        else "unknown"
                    )
                }
                for obj in approaching_deadlines[:5]
            ]
            
            insight = Insight(
                title="Objectives at Risk of Missing Deadlines",
                description=(
                    f"Found {len(approaching_deadlines)} objectives with approaching deadlines "
                    f"(within 30 days) that have less than 70% progress toward their targets. "
                    f"These are at risk of not being completed on time."
                ),
                confidence=0.9,
                source_entities=source_entities,
                insight_type="deadline_risk",
                tags=["objectives", "deadlines", "risks"]
            )
            
            insights.append(insight)
        
        # Insight 4: Abandoned child objectives
        orphaned_objectives = []
        
        for obj in objectives:
            if obj.parent_id:
                parent = next((o for o in objectives if o.id == obj.parent_id), None)
                if parent and (
                    parent.status == StatusEnum.COMPLETED or
                    parent.status == StatusEnum.CANCELLED or
                    parent.status == StatusEnum.DEFERRED
                ) and obj.status in (StatusEnum.PLANNED, StatusEnum.IN_PROGRESS):
                    orphaned_objectives.append((obj, parent))
        
        if orphaned_objectives:
            source_entities = [
                {
                    "id": str(obj.id),
                    "type": "objective",
                    "name": obj.name,
                    "status": obj.status.value if obj.status else "unknown",
                    "parent_name": parent.name,
                    "parent_status": parent.status.value if parent.status else "unknown"
                }
                for obj, parent in orphaned_objectives[:5]
            ]
            
            insight = Insight(
                title="Active Child Objectives with Inactive Parents",
                description=(
                    f"Identified {len(orphaned_objectives)} active child objectives whose "
                    f"parent objectives are completed, cancelled, or deferred. These may "
                    f"need re-evaluation for strategic alignment."
                ),
                confidence=0.75,
                source_entities=source_entities,
                insight_type="objective_alignment_issue",
                tags=["objectives", "hierarchy", "alignment"]
            )
            
            insights.append(insight)
        
        return insights
    
    def generate_decision_insights(self) -> List[Insight]:
        """Generate insights from decision data.
        
        Returns:
            List of insights
        """
        insights = []
        
        # Get data
        decisions = self.decision_storage.list()
        
        # Only proceed if we have data
        if not decisions:
            return insights
        
        # Insight 1: Decisions without outcomes
        decisions_no_outcomes = [
            d for d in decisions
            if not d.outcome_notes and d.decision_date < (datetime.now() - timedelta(days=90))
        ]
        
        if decisions_no_outcomes:
            source_entities = [
                {
                    "id": str(d.id),
                    "type": "decision",
                    "title": d.title,
                    "date": d.decision_date.strftime("%Y-%m-%d")
                }
                for d in decisions_no_outcomes[:5]
            ]
            
            insight = Insight(
                title="Decisions Without Outcome Documentation",
                description=(
                    f"Found {len(decisions_no_outcomes)} decisions made over 90 days ago "
                    f"that don't have documented outcomes. This may indicate a gap in "
                    f"the decision review process."
                ),
                confidence=0.85,
                source_entities=source_entities,
                insight_type="decision_tracking_gap",
                tags=["decisions", "outcomes", "tracking"]
            )
            
            insights.append(insight)
        
        # Insight 2: Decisions with no stakeholder input
        decisions_no_stakeholders = [
            d for d in decisions
            if not d.stakeholder_input and not d.decided_by
        ]
        
        if decisions_no_stakeholders:
            source_entities = [
                {
                    "id": str(d.id),
                    "type": "decision",
                    "title": d.title,
                    "date": d.decision_date.strftime("%Y-%m-%d")
                }
                for d in decisions_no_stakeholders[:5]
            ]
            
            insight = Insight(
                title="Decisions Without Stakeholder Input",
                description=(
                    f"Identified {len(decisions_no_stakeholders)} decisions that lack documented "
                    f"stakeholder input or decision-makers. These may have limited buy-in."
                ),
                confidence=0.7,
                source_entities=source_entities,
                insight_type="stakeholder_engagement_gap",
                tags=["decisions", "stakeholders", "engagement"]
            )
            
            insights.append(insight)
        
        # Insight 3: Frequent decision patterns
        if len(decisions) >= 10:
            # Extract decision topics/tags
            all_tags = []
            for decision in decisions:
                for tag in decision.tags:
                    all_tags.append(tag.name)
            
            tag_counts = Counter(all_tags)
            common_tags = [tag for tag, count in tag_counts.most_common(5) if count >= 3]
            
            if common_tags:
                source_entities = [
                    {
                        "type": "tag_stats",
                        "tag": tag,
                        "count": count
                    }
                    for tag, count in tag_counts.most_common(5) if count >= 3
                ]
                
                insight = Insight(
                    title="Recurring Decision Themes",
                    description=(
                        f"Identified {len(common_tags)} recurring themes in product decisions: "
                        f"{', '.join(common_tags)}. These represent areas requiring frequent "
                        f"decision-making, which might benefit from established guidelines."
                    ),
                    confidence=0.75,
                    source_entities=source_entities,
                    insight_type="decision_patterns",
                    tags=["decisions", "patterns", "themes"]
                )
                
                insights.append(insight)
        
        # Insight 4: Decisions with limited supporting data
        decisions_limited_evidence = [
            d for d in decisions
            if not d.supporting_data and d.decision_date > (datetime.now() - timedelta(days=180))
        ]
        
        if decisions_limited_evidence:
            source_entities = [
                {
                    "id": str(d.id),
                    "type": "decision",
                    "title": d.title,
                    "date": d.decision_date.strftime("%Y-%m-%d")
                }
                for d in decisions_limited_evidence[:5]
            ]
            
            insight = Insight(
                title="Decisions with Limited Supporting Evidence",
                description=(
                    f"Found {len(decisions_limited_evidence)} recent decisions (within 6 months) "
                    f"that lack documented supporting data. These may be more opinion-based "
                    f"than data-driven decisions."
                ),
                confidence=0.7,
                source_entities=source_entities,
                insight_type="evidence_gap",
                tags=["decisions", "evidence", "data-driven"]
            )
            
            insights.append(insight)
        
        return insights
    
    def generate_stakeholder_insights(self) -> List[Insight]:
        """Generate insights from stakeholder data.
        
        Returns:
            List of insights
        """
        insights = []
        
        # Get data
        stakeholders = self.stakeholder_storage.list()
        perspectives = self.perspective_storage.list()
        
        # Only proceed if we have data
        if not stakeholders:
            return insights
        
        # Insight 1: Stakeholders without recent engagement
        stakeholders_no_engagement = [
            s for s in stakeholders
            if not s.engagement_history or
            (len(s.engagement_history) > 0 and "[" in s.engagement_history[-1] and
             datetime.strptime(s.engagement_history[-1].split("]")[0].strip("[]"), "%Y-%m-%d %H:%M") < 
             (datetime.now() - timedelta(days=90)))
        ]
        
        if stakeholders_no_engagement:
            high_influence_disengaged = [
                s for s in stakeholders_no_engagement
                if s.influence and s.influence.value == "high"
            ]
            
            if high_influence_disengaged:
                source_entities = [
                    {
                        "id": str(s.id),
                        "type": "stakeholder",
                        "name": s.name,
                        "role": s.role.value if s.role else "unknown",
                        "influence": s.influence.value if s.influence else "unknown"
                    }
                    for s in high_influence_disengaged[:5]
                ]
                
                insight = Insight(
                    title="High-Influence Stakeholders with Low Engagement",
                    description=(
                        f"Identified {len(high_influence_disengaged)} high-influence stakeholders "
                        f"with no engagement in the last 90 days. These relationships may "
                        f"need renewed attention."
                    ),
                    confidence=0.8,
                    source_entities=source_entities,
                    insight_type="stakeholder_engagement_gap",
                    tags=["stakeholders", "engagement", "influence"]
                )
                
                insights.append(insight)
        
        # Insight 2: Stakeholders with preference/alignment mismatches
        stakeholders_with_mismatches = []
        
        for stakeholder in stakeholders:
            feature_prefs = []
            objective_alignments = []
            
            for feature_id, pref in stakeholder.feature_preferences.items():
                feature_prefs.append(pref)
            
            for obj_id, alignment in stakeholder.objective_alignment.items():
                objective_alignments.append(alignment)
            
            if feature_prefs and objective_alignments:
                avg_feature_pref = sum(feature_prefs) / len(feature_prefs)
                avg_obj_alignment = sum(objective_alignments) / len(objective_alignments)
                
                # Check for significant mismatch
                if abs(avg_feature_pref - avg_obj_alignment) >= 0.3:
                    stakeholders_with_mismatches.append((
                        stakeholder,
                        avg_feature_pref,
                        avg_obj_alignment
                    ))
        
        if stakeholders_with_mismatches:
            source_entities = [
                {
                    "id": str(s.id),
                    "type": "stakeholder",
                    "name": s.name,
                    "role": s.role.value if s.role else "unknown",
                    "feature_preference": f"{fp:.2f}",
                    "objective_alignment": f"{oa:.2f}"
                }
                for s, fp, oa in stakeholders_with_mismatches[:5]
            ]
            
            insight = Insight(
                title="Stakeholders with Alignment Inconsistencies",
                description=(
                    f"Found {len(stakeholders_with_mismatches)} stakeholders with significant "
                    f"differences between their feature preferences and objective alignments. "
                    f"This may indicate misunderstanding of how features support strategy."
                ),
                confidence=0.7,
                source_entities=source_entities,
                insight_type="alignment_inconsistency",
                tags=["stakeholders", "alignment", "consistency"]
            )
            
            insights.append(insight)
        
        # Insight 3: Stakeholder groups with conflicting perspectives
        if perspectives:
            perspective_by_topic = {}
            
            # Group perspectives by topic
            for perspective in perspectives:
                topic = perspective.topic
                if topic not in perspective_by_topic:
                    perspective_by_topic[topic] = []
                perspective_by_topic[topic].append(perspective)
            
            # Find topics with differing sentiments
            conflict_topics = []
            
            for topic, topic_perspectives in perspective_by_topic.items():
                if len(topic_perspectives) >= 3:  # Minimum number for meaningful divergence
                    positive_count = sum(
                        1 for p in topic_perspectives
                        if p.sentiment and (p.sentiment.value == "positive" or p.sentiment.value == "very_positive")
                    )
                    negative_count = sum(
                        1 for p in topic_perspectives
                        if p.sentiment and (p.sentiment.value == "negative" or p.sentiment.value == "very_negative")
                    )
                    
                    if positive_count >= 1 and negative_count >= 1:
                        conflict_topics.append((topic, topic_perspectives))
            
            if conflict_topics:
                topic_data = []
                
                for topic, topic_perspectives in conflict_topics[:3]:
                    stakeholder_perspectives = []
                    
                    for perspective in topic_perspectives[:5]:
                        # Find stakeholder
                        stakeholder_name = "Unknown"
                        stakeholder_role = "unknown"
                        
                        for stakeholder in stakeholders:
                            if stakeholder.id == perspective.stakeholder_id:
                                stakeholder_name = stakeholder.name
                                stakeholder_role = stakeholder.role.value if stakeholder.role else "unknown"
                                break
                        
                        stakeholder_perspectives.append({
                            "id": str(perspective.id),
                            "stakeholder_name": stakeholder_name,
                            "stakeholder_role": stakeholder_role,
                            "sentiment": perspective.sentiment.value if perspective.sentiment else "neutral"
                        })
                    
                    topic_data.append({
                        "topic": topic,
                        "perspectives": stakeholder_perspectives
                    })
                
                insight = Insight(
                    title="Topics with Stakeholder Disagreement",
                    description=(
                        f"Identified {len(conflict_topics)} topics where stakeholders have significantly "
                        f"different perspectives: {', '.join(topic for topic, _ in conflict_topics[:3])}. "
                        f"These may require conflict resolution or further discussion."
                    ),
                    confidence=0.8,
                    source_entities=topic_data,
                    insight_type="stakeholder_conflict",
                    tags=["stakeholders", "perspectives", "conflicts"]
                )
                
                insights.append(insight)
        
        # Insight 4: Stakeholder role representation
        role_counts = Counter()
        for stakeholder in stakeholders:
            if stakeholder.role:
                role_counts[stakeholder.role.value] += 1
        
        # Find missing or underrepresented roles
        key_roles = ["customer", "engineering", "product", "design", "sales", "marketing"]
        missing_roles = [role for role in key_roles if role_counts.get(role, 0) == 0]
        
        if missing_roles:
            source_entities = [
                {
                    "type": "role_stats",
                    "role": role,
                    "count": 0
                }
                for role in missing_roles
            ]
            
            insight = Insight(
                title="Missing Stakeholder Representation",
                description=(
                    f"Found {len(missing_roles)} key stakeholder roles with no representation: "
                    f"{', '.join(missing_roles)}. This may lead to blind spots in product planning."
                ),
                confidence=0.9,
                source_entities=source_entities,
                insight_type="representation_gap",
                tags=["stakeholders", "roles", "representation"]
            )
            
            insights.append(insight)
        
        return insights
    
    def generate_competitive_insights(self) -> List[Insight]:
        """Generate insights from competitive analysis data.
        
        Returns:
            List of insights
        """
        insights = []
        
        # Get data
        competitors = self.competitor_storage.list()
        features = self.feature_storage.list()
        
        # Only proceed if we have data
        if not competitors:
            return insights
        
        # Insight 1: Common competitor strengths
        all_strengths = []
        for competitor in competitors:
            all_strengths.extend(competitor.strengths)
        
        strength_counts = Counter(all_strengths)
        common_strengths = [
            (strength, count) for strength, count in strength_counts.most_common(5)
            if count >= 2
        ]
        
        if common_strengths:
            source_entities = [
                {
                    "type": "strength_stats",
                    "strength": strength,
                    "count": count,
                    "competitors": [
                        c.name for c in competitors
                        if strength in c.strengths
                    ][:3]
                }
                for strength, count in common_strengths
            ]
            
            insight = Insight(
                title="Common Competitor Strengths",
                description=(
                    f"Identified {len(common_strengths)} strengths shared by multiple competitors: "
                    f"{', '.join(s for s, _ in common_strengths)}. These likely represent "
                    f"critical capabilities your product should match or differentiate from."
                ),
                confidence=0.85,
                source_entities=source_entities,
                insight_type="competitive_pattern",
                tags=["competitors", "strengths", "market"]
            )
            
            insights.append(insight)
        
        # Insight 2: Feature parity gaps
        if features:
            feature_parity_map = {}
            
            for feature in features:
                # Find how many competitors have this feature
                competitor_has_feature = []
                
                for competitor in competitors:
                    feature_name = feature.name.lower()
                    
                    # Check if competitor has this feature
                    for comp_feature, has_feature in competitor.feature_comparison.items():
                        if has_feature and feature_name in comp_feature.lower():
                            competitor_has_feature.append(competitor.name)
                            break
                
                feature_parity_map[feature.id] = {
                    "feature": feature,
                    "competitor_count": len(competitor_has_feature),
                    "competitors": competitor_has_feature
                }
            
            # Find features that most competitors have but are not completed
            common_competitor_features = [
                info for _, info in feature_parity_map.items()
                if info["competitor_count"] >= 3 and
                info["feature"].status != StatusEnum.COMPLETED and
                info["feature"].status != StatusEnum.IN_PROGRESS
            ]
            
            if common_competitor_features:
                source_entities = [
                    {
                        "id": str(info["feature"].id),
                        "type": "feature",
                        "name": info["feature"].name,
                        "status": info["feature"].status.value if info["feature"].status else "unknown",
                        "competitor_count": info["competitor_count"],
                        "competitors": info["competitors"][:3]
                    }
                    for info in common_competitor_features[:5]
                ]
                
                insight = Insight(
                    title="Feature Parity Gaps",
                    description=(
                        f"Found {len(common_competitor_features)} features that are common among "
                        f"competitors but not yet completed in your product. These may represent "
                        f"competitive disadvantages."
                    ),
                    confidence=0.8,
                    source_entities=source_entities,
                    insight_type="parity_gap",
                    tags=["competitors", "features", "parity"]
                )
                
                insights.append(insight)
        
        # Insight 3: Emerging market segments
        all_segments = []
        for competitor in competitors:
            all_segments.extend(competitor.target_segments)
        
        segment_counts = Counter(all_segments)
        
        # Find segments targeted by just 1-2 competitors (potential emerging segments)
        emerging_segments = [
            (segment, count) for segment, count in segment_counts.items()
            if 1 <= count <= 2
        ]
        
        if emerging_segments:
            source_entities = [
                {
                    "type": "segment_stats",
                    "segment": segment,
                    "count": count,
                    "competitors": [
                        c.name for c in competitors
                        if segment in c.target_segments
                    ]
                }
                for segment, count in emerging_segments[:5]
            ]
            
            insight = Insight(
                title="Potential Emerging Market Segments",
                description=(
                    f"Identified {len(emerging_segments)} market segments that only a few competitors "
                    f"are targeting: {', '.join(s for s, _ in emerging_segments[:3])}. "
                    f"These may represent emerging opportunities."
                ),
                confidence=0.7,
                source_entities=source_entities,
                insight_type="market_opportunity",
                tags=["competitors", "segments", "opportunities"]
            )
            
            insights.append(insight)
        
        # Insight 4: High threat competitors without differentiation
        high_threat_competitors = [
            c for c in competitors
            if c.threat_level and c.threat_level >= 0.7
        ]
        
        if high_threat_competitors and features:
            competitors_without_diff = []
            
            for competitor in high_threat_competitors:
                # Count feature differentiation
                diff_count = 0
                
                for feature in features:
                    if feature.status == StatusEnum.COMPLETED:
                        # Check if competitor has this feature
                        has_feature = False
                        
                        for comp_feature, comp_has_feature in competitor.feature_comparison.items():
                            if comp_has_feature and feature.name.lower() in comp_feature.lower():
                                has_feature = True
                                break
                        
                        if not has_feature:
                            diff_count += 1
                
                if diff_count <= 2:  # Very little differentiation
                    competitors_without_diff.append({
                        "competitor": competitor,
                        "diff_count": diff_count
                    })
            
            if competitors_without_diff:
                source_entities = [
                    {
                        "id": str(info["competitor"].id),
                        "type": "competitor",
                        "name": info["competitor"].name,
                        "threat_level": info["competitor"].threat_level,
                        "diff_count": info["diff_count"]
                    }
                    for info in competitors_without_diff[:5]
                ]
                
                insight = Insight(
                    title="High-Threat Competitors Without Differentiation",
                    description=(
                        f"Found {len(competitors_without_diff)} high-threat competitors against which "
                        f"your product has minimal feature differentiation. This may indicate "
                        f"strategic positioning challenges."
                    ),
                    confidence=0.85,
                    source_entities=source_entities,
                    insight_type="differentiation_risk",
                    tags=["competitors", "threat", "differentiation"]
                )
                
                insights.append(insight)
        
        return insights
    
    def generate_cross_domain_insights(self) -> List[Insight]:
        """Generate insights that span multiple knowledge domains.
        
        Returns:
            List of insights
        """
        insights = []
        
        # Get data from various domains
        feedback_items = self.feedback_storage.list()
        features = self.feature_storage.list()
        objectives = self.objective_storage.list()
        decisions = self.decision_storage.list()
        stakeholders = self.stakeholder_storage.list()
        competitors = self.competitor_storage.list()
        
        # Only proceed if we have sufficient data
        if not (features and (feedback_items or objectives or stakeholders)):
            return insights
        
        # Insight 1: Features with feedback but low priority
        if feedback_items:
            feature_feedback_counts = {}
            
            # Count feedback mentions for each feature
            for feature in features:
                feedback_count = sum(
                    1 for fb in feedback_items
                    if feature.id in fb.extracted_features or feature.id in fb.feature_ids
                )
                
                if feedback_count >= 3:  # Minimum threshold to be significant
                    feature_feedback_counts[feature.id] = {
                        "feature": feature,
                        "feedback_count": feedback_count
                    }
            
            # Find features with high feedback but low priority
            high_feedback_low_priority = [
                info for _, info in feature_feedback_counts.items()
                if info["feedback_count"] >= 5 and
                info["feature"].priority_score and info["feature"].priority_score < 0.5 and
                info["feature"].status != StatusEnum.COMPLETED and
                info["feature"].status != StatusEnum.CANCELLED
            ]
            
            if high_feedback_low_priority:
                source_entities = [
                    {
                        "id": str(info["feature"].id),
                        "type": "feature",
                        "name": info["feature"].name,
                        "priority": info["feature"].priority_score,
                        "feedback_count": info["feedback_count"]
                    }
                    for info in high_feedback_low_priority[:5]
                ]
                
                insight = Insight(
                    title="High Feedback Features with Low Priority",
                    description=(
                        f"Identified {len(high_feedback_low_priority)} features with significant user feedback "
                        f"but relatively low priority scores. These may represent misaligned "
                        f"priorities between user needs and product planning."
                    ),
                    confidence=0.8,
                    source_entities=source_entities,
                    insight_type="feedback_priority_mismatch",
                    tags=["features", "feedback", "priority"]
                )
                
                insights.append(insight)
        
        # Insight 2: Disconnected decisions
        if decisions and (objectives or features):
            disconnected_decisions = [
                d for d in decisions
                if not d.objective_ids and not d.feature_ids and
                d.decision_date > (datetime.now() - timedelta(days=180))
            ]
            
            if disconnected_decisions:
                source_entities = [
                    {
                        "id": str(d.id),
                        "type": "decision",
                        "title": d.title,
                        "date": d.decision_date.strftime("%Y-%m-%d")
                    }
                    for d in disconnected_decisions[:5]
                ]
                
                insight = Insight(
                    title="Disconnected Strategic Decisions",
                    description=(
                        f"Found {len(disconnected_decisions)} recent decisions not linked to "
                        f"any objectives or features. These decisions may lack traceability "
                        f"to product strategy or implementation."
                    ),
                    confidence=0.75,
                    source_entities=source_entities,
                    insight_type="decision_traceability_gap",
                    tags=["decisions", "traceability", "strategy"]
                )
                
                insights.append(insight)
        
        # Insight 3: Competitor strengths without corresponding objectives
        if competitors and objectives:
            # Collect common competitor strengths
            all_strengths = []
            for competitor in competitors:
                all_strengths.extend(competitor.strengths)
            
            strength_counts = Counter(all_strengths)
            common_strengths = [
                strength for strength, count in strength_counts.most_common(10)
                if count >= 2
            ]
            
            if common_strengths:
                # Check if objectives address these competitor strengths
                unaddressed_strengths = []
                
                for strength in common_strengths:
                    addressed = False
                    
                    for objective in objectives:
                        if strength.lower() in objective.name.lower() or strength.lower() in objective.description.lower():
                            addressed = True
                            break
                    
                    if not addressed:
                        unaddressed_strengths.append(strength)
                
                if unaddressed_strengths:
                    source_entities = [
                        {
                            "type": "strength",
                            "name": strength,
                            "competitors": [
                                c.name for c in competitors
                                if strength in c.strengths
                            ][:3]
                        }
                        for strength in unaddressed_strengths[:5]
                    ]
                    
                    insight = Insight(
                        title="Competitor Strengths Not Addressed in Strategy",
                        description=(
                            f"Identified {len(unaddressed_strengths)} common competitor strengths "
                            f"that don't appear to be addressed in your strategic objectives: "
                            f"{', '.join(unaddressed_strengths[:3])}. These may represent "
                            f"strategic blind spots."
                        ),
                        confidence=0.7,
                        source_entities=source_entities,
                        insight_type="strategic_gap",
                        tags=["competitors", "strategy", "objectives"]
                    )
                    
                    insights.append(insight)
        
        # Insight 4: Stakeholder concerns without corresponding features
        if stakeholders and features:
            # Collect stakeholder concerns
            all_concerns = []
            for stakeholder in stakeholders:
                all_concerns.extend(stakeholder.key_concerns)
            
            if all_concerns:
                # Check if features address these concerns
                unaddressed_concerns = []
                
                for concern in all_concerns:
                    addressed = False
                    
                    for feature in features:
                        if (concern.lower() in feature.name.lower() or 
                            concern.lower() in feature.description.lower()):
                            addressed = True
                            break
                    
                    if not addressed:
                        unaddressed_concerns.append(concern)
                
                # Remove duplicates while preserving order
                unique_unaddressed = []
                seen = set()
                for concern in unaddressed_concerns:
                    if concern not in seen:
                        unique_unaddressed.append(concern)
                        seen.add(concern)
                
                if unique_unaddressed:
                    source_entities = [
                        {
                            "type": "concern",
                            "text": concern,
                            "stakeholders": [
                                s.name for s in stakeholders
                                if concern in s.key_concerns
                            ][:3]
                        }
                        for concern in unique_unaddressed[:5]
                    ]
                    
                    insight = Insight(
                        title="Stakeholder Concerns Without Corresponding Features",
                        description=(
                            f"Found {len(unique_unaddressed)} stakeholder concerns not clearly "
                            f"addressed by current features: {', '.join(unique_unaddressed[:3])}. "
                            f"These may represent important stakeholder needs that aren't being met."
                        ),
                        confidence=0.7,
                        source_entities=source_entities,
                        insight_type="stakeholder_need_gap",
                        tags=["stakeholders", "concerns", "features"]
                    )
                    
                    insights.append(insight)
        
        return insights
    
    def generate_all_insights(self) -> List[InsightGroup]:
        """Generate all insights from all domains.
        
        Returns:
            List of insight groups
        """
        # Generate insights from each domain
        feedback_insights = self.generate_feedback_insights()
        feature_insights = self.generate_feature_insights()
        objective_insights = self.generate_objective_insights()
        decision_insights = self.generate_decision_insights()
        stakeholder_insights = self.generate_stakeholder_insights()
        competitive_insights = self.generate_competitive_insights()
        cross_domain_insights = self.generate_cross_domain_insights()
        
        # Group insights by domain
        insight_groups = []
        
        if feedback_insights:
            insight_groups.append(InsightGroup(
                title="Feedback Insights",
                insights=feedback_insights,
                insight_type="feedback"
            ))
        
        if feature_insights:
            insight_groups.append(InsightGroup(
                title="Feature Insights",
                insights=feature_insights,
                insight_type="feature"
            ))
        
        if objective_insights:
            insight_groups.append(InsightGroup(
                title="Strategic Objective Insights",
                insights=objective_insights,
                insight_type="objective"
            ))
        
        if decision_insights:
            insight_groups.append(InsightGroup(
                title="Decision Insights",
                insights=decision_insights,
                insight_type="decision"
            ))
        
        if stakeholder_insights:
            insight_groups.append(InsightGroup(
                title="Stakeholder Insights",
                insights=stakeholder_insights,
                insight_type="stakeholder"
            ))
        
        if competitive_insights:
            insight_groups.append(InsightGroup(
                title="Competitive Insights",
                insights=competitive_insights,
                insight_type="competitive"
            ))
        
        if cross_domain_insights:
            insight_groups.append(InsightGroup(
                title="Cross-Domain Insights",
                insights=cross_domain_insights,
                insight_type="cross-domain"
            ))
        
        return insight_groups
    
    def generate_trend_analysis(
        self, days: int = 180, interval_days: int = 30
    ) -> List[TrendData]:
        """Generate trend analysis data.
        
        Args:
            days: Number of days to analyze
            interval_days: Size of each interval in days
            
        Returns:
            List of trend data
        """
        trends = []
        
        # Calculate time periods
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Create time intervals
        intervals = []
        current_date = start_date
        
        while current_date < end_date:
            interval_end = min(current_date + timedelta(days=interval_days), end_date)
            intervals.append((current_date, interval_end))
            current_date = interval_end
        
        # Format interval labels
        interval_labels = [
            f"{start.strftime('%m/%d/%y')}-{end.strftime('%m/%d/%y')}"
            for start, end in intervals
        ]
        
        # Get data
        feedback_items = self.feedback_storage.list()
        features = self.feature_storage.list()
        objectives = self.objective_storage.list()
        decisions = self.decision_storage.list()
        
        # Trend 1: Feedback volume over time
        if feedback_items:
            feedback_counts = []
            
            for start, end in intervals:
                count = sum(
                    1 for fb in feedback_items
                    if start <= fb.created_at < end
                )
                feedback_counts.append(count)
            
            # Only add if we have non-zero data
            if any(feedback_counts):
                trends.append(TrendData(
                    title="Feedback Volume Trend",
                    time_periods=interval_labels,
                    series={"Feedback Volume": feedback_counts}
                ))
        
        # Trend 2: Feature completion over time
        if features:
            feature_completion_counts = []
            feature_creation_counts = []
            
            for start, end in intervals:
                completion_count = sum(
                    1 for f in features
                    if f.status == StatusEnum.COMPLETED and
                    f.updated_at and start <= f.updated_at < end
                )
                
                creation_count = sum(
                    1 for f in features
                    if start <= f.created_at < end
                )
                
                feature_completion_counts.append(completion_count)
                feature_creation_counts.append(creation_count)
            
            # Only add if we have non-zero data
            if any(feature_completion_counts) or any(feature_creation_counts):
                trends.append(TrendData(
                    title="Feature Lifecycle Trend",
                    time_periods=interval_labels,
                    series={
                        "Features Created": feature_creation_counts,
                        "Features Completed": feature_completion_counts
                    }
                ))
        
        # Trend 3: Objective progress over time
        if objectives:
            progress_by_interval = []
            
            for start, end in intervals:
                # Find objectives that existed during this interval
                interval_objectives = [
                    obj for obj in objectives
                    if obj.created_at < end and
                    (obj.status != StatusEnum.COMPLETED or obj.updated_at >= start)
                ]
                
                # Calculate average progress
                progress_sum = 0
                count = 0
                
                for obj in interval_objectives:
                    if obj.metric_current is not None and obj.metric_target is not None and obj.metric_target > 0:
                        progress = (obj.metric_current / obj.metric_target) * 100.0
                        progress_sum += progress
                        count += 1
                
                avg_progress = progress_sum / count if count > 0 else 0
                progress_by_interval.append(avg_progress)
            
            # Only add if we have non-zero data
            if any(progress_by_interval):
                trends.append(TrendData(
                    title="Objective Progress Trend",
                    time_periods=interval_labels,
                    series={"Average Objective Progress (%)": progress_by_interval}
                ))
        
        # Trend 4: Decision frequency over time
        if decisions:
            decision_counts = []
            
            for start, end in intervals:
                count = sum(
                    1 for d in decisions
                    if start <= d.decision_date < end
                )
                decision_counts.append(count)
            
            # Only add if we have non-zero data
            if any(decision_counts):
                trends.append(TrendData(
                    title="Decision Frequency Trend",
                    time_periods=interval_labels,
                    series={"Decision Count": decision_counts}
                ))
        
        return trends