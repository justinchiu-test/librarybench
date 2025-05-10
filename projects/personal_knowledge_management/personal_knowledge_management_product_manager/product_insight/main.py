"""
Main entry point for the ProductInsight application.

This module provides the main entry point and initialization for the
ProductInsight system.
"""

import argparse
import os
import sys
from pathlib import Path

from product_insight import __version__
from product_insight.competitive import CompetitiveAnalyzer
from product_insight.decisions import DecisionManager
from product_insight.discovery import InsightEngine, SearchEngine
from product_insight.feedback import FeedbackManager
from product_insight.prioritization import FeaturePrioritizer
from product_insight.stakeholders import StakeholderManager
from product_insight.strategy import ObjectiveManager


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="ProductInsight - Strategic Product Knowledge System")
    
    parser.add_argument(
        "--version", action="version", version=f"ProductInsight v{__version__}"
    )
    
    parser.add_argument(
        "--data-dir",
        type=str,
        default=os.path.expanduser("~/.product_insight"),
        help="Directory for storing data (default: ~/.product_insight)"
    )
    
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize the data directory structure"
    )
    
    # Add subcommands for different components
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Feedback commands
    feedback_parser = subparsers.add_parser("feedback", help="Feedback management")
    feedback_subparsers = feedback_parser.add_subparsers(dest="feedback_command")
    
    feedback_cluster_parser = feedback_subparsers.add_parser("cluster", help="Cluster feedback")
    feedback_cluster_parser.add_argument("--recalculate", action="store_true", help="Recalculate all clusters")
    
    feedback_stats_parser = feedback_subparsers.add_parser("stats", help="Get feedback statistics")
    
    # Feature commands
    feature_parser = subparsers.add_parser("feature", help="Feature management")
    feature_subparsers = feature_parser.add_subparsers(dest="feature_command")
    
    feature_prioritize_parser = feature_subparsers.add_parser("prioritize", help="Prioritize features")
    feature_prioritize_parser.add_argument(
        "--method",
        choices=["rice", "value_effort", "weighted", "kano"],
        default="weighted",
        help="Prioritization method to use"
    )
    
    feature_top_parser = feature_subparsers.add_parser("top", help="Get top features")
    feature_top_parser.add_argument(
        "--limit", type=int, default=10, help="Maximum number of features to return"
    )
    
    # Objective commands
    objective_parser = subparsers.add_parser("objective", help="Objective management")
    objective_subparsers = objective_parser.add_subparsers(dest="objective_command")
    
    objective_root_parser = objective_subparsers.add_parser("roots", help="Get root objectives")
    
    objective_tree_parser = objective_subparsers.add_parser("tree", help="Get objective tree")
    objective_tree_parser.add_argument("id", help="Objective ID")
    
    # Decision commands
    decision_parser = subparsers.add_parser("decision", help="Decision management")
    decision_subparsers = decision_parser.add_subparsers(dest="decision_command")
    
    decision_search_parser = decision_subparsers.add_parser("search", help="Search decisions")
    decision_search_parser.add_argument("query", help="Search query")
    
    # Competitive commands
    competitive_parser = subparsers.add_parser("competitive", help="Competitive analysis")
    competitive_subparsers = competitive_parser.add_subparsers(dest="competitive_command")
    
    competitive_matrix_parser = competitive_subparsers.add_parser("matrix", help="Create feature matrix")
    
    # Stakeholder commands
    stakeholder_parser = subparsers.add_parser("stakeholder", help="Stakeholder management")
    stakeholder_subparsers = stakeholder_parser.add_subparsers(dest="stakeholder_command")
    
    stakeholder_role_parser = stakeholder_subparsers.add_parser("byrole", help="Get stakeholders by role")
    stakeholder_role_parser.add_argument("role", help="Role to filter by")
    
    # Search commands
    search_parser = subparsers.add_parser("search", help="Search knowledge")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", type=int, default=10, help="Maximum number of results")
    
    # Insight commands
    insight_parser = subparsers.add_parser("insight", help="Generate insights")
    insight_subparsers = insight_parser.add_subparsers(dest="insight_command")
    
    insight_all_parser = insight_subparsers.add_parser("all", help="Generate all insights")
    
    insight_trend_parser = insight_subparsers.add_parser("trends", help="Generate trend analysis")
    insight_trend_parser.add_argument(
        "--days", type=int, default=90, help="Number of days to analyze"
    )
    insight_trend_parser.add_argument(
        "--interval", type=int, default=30, help="Interval size in days"
    )
    
    return parser.parse_args()


