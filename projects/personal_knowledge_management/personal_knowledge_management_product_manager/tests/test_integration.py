"""
Integration tests for the ProductInsight system.

This module tests the integration between different components of the
ProductInsight system, focusing on end-to-end scenarios.
"""

import os
from datetime import datetime
from uuid import uuid4

import pytest

from product_insight.competitive import CompetitiveAnalyzer
from product_insight.decisions import DecisionManager
from product_insight.discovery import InsightEngine, SearchEngine, SearchQuery
from product_insight.feedback import FeedbackManager
from product_insight.models import (
    Competitor,
    Decision,
    Feature,
    FeedbackItem,
    SentimentEnum,
    SourceEnum,
    Stakeholder,
    StakeholderPerspective,
    StakeholderRoleEnum,
    StatusEnum,
    StrategicObjective,
    Tag,
)
from product_insight.prioritization import (
    FeaturePrioritizer,
    PrioritizationMethod,
)
from product_insight.stakeholders import StakeholderManager
from product_insight.strategy import ObjectiveManager

from tests.fixtures.fixtures import (
    feedback_manager,
    mock_data_generator,
    populated_storage_dir,
    temp_dir,
)


class TestEndToEndScenarios:
    """Tests for end-to-end scenarios."""

    def test_feature_prioritization_workflow(self, populated_storage_dir):
        """Test the complete feature prioritization workflow."""
        # Initialize managers
        feedback_mgr = FeedbackManager(storage_dir=populated_storage_dir)
        prioritizer = FeaturePrioritizer(storage_dir=populated_storage_dir)
        objective_mgr = ObjectiveManager(storage_dir=populated_storage_dir)

        # Step 1: Create multiple feedback items related to the same feature
        feedback_items = [
            FeedbackItem(
                content="I really need the ability to export data to Excel. This would save me hours every month.",
                source=SourceEnum.CUSTOMER_INTERVIEW,
                customer_segment="Enterprise"
            ),
            FeedbackItem(
                content="Your competitors all have Excel export capabilities. Without this, we might need to look elsewhere.",
                source=SourceEnum.SALES_CALL,
                customer_segment="Enterprise"
            ),
            FeedbackItem(
                content="Excel export would be nice to have, but it's not critical for me.",
                source=SourceEnum.SURVEY,
                customer_segment="Basic"
            )
        ]

        # Add and process feedback
        processed_items = [feedback_mgr.add_feedback(item, process=True) for item in feedback_items]

        # Step 2: Cluster the feedback
        clustering_result = feedback_mgr.cluster_feedback()

        # There should be at least one cluster related to exports
        export_cluster = None
        for cluster in clustering_result.clusters:
            if 'export' in cluster.name.lower() or any('export' in term.lower() for term in cluster.common_terms):
                export_cluster = cluster
                break

        # Step 3: Create strategic objectives
        primary_objective = StrategicObjective(
            name="Improve Data Export Capabilities",
            description="Enhance the system's ability to export data in various formats",
            status=StatusEnum.IN_PROGRESS,
            priority=PriorityEnum.HIGH
        )

        secondary_objective = StrategicObjective(
            name="Increase User Productivity",
            description="Enable users to accomplish tasks more efficiently",
            status=StatusEnum.IN_PROGRESS,
            priority=PriorityEnum.MEDIUM
        )

        saved_primary = objective_mgr.add_objective(primary_objective)
        saved_secondary = objective_mgr.add_objective(secondary_objective)

        # Step 4: Create features with varying characteristics
        features = [
            Feature(
                name="Excel Export",
                description="Allow users to export data to Excel format",
                status=StatusEnum.PLANNED,
                effort_estimate=4.0,
                value_estimate=9.0,
                feedback_ids=[item.id for item in processed_items],
                feedback_cluster_ids=[export_cluster.id] if export_cluster else [],
                objective_ids=[saved_primary.id, saved_secondary.id],
                risk_level=0.3
            ),
            Feature(
                name="CSV Export",
                description="Allow users to export data to CSV format",
                status=StatusEnum.PLANNED,
                effort_estimate=2.0,
                value_estimate=7.0,
                objective_ids=[saved_primary.id],
                risk_level=0.2
            ),
            Feature(
                name="PDF Export",
                description="Allow users to export data to PDF format",
                status=StatusEnum.PLANNED,
                effort_estimate=5.0,
                value_estimate=8.0,
                objective_ids=[saved_primary.id],
                risk_level=0.4
            ),
            Feature(
                name="API Access",
                description="Provide API for programmatic data access",
                status=StatusEnum.PLANNED,
                effort_estimate=8.0,
                value_estimate=9.0,
                objective_ids=[saved_primary.id, saved_secondary.id],
                risk_level=0.6
            )
        ]

        # Add features
        saved_features = [prioritizer.add_feature(feature) for feature in features]
        feature_ids = [feature.id for feature in saved_features]

        # Step 5: Compare prioritization across different methods
        comparison = prioritizer.compare_prioritization_methods(feature_ids)

        # Check that all methods are compared
        for method in PrioritizationMethod:
            assert method.value in comparison
            assert len(comparison[method.value]) == len(features)

        # Step 6: Create custom prioritization criteria
        criteria = PrioritizationCriteria(
            method=PrioritizationMethod.WEIGHTED,
            weight_strategic=2.0,  # Higher weight for strategic alignment
            weight_feedback=1.5,   # Higher weight for feedback
            weight_value=1.0,      # Normal weight for value
            weight_effort=1.0,     # Normal weight for effort
            weight_risk=1.5        # Higher weight for risk
        )

        # Step 7: Prioritize with custom criteria
        result = prioritizer.prioritize_features(
            feature_ids=feature_ids,
            method=PrioritizationMethod.WEIGHTED,
            criteria=criteria
        )

        # Check prioritization results
        assert result.method == PrioritizationMethod.WEIGHTED
        assert result.criteria == criteria
        assert len(result.scored_features) == len(features)

        # Features should be sorted by score (highest first)
        scores = [scorecard.total_score for _, scorecard in result.scored_features]
        assert scores == sorted(scores, reverse=True)

        # Step 8: Create a value/effort matrix
        from product_insight.prioritization import PrioritizationVisualizer

        # Get features from storage to ensure they have updated priority scores
        updated_features = [prioritizer.get_feature(feature_id) for feature_id in feature_ids]

        # Create matrix
        matrix = PrioritizationVisualizer.create_value_effort_matrix(updated_features)

        # Check matrix structure
        assert hasattr(matrix, 'high_value_low_effort')
        assert hasattr(matrix, 'high_value_high_effort')
        assert hasattr(matrix, 'low_value_low_effort')
        assert hasattr(matrix, 'low_value_high_effort')

        # Excel Export should be in high value zone
        excel_feature = next(f for f in updated_features if f.name == "Excel Export")
        csv_feature = next(f for f in updated_features if f.name == "CSV Export")

        # Check quadrant placements based on value/effort
        high_value_features = [f for f, _ in matrix.high_value_low_effort + matrix.high_value_high_effort]
        low_effort_features = [f for f, _ in matrix.high_value_low_effort + matrix.low_value_low_effort]

        assert excel_feature in high_value_features
        assert csv_feature in low_effort_features

        # Step 9: Get top features
        top_features = prioritizer.get_top_features(limit=2)
        assert len(top_features) == 2

        # Top features should be sorted by score
        assert top_features[0][1] >= top_features[1][1]

        # Step 10: Generate a distribution visualization
        distribution = PrioritizationVisualizer.create_priority_distribution(updated_features)
        distribution_json = PrioritizationVisualizer.priority_distribution_to_json(distribution)

        # Check distribution structure
        assert isinstance(distribution, dict)
        assert len(distribution) > 0
        assert isinstance(distribution_json, str)
        assert "range" in distribution_json
        assert "count" in distribution_json
    
    def test_feedback_to_feature_lifecycle(self, populated_storage_dir):
        """Test the lifecycle from feedback to feature to decision."""
        # Initialize managers
        feedback_mgr = FeedbackManager(storage_dir=populated_storage_dir)
        prioritizer = FeaturePrioritizer(storage_dir=populated_storage_dir)
        objective_mgr = ObjectiveManager(storage_dir=populated_storage_dir)
        decision_mgr = DecisionManager(storage_dir=populated_storage_dir)
        stakeholder_mgr = StakeholderManager(storage_dir=populated_storage_dir)
        
        # Step 1: Add and process feedback
        feedback = FeedbackItem(
            content="I would like to be able to export reports to PDF format. This would really help with sharing data.",
            source=SourceEnum.CUSTOMER_INTERVIEW,
            customer_segment="Enterprise"
        )
        
        processed_feedback = feedback_mgr.add_feedback(feedback, process=True)
        
        # Verify feedback processing
        assert processed_feedback.processed is True
        assert processed_feedback.sentiment is not None
        assert len(processed_feedback.extracted_features) > 0
        assert "export" in " ".join(processed_feedback.extracted_features).lower()
        assert processed_feedback.impact_score is not None
        
        # Step 2: Cluster the feedback
        clustering_result = feedback_mgr.cluster_feedback()
        
        # At this point, the feedback might be in a cluster or unclustered
        # depending on how it relates to other existing feedback
        assert processed_feedback.id in [
            fb.id for fb in clustering_result.unclustered_items
        ] or processed_feedback.cluster_id is not None
        
        # Step 3: Create a feature based on the feedback
        feature = Feature(
            name="PDF Export",
            description="Allow users to export reports to PDF format",
            status=StatusEnum.PLANNED,
            effort_estimate=5.0,
            value_estimate=8.0,
            feedback_ids=[processed_feedback.id]
        )
        
        saved_feature = prioritizer.add_feature(feature)
        
        # Step 4: Create a strategic objective
        objective = StrategicObjective(
            name="Improve Export Capabilities",
            description="Enhance the system's ability to export data in various formats",
            status=StatusEnum.IN_PROGRESS
        )
        
        saved_objective = objective_mgr.add_objective(objective)
        
        # Link feature to objective
        saved_feature.objective_ids = [saved_objective.id]
        updated_feature = prioritizer.update_feature(saved_feature)
        
        # Step 5: Prioritize the feature
        prioritized_feature, scorecard = prioritizer.prioritize_feature(
            updated_feature.id,
            PrioritizationMethod.VALUE_EFFORT
        )
        
        # Verify prioritization
        assert prioritized_feature.priority_score is not None
        assert prioritized_feature.priority_method == PrioritizationMethod.VALUE_EFFORT.value
        assert scorecard.value_effort_score is not None
        
        # Step 6: Create a stakeholder
        stakeholder = Stakeholder(
            name="John Smith",
            role=StakeholderRoleEnum.PRODUCT,
            influence="high"
        )
        
        saved_stakeholder = stakeholder_mgr.add_stakeholder(stakeholder)
        
        # Step 7: Add a stakeholder perspective
        perspective = StakeholderPerspective(
            stakeholder_id=saved_stakeholder.id,
            topic="Export Features",
            perspective="I think PDF export is a high-priority feature that will benefit our enterprise customers.",
            sentiment=SentimentEnum.POSITIVE,
            related_feature_ids=[updated_feature.id],
            related_objective_ids=[saved_objective.id]
        )
        
        saved_perspective = stakeholder_mgr.add_stakeholder_perspective(perspective)
        
        # Step 8: Make a decision
        decision = Decision(
            title="Implement PDF Export Feature",
            description="Decision to implement PDF export capability",
            context="Enterprise customers have frequently requested the ability to export reports as PDFs.",
            rationale="This feature aligns with our strategic objective to improve export capabilities and has high value relative to effort.",
            decision_date=datetime.now(),
            decided_by=[saved_stakeholder.id],
            feature_ids=[updated_feature.id],
            objective_ids=[saved_objective.id]
        )
        
        saved_decision = decision_mgr.add_decision(decision)
        
        # Step 9: Update feature status
        updated_feature.status = StatusEnum.IN_PROGRESS
        updated_feature = prioritizer.update_feature(updated_feature)
        
        # Verify the complete lifecycle
        # Check feature references feedback
        assert processed_feedback.id in updated_feature.feedback_ids
        
        # Check feature is linked to objective
        assert saved_objective.id in updated_feature.objective_ids
        
        # Check decision references feature and objective
        assert updated_feature.id in saved_decision.feature_ids
        assert saved_objective.id in saved_decision.objective_ids
        
        # Check perspective is linked to feature and objective
        assert updated_feature.id in saved_perspective.related_feature_ids
        assert saved_objective.id in saved_perspective.related_objective_ids
    
    def test_search_and_insights(self, populated_storage_dir):
        """Test search functionality and insight generation."""
        # Initialize engines
        search_engine = SearchEngine(storage_dir=populated_storage_dir)
        insight_engine = InsightEngine(storage_dir=populated_storage_dir)
        
        # Build the search index
        search_engine.build_index()
        
        # Test 1: Search across all domains
        query = SearchQuery(
            query="export",
            include_feedback=True,
            include_features=True,
            include_objectives=True,
            include_decisions=True,
            limit=10
        )
        
        results = search_engine.search(query)
        
        # Check search results
        assert results.total_count >= 0
        assert results.execution_time_ms > 0
        
        # If results found, check facets
        if results.total_count > 0:
            assert "entity_type" in results.facets
            assert sum(results.facets["entity_type"].values()) == results.total_count
        
        # Test 2: Find related entities
        # First find a feature
        feature_query = SearchQuery(
            query="feature",
            include_features=True,
            include_feedback=False,
            include_objectives=False,
            include_decisions=False,
            include_competitors=False,
            include_stakeholders=False,
            limit=1
        )
        
        feature_results = search_engine.search(feature_query)
        
        # If a feature is found, find related entities
        if feature_results.total_count > 0:
            feature_id = feature_results.results[0].entity_id
            related = search_engine.find_related_entities(
                feature_id, "feature", max_results=5
            )
            
            # Check related entities
            assert isinstance(related, dict)
            assert set(related.keys()) == {
                "feedback", "feature", "objective", "decision", 
                "competitor", "stakeholder", "perspective"
            }
        
        # Test 3: Generate insights
        # This may not produce any insights with limited test data
        insight_groups = insight_engine.generate_all_insights()
        
        # Check insight structure if any found
        if insight_groups:
            # At least check the structure
            assert isinstance(insight_groups, list)
            if insight_groups:
                assert hasattr(insight_groups[0], "title")
                assert hasattr(insight_groups[0], "insights")
                assert hasattr(insight_groups[0], "insight_type")
        
        # Test 4: Generate trend analysis
        trends = insight_engine.generate_trend_analysis(days=90, interval_days=30)
        
        # Check trend structure if any found
        if trends:
            assert isinstance(trends, list)
            if trends:
                assert hasattr(trends[0], "title")
                assert hasattr(trends[0], "time_periods")
                assert hasattr(trends[0], "series")
    
    def test_competitive_analysis_workflow(self, populated_storage_dir):
        """Test competitive analysis workflow."""
        # Initialize analyzers and managers
        competitive_analyzer = CompetitiveAnalyzer(storage_dir=populated_storage_dir)
        feature_prioritizer = FeaturePrioritizer(storage_dir=populated_storage_dir)
        
        # Step 1: Add a competitor
        competitor = Competitor(
            name="CompeteCorp",
            description="A major competitor in our market",
            market_share=15.0,
            strengths=["User-friendly interface", "Mobile experience"],
            weaknesses=["Limited reporting", "No custom exports"],
            feature_comparison={
                "Dashboard": True,
                "Custom Reports": True,
                "Mobile App": True,
                "PDF Export": False,
                "API Access": False
            },
            threat_level=0.7
        )
        
        saved_competitor = competitive_analyzer.add_competitor(competitor)
        
        # Step 2: Add features for comparison
        our_features = [
            Feature(
                name="Dashboard",
                description="Interactive dashboard",
                status=StatusEnum.COMPLETED
            ),
            Feature(
                name="Custom Reports",
                description="Create custom reports",
                status=StatusEnum.COMPLETED
            ),
            Feature(
                name="PDF Export",
                description="Export reports as PDFs",
                status=StatusEnum.PLANNED
            ),
            Feature(
                name="API Access",
                description="API for programmatic access",
                status=StatusEnum.IN_PROGRESS
            )
        ]
        
        # Add features
        saved_features = [feature_prioritizer.add_feature(feature) for feature in our_features]
        feature_names = [feature.name for feature in saved_features]
        
        # Step 3: Create a feature matrix
        matrix = competitive_analyzer.create_feature_matrix([saved_competitor.id])
        
        # Check matrix structure
        assert saved_competitor.name in matrix.competitors
        assert matrix.matrix[saved_competitor.name] is not None
        
        # Step 4: Find feature gaps
        gaps = competitive_analyzer.find_feature_gaps(feature_names, [saved_competitor.id])
        
        # Check gaps
        assert saved_competitor.name in gaps
        assert "Mobile App" in gaps[saved_competitor.name]
        
        # Step 5: Find competitive advantages
        advantages = competitive_analyzer.find_competitive_advantages(feature_names, [saved_competitor.id])
        
        # Check advantages
        assert saved_competitor.name in advantages
        assert "PDF Export" in advantages[saved_competitor.name] or "API Access" in advantages[saved_competitor.name]