def initialize_data_dir(data_dir):
    """Initialize the data directory structure."""
    # Create main directory
    os.makedirs(data_dir, exist_ok=True)
    
    # Create subdirectories for each component
    subdirs = [
        "feedback",
        "feedback_clusters",
        "features",
        "objectives",
        "decisions",
        "competitors",
        "stakeholders",
        "stakeholder_perspectives",
        "scorecards"
    ]
    
    for subdir in subdirs:
        os.makedirs(os.path.join(data_dir, subdir), exist_ok=True)
    
    print(f"Initialized data directory at: {data_dir}")


def main():
    """Main entry point."""
    args = parse_args()
    
    # Ensure data directory exists
    data_dir = args.data_dir
    if not os.path.exists(data_dir):
        if args.init:
            initialize_data_dir(data_dir)
        else:
            print(f"Data directory does not exist: {data_dir}")
            print("Run with --init to create it")
            sys.exit(1)
    
    # Initialize managers based on the command
    if args.command == "feedback" or args.command == "search" or args.command == "insight":
        feedback_mgr = FeedbackManager(storage_dir=data_dir)
    
    if args.command == "feature" or args.command == "search" or args.command == "insight":
        feature_mgr = FeaturePrioritizer(storage_dir=data_dir)
    
    if args.command == "objective" or args.command == "search" or args.command == "insight":
        objective_mgr = ObjectiveManager(storage_dir=data_dir)
    
    if args.command == "decision" or args.command == "search" or args.command == "insight":
        decision_mgr = DecisionManager(storage_dir=data_dir)
    
    if args.command == "competitive" or args.command == "search" or args.command == "insight":
        competitive_mgr = CompetitiveAnalyzer(storage_dir=data_dir)
    
    if args.command == "stakeholder" or args.command == "search" or args.command == "insight":
        stakeholder_mgr = StakeholderManager(storage_dir=data_dir)
    
    if args.command == "search":
        search_engine = SearchEngine(
            storage_dir=data_dir,
            feedback_storage=feedback_mgr.feedback_storage,
            feedback_cluster_storage=feedback_mgr.cluster_storage,
            feature_storage=feature_mgr.feature_storage,
            objective_storage=objective_mgr.objective_storage,
            decision_storage=decision_mgr.decision_storage,
            competitor_storage=competitive_mgr.competitor_storage,
            stakeholder_storage=stakeholder_mgr.stakeholder_storage,
            perspective_storage=stakeholder_mgr.perspective_storage
        )
    
    if args.command == "insight":
        insight_engine = InsightEngine(
            storage_dir=data_dir,
            feedback_storage=feedback_mgr.feedback_storage,
            feedback_cluster_storage=feedback_mgr.cluster_storage,
            feature_storage=feature_mgr.feature_storage,
            objective_storage=objective_mgr.objective_storage,
            decision_storage=decision_mgr.decision_storage,
            competitor_storage=competitive_mgr.competitor_storage,
            stakeholder_storage=stakeholder_mgr.stakeholder_storage,
            perspective_storage=stakeholder_mgr.perspective_storage
        )
    
    # Handle initialization only
    if args.init and not args.command:
        return
    
    # Handle feedback commands
    if args.command == "feedback":
        if args.feedback_command == "cluster":
            result = feedback_mgr.cluster_feedback(recalculate=args.recalculate)
            print(f"Created {result.num_clusters} clusters")
            print(f"Execution time: {result.execution_time_ms} ms")
            print(f"Average cluster size: {result.avg_cluster_size:.2f}")
            print(f"Unclustered items: {len(result.unclustered_items)}")
        
        elif args.feedback_command == "stats":
            stats = feedback_mgr.get_feedback_stats()
            print(f"Total feedback items: {stats.total_items}")
            print(f"Processed items: {stats.processed_items}")
            print(f"Clustered items: {stats.clustered_items}")
            print(f"Unclustered items: {stats.unclustered_items}")
            print(f"Number of clusters: {stats.num_clusters}")
            print(f"Average cluster size: {stats.avg_cluster_size:.2f}")
            
            print("\nSentiment distribution:")
            for sentiment, count in stats.sentiment_counts.items():
                print(f"  {sentiment}: {count}")
            
            print("\nSource distribution:")
            for source, count in stats.source_counts.items():
                print(f"  {source}: {count}")
    
    # Handle feature commands
    elif args.command == "feature":
        if args.feature_command == "prioritize":
            from product_insight.prioritization import PrioritizationMethod
            
            method_map = {
                "rice": PrioritizationMethod.RICE,
                "value_effort": PrioritizationMethod.VALUE_EFFORT,
                "weighted": PrioritizationMethod.WEIGHTED,
                "kano": PrioritizationMethod.KANO
            }
            
            method = method_map[args.method]
            result = feature_mgr.prioritize_features(method=method)
            
            print(f"Prioritized {len(result.scored_features)} features using {args.method} method")
            print(f"Execution time: {result.execution_time_ms} ms")
            
            print("\nTop 5 features:")
            for i, (feature, scorecard) in enumerate(result.scored_features[:5]):
                print(f"{i+1}. {feature.name} (Score: {scorecard.total_score:.2f})")
        
        elif args.feature_command == "top":
            top_features = feature_mgr.get_top_features(limit=args.limit)
            
            print(f"Top {len(top_features)} features:")
            for i, (feature, score) in enumerate(top_features):
                print(f"{i+1}. {feature.name} (Score: {score:.2f})")
    
    # Handle objective commands
    elif args.command == "objective":
        if args.objective_command == "roots":
            roots = objective_mgr.get_root_objectives()
            
            print(f"Found {len(roots)} root objectives:")
            for i, obj in enumerate(roots):
                print(f"{i+1}. {obj.name}")
        
        elif args.objective_command == "tree":
            try:
                from uuid import UUID
                obj_id = UUID(args.id)
                tree = objective_mgr.get_objective_tree(obj_id)
                
                print(f"Objective tree for: {tree.root.name}")
                
                def print_tree(node, level=0):
                    indent = "  " * level
                    print(f"{indent}- {node.root.name}")
                    for child in node.children:
                        print_tree(child, level + 1)
                
                print_tree(tree)
            except ValueError:
                print(f"Invalid objective ID: {args.id}")
                sys.exit(1)
            except Exception as e:
                print(f"Error retrieving objective tree: {str(e)}")
                sys.exit(1)
    
    # Handle decision commands
    elif args.command == "decision":
        if args.decision_command == "search":
            from product_insight.models import SearchQuery
            
            query = SearchQuery(
                query=args.query,
                include_decisions=True,
                include_feedback=False,
                include_features=False,
                include_objectives=False,
                include_competitors=False,
                include_stakeholders=False
            )
            
            # Use the decision manager to search
            matching_decisions = decision_mgr.search_decisions(query)
            
            print(f"Found {len(matching_decisions)} matching decisions:")
            for i, decision in enumerate(matching_decisions):
                print(f"{i+1}. {decision.title} ({decision.decision_date.strftime('%Y-%m-%d')})")
    
    # Handle competitive commands
    elif args.command == "competitive":
        if args.competitive_command == "matrix":
            # Create a feature matrix for all competitors
            matrix = competitive_mgr.create_feature_matrix()
            
            print("Competitive Feature Matrix:")
            print(f"Features: {len(matrix.features)}")
            print(f"Competitors: {len(matrix.competitors)}")
            
            # Print matrix header
            print("\n" + " " * 20, end="")
            for comp in matrix.competitors:
                print(f"{comp[:15]:15}", end=" ")
            print()
            
            # Print each feature row
            for feature in matrix.features:
                print(f"{feature[:20]:20}", end="")
                for comp in matrix.competitors:
                    has_feature = matrix.matrix[comp].get(feature, False)
                    mark = "✓" if has_feature else " "
                    print(f"{mark:15}", end=" ")
                print()
    
    # Handle stakeholder commands
    elif args.command == "stakeholder":
        if args.stakeholder_command == "byrole":
            # Convert role string to enum
            try:
                from product_insight.models import StakeholderRoleEnum
                role = StakeholderRoleEnum(args.role.lower())
                
                # Get stakeholders by role
                stakeholders = stakeholder_mgr.get_stakeholders_by_role(role)
                
                print(f"Found {len(stakeholders)} stakeholders with role '{args.role}':")
                for i, stakeholder in enumerate(stakeholders):
                    org = f" ({stakeholder.organization})" if stakeholder.organization else ""
                    print(f"{i+1}. {stakeholder.name}{org} - {stakeholder.influence.value} influence")
            except ValueError:
                print(f"Invalid stakeholder role: {args.role}")
                print("Valid roles: customer, engineering, product, design, sales, marketing, support, executive, investor, other")
                sys.exit(1)
    
    # Handle search commands
    elif args.command == "search":
        # Build the search index (this may take time)
        print("Building search index...")
        search_engine.build_index()
        
        # Create a search query
        from product_insight.models import SearchQuery
        
        query = SearchQuery(
            query=args.query,
            include_feedback=True,
            include_features=True,
            include_objectives=True,
            include_decisions=True,
            include_competitors=True,
            include_stakeholders=True,
            limit=args.limit
        )
        
        # Perform search
        print(f"Searching for: {args.query}")
        results = search_engine.search(query)
        
        # Display results
        print(f"Found {results.total_count} results in {results.execution_time_ms} ms")
        
        if results.facets.get("entity_type"):
            print("\nResults by type:")
            for entity_type, count in results.facets["entity_type"].items():
                print(f"  {entity_type}: {count}")
        
        print("\nTop results:")
        for i, result in enumerate(results.results):
            print(f"{i+1}. [{result.entity_type}] {result.title}")
            print(f"   Score: {result.relevance_score:.2f}")
            print(f"   {result.snippet[:100]}...")
            print()
    
    # Handle insight commands
    elif args.command == "insight":
        if args.insight_command == "all":
            print("Generating insights (this may take a while)...")
            insight_groups = insight_engine.generate_all_insights()
            
            print(f"Generated {sum(len(group.insights) for group in insight_groups)} insights across {len(insight_groups)} categories")
            
            for group in insight_groups:
                print(f"\n## {group.title}")
                for insight in group.insights:
                    print(f"- {insight.title} ({insight.confidence:.0%} confidence)")
        
        elif args.insight_command == "trends":
            print(f"Generating trend analysis for the past {args.days} days...")
            trends = insight_engine.generate_trend_analysis(
                days=args.days,
                interval_days=args.interval
            )
            
            print(f"Generated {len(trends)} trend analyses")
            
            for trend in trends:
                print(f"\n## {trend.title}")
                print(f"Time periods: {', '.join(trend.time_periods)}")
                
                for series_name, values in trend.series.items():
                    print(f"\n{series_name}:")
                    for i, value in enumerate(values):
                        period = trend.time_periods[i] if i < len(trend.time_periods) else "?"
                        print(f"  {period}: {value}")


if __name__ == "__main__":
    main()