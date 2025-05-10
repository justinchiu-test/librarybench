"""
Mock data generators for ProductInsight tests.

This module provides functionality for generating realistic test data for the
different components of the ProductInsight system.
"""

import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Union
from uuid import UUID, uuid4

from product_insight.models import (
    Competitor,
    Decision,
    Feature,
    FeedbackCluster,
    FeedbackItem,
    InfluenceEnum,
    MetricTypeEnum,
    PriorityEnum,
    SentimentEnum,
    SourceEnum,
    Stakeholder,
    StakeholderPerspective,
    StakeholderRoleEnum,
    StatusEnum,
    StrategicObjective,
    Tag,
)


class MockDataGenerator:
    """Generates mock data for testing."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize the mock data generator.
        
        Args:
            seed: Optional random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)
        
        self.feedback_templates = [
            "I really like the {feature} but it could use some improvements in {aspect}.",
            "The {feature} is not working as expected. It keeps {issue}.",
            "Have you considered adding {feature}? It would really help with {aspect}.",
            "I find it difficult to {task} because the {feature} is not intuitive.",
            "Great job on the {feature}! It's made {task} so much easier.",
            "Could you please add the ability to {task} in the {feature}?",
            "The {feature} is a game-changer for our team's productivity.",
            "I'm experiencing issues with {feature} when I try to {task}.",
            "The {feature} is too slow when handling {aspect}.",
            "Is there a way to customize the {feature} to better suit our {aspect} needs?",
            "The new {feature} update broke our workflow for {task}.",
            "We need better {aspect} capabilities in the {feature}.",
            "Your {feature} has saved us countless hours on {task}.",
            "The {feature} UI is confusing and makes it hard to {task}.",
            "Could the {feature} include better support for {aspect}?",
        ]
        
        self.features = [
            "dashboard", "reports", "user management", "notifications", "data export",
            "authentication", "search", "filtering", "integration", "mobile app",
            "analytics", "automation", "API", "user profiles", "calendar",
            "task management", "team collaboration", "document editor", "permissions",
            "billing", "customer support", "settings", "dark mode", "comments",
            "file sharing", "templates", "email notifications", "workflow",
            "data visualization", "import/export"
        ]
        
        self.aspects = [
            "performance", "usability", "customization", "reliability", "security",
            "accessibility", "mobile support", "integration", "documentation",
            "error handling", "speed", "user interface", "compatibility",
            "configuration", "scalability", "data management", "reporting",
            "collaboration", "automation", "consistency"
        ]
        
        self.tasks = [
            "generate reports", "manage users", "export data", "configure settings",
            "analyze trends", "collaborate with team members", "process large files",
            "integrate with other tools", "customize the interface", "handle errors",
            "search for information", "filter results", "share documents",
            "track progress", "manage permissions", "schedule events",
            "automate workflows", "visualize data", "manage notifications",
            "import data"
        ]
        
        self.issues = [
            "crashing", "freezing", "losing data", "showing errors",
            "running slowly", "not saving changes", "displaying incorrectly",
            "using too much memory", "not responding", "timing out",
            "corrupting files", "loading indefinitely", "failing to connect",
            "sending duplicate notifications", "miscalculating results"
        ]
        
        self.customers = [
            ("John Smith", "Enterprise"),
            ("Emma Johnson", "Premium"),
            ("Michael Brown", "Basic"),
            ("Sarah Williams", "Enterprise"),
            ("James Jones", "Premium"),
            ("Jessica Miller", "Basic"),
            ("Robert Davis", "Enterprise"),
            ("Jennifer Garcia", "Premium"),
            ("William Rodriguez", "Basic"),
            ("Elizabeth Martinez", "Enterprise"),
            ("David Hernandez", "Premium"),
            ("Lisa Lopez", "Basic"),
            ("Joseph Gonzalez", "Enterprise"),
            ("Nancy Wilson", "Premium"),
            ("Thomas Anderson", "Basic"),
            ("Dorothy Taylor", "Enterprise"),
            ("Daniel Moore", "Premium"),
            ("Patricia Jackson", "Basic"),
            ("George White", "Enterprise"),
            ("Margaret Harris", "Premium")
        ]
        
        self.tags = [
            "bug", "feature request", "usability", "performance", "security",
            "mobile", "desktop", "integration", "documentation", "ux",
            "ui", "accessibility", "reliability", "compatibility", "api",
            "data", "reporting", "collaboration", "automation", "configuration"
        ]
        
        self.objective_templates = [
            "Increase {metric} by {value}% in {timeframe}",
            "Reduce {metric} by {value}% in {timeframe}",
            "Achieve {value}% {metric} by {timeframe}",
            "Improve {metric} to {value} in {timeframe}",
            "Optimize {metric} for {value}% efficiency by {timeframe}",
            "Expand {metric} to {value} new {unit} by {timeframe}",
            "Launch {metric} with {value}% {unit} by {timeframe}",
            "Develop {metric} capabilities for {value} {unit} by {timeframe}",
            "Establish {metric} framework with {value} {unit} by {timeframe}",
            "Transform {metric} approach with {value}% improvement by {timeframe}"
        ]
        
        self.metrics = [
            "user adoption", "customer satisfaction", "revenue", "market share",
            "user engagement", "conversion rate", "customer retention",
            "operational efficiency", "platform performance", "feature usage",
            "team productivity", "support response time", "system reliability",
            "data accuracy", "user onboarding", "mobile usage", "api utilization",
            "integration success", "reporting capabilities", "automation coverage"
        ]
        
        self.timeframes = [
            "Q1", "Q2", "Q3", "Q4", "H1", "H2", "2023", "2024", "next quarter",
            "next 6 months", "next year", "18 months", "24 months", "36 months"
        ]
        
        self.units = [
            "users", "customers", "markets", "segments", "features", "platforms",
            "integrations", "reports", "dashboards", "workflows", "automations",
            "countries", "languages", "data sources", "partners", "use cases",
            "templates", "configurations", "team members", "departments"
        ]
        
        self.decision_templates = [
            "Decision to {action} {subject} based on {reason}",
            "Approval of {subject} {action} to address {reason}",
            "Strategic decision to {action} {subject} for {reason}",
            "Plan to {action} {subject} in response to {reason}",
            "Agreement to {action} {subject} to enable {reason}",
            "Choice to {action} {subject} rather than alternatives due to {reason}",
            "Commitment to {action} {subject} in support of {reason}",
            "Resolution to {action} {subject} considering {reason}",
            "Direction to {action} {subject} in alignment with {reason}",
            "Verdict to {action} {subject} after evaluating {reason}"
        ]
        
        self.decision_actions = [
            "implement", "develop", "launch", "redesign", "enhance", "optimize",
            "integrate", "prioritize", "postpone", "accelerate", "scale",
            "customize", "standardize", "modernize", "simplify", "expand",
            "consolidate", "outsource", "insource", "discontinue"
        ]
        
        self.decision_subjects = [
            "new user interface", "mobile experience", "reporting system",
            "analytics platform", "customer onboarding", "pricing structure",
            "integration framework", "security protocols", "user permissions",
            "notification system", "workflow automation", "data architecture",
            "support processes", "deployment pipeline", "feature roadmap",
            "performance optimizations", "resource allocation", "team structure",
            "development approach", "marketing strategy"
        ]
        
        self.decision_reasons = [
            "customer feedback", "market trends", "competitive pressure",
            "technical debt", "strategic alignment", "resource constraints",
            "performance issues", "security concerns", "compliance requirements",
            "user experience improvement", "operational efficiency", "cost reduction",
            "revenue growth", "market expansion", "platform stability",
            "innovation opportunities", "stakeholder requests", "risk mitigation",
            "quality improvement", "technological advancement"
        ]
        
        self.stakeholder_templates = [
            "{name} from {organization}, {role}",
            "{name}, {role} at {organization}",
            "{name} ({role}) - {organization}",
            "{name} - {role}, {organization}",
            "{organization} - {name}, {role}"
        ]
        
        self.organizations = [
            "Acme Corp", "TechSolutions", "Global Innovations", "DataDynamics",
            "NextGen Systems", "Enterprise Solutions", "Digital Transformers",
            "Cloud Pioneers", "Strategic Partners", "Infinity Software",
            "Market Leaders", "Industry Experts", "Client Success", "Value Creators",
            "Growth Accelerators", "Innovation Hub", "Future Tech", "Smart Systems",
            "Connected Solutions", "Insight Partners"
        ]
        
        self.stakeholder_names = [
            "Alexander Thompson", "Olivia Martinez", "Benjamin Rodriguez",
            "Sophia Nguyen", "Samuel Kim", "Isabella Patel", "Ethan Chen",
            "Amelia Johnson", "Andrew Wilson", "Charlotte Davis", "Matthew Taylor",
            "Abigail Brown", "Christopher Lee", "Harper Garcia", "Joshua Smith",
            "Emily Anderson", "Daniel Thompson", "Elizabeth White", "Jacob Harris",
            "Ava Williams", "Ryan Lewis", "Grace Turner", "Nathan Walker",
            "Zoe Phillips", "Jonathan Campbell", "Lily Peterson", "Christian Scott",
            "Madison Evans", "Nicholas Green", "Sofia Martinez"
        ]
        
        self.perspective_topics = [
            "Product roadmap priorities", "User experience design",
            "Technical architecture", "Market positioning", "Pricing strategy",
            "Feature prioritization", "Customer support model", "Release cadence",
            "Integration strategy", "Data security approach", "Mobile strategy",
            "Enterprise scalability", "Automation capabilities", "API strategy",
            "Reporting framework", "Customization options", "Onboarding process",
            "Performance optimization", "Competitive positioning", "Platform reliability"
        ]
        
        self.perspective_templates = [
            "I believe that {topic} should prioritize {aspect} because {reason}.",
            "From my perspective, {topic} needs to focus more on {aspect} to address {reason}.",
            "My view on {topic} is that we need to {action} {aspect} due to {reason}.",
            "Regarding {topic}, I think we should {action} {aspect} since {reason}.",
            "In my opinion, {topic} would benefit from {action} {aspect}, considering {reason}.",
            "I would recommend that {topic} should {action} {aspect} in light of {reason}.",
            "When it comes to {topic}, my stance is that {aspect} needs to be {action} because of {reason}.",
            "My position on {topic} is that {aspect} is critical and we should {action} it to address {reason}.",
            "For {topic}, I strongly suggest we {action} {aspect} given {reason}.",
            "I'm concerned about {topic} and feel we need to {action} {aspect} to mitigate {reason}."
        ]
        
        self.perspective_actions = [
            "improve", "prioritize", "reconsider", "accelerate", "invest in",
            "simplify", "expand", "rethink", "streamline", "focus on",
            "develop", "enhance", "optimize", "redesign", "standardize",
            "customize", "modernize", "consolidate", "transform", "revamp"
        ]
        
        self.perspective_reasons = [
            "changing customer needs", "competitive pressure", "market trends",
            "technical limitations", "user feedback", "operational inefficiencies",
            "strategic alignment", "growth opportunities", "risk factors",
            "resource constraints", "innovation potential", "quality concerns",
            "compliance requirements", "scalability challenges", "cost considerations",
            "user experience issues", "integration complexities", "time-to-market pressures",
            "technological advances", "organizational priorities"
        ]
        
        self.competitor_templates = [
            "{name} - {tagline}",
            "{name}, {tagline}",
            "{name}: {tagline}",
            "{name} ({tagline})",
            "{name} | {tagline}"
        ]
        
        self.competitor_names = [
            "TechVision", "InnoSoft", "DataPilot", "CloudMaster", "ProcessPro",
            "AgileStack", "IntegrateX", "FlexiSystems", "SmartFlow", "AnalyticsPrime",
            "SecureNet", "FusionWare", "VelocityApps", "UniConnect", "InsightHub",
            "DynamicEdge", "StratoScale", "PivotalSystem", "OptimizeIT", "NexGenSoft"
        ]
        
        self.competitor_taglines = [
            "Enterprise solutions for the digital age",
            "Simplifying complex workflows",
            "Data-driven insights for business growth",
            "Seamless integration for modern teams",
            "Accelerating digital transformation",
            "Powering the next generation of business",
            "Innovation at the speed of thought",
            "Where technology meets human needs",
            "Transforming how businesses operate",
            "Collaborative solutions for complex problems",
            "Security-first platform for enterprise",
            "Scalable solutions for growing businesses",
            "Streamlining processes with smart technology",
            "Connecting teams across the enterprise",
            "Intuitive tools for productive teams",
            "Leading the way in business automation",
            "Enterprise-grade reliability with startup agility",
            "Strategic solutions for digital leaders",
            "Performance optimization at every level",
            "Next-generation tools for tomorrow's challenges"
        ]
        
        self.pricing_models = [
            "Per-user subscription", "Tiered subscription", "Usage-based",
            "Freemium with paid upgrades", "Enterprise licensing", "Perpetual license",
            "Value-based", "Feature-based tiers", "Platform fee plus usage", 
            "Volume-based discount", "Annual contract", "Monthly subscription",
            "Transaction-based", "Per-module pricing", "Hybrid model"
        ]
        
        self.competitor_strengths = [
            "User-friendly interface", "Robust reporting capabilities",
            "Seamless third-party integrations", "Advanced analytics",
            "Comprehensive API", "Strong mobile experience", "Enterprise scalability",
            "Excellent customer support", "Rapid implementation", "Customizable workflows",
            "High performance", "Data visualization", "Automated processes",
            "Industry-specific features", "Predictive insights", "Collaboration tools",
            "Low learning curve", "Real-time capabilities", "Flexible deployment options",
            "Compliance certifications"
        ]
        
        self.competitor_weaknesses = [
            "Limited customization", "Poor mobile experience", "Weak reporting",
            "Expensive pricing", "Complex implementation", "Slow performance",
            "Limited integrations", "Outdated UI", "Poor customer support",
            "Missing key features", "Reliability issues", "Security concerns",
            "Difficult to scale", "Limited API capabilities", "Inflexible workflows",
            "Confusing navigation", "Lack of automation", "Heavy resource usage",
            "Poor documentation", "Infrequent updates"
        ]
        
        self.market_segments = [
            "Enterprise", "SMB", "Startups", "Healthcare", "Financial Services",
            "Retail", "Manufacturing", "Technology", "Education", "Government",
            "Non-profit", "Media", "Telecommunications", "Professional Services",
            "Hospitality", "Transportation", "Energy", "Real Estate", "Construction",
            "Consumer Goods"
        ]
    
    def generate_tags(self, count: int = 3) -> List[Tag]:
        """Generate a list of random tags.
        
        Args:
            count: Number of tags to generate
            
        Returns:
            List of tags
        """
        selected_tags = random.sample(self.tags, min(count, len(self.tags)))
        
        colors = [
            "#4285F4", "#DB4437", "#F4B400", "#0F9D58", "#AB47BC",
            "#00ACC1", "#FF7043", "#9E9E9E", "#5C6BC0", "#26A69A"
        ]
        
        return [
            Tag(name=tag, color=random.choice(colors))
            for tag in selected_tags
        ]
    
    def generate_feedback_item(self, index: int = 0) -> FeedbackItem:
        """Generate a random feedback item.
        
        Args:
            index: Optional index for deterministic generation
            
        Returns:
            Generated FeedbackItem
        """
        template = random.choice(self.feedback_templates)
        feature = random.choice(self.features)
        aspect = random.choice(self.aspects)
        task = random.choice(self.tasks)
        issue = random.choice(self.issues)
        
        content = template.format(
            feature=feature,
            aspect=aspect,
            task=task,
            issue=issue
        )
        
        # Select a random customer
        customer_name, customer_segment = random.choice(self.customers)
        
        # Generate a creation date between 1 and 180 days ago
        days_ago = random.randint(1, 180)
        created_at = datetime.now() - timedelta(days=days_ago)
        
        # Generate random source
        source = random.choice(list(SourceEnum))
        
        # Generate random sentiment (more likely to be neutral or negative for feedback)
        sentiment_weights = {
            SentimentEnum.VERY_NEGATIVE: 0.15,
            SentimentEnum.NEGATIVE: 0.3,
            SentimentEnum.NEUTRAL: 0.4,
            SentimentEnum.POSITIVE: 0.1,
            SentimentEnum.VERY_POSITIVE: 0.05
        }
        sentiment = random.choices(
            list(sentiment_weights.keys()),
            weights=list(sentiment_weights.values())
        )[0]
        
        # Generate tags
        tags = self.generate_tags(random.randint(1, 3))
        
        # Generate extracted features (50% chance)
        extracted_features = []
        if random.random() < 0.5:
            num_features = random.randint(1, 2)
            for _ in range(num_features):
                extracted_features.append(str(uuid4()))
        
        # Generate impact score (60% chance)
        impact_score = None
        if random.random() < 0.6:
            impact_score = random.uniform(0.1, 1.0)
        
        return FeedbackItem(
            content=content,
            source=source,
            sentiment=sentiment,
            tags=tags,
            source_id=f"SRC-{index:04d}",
            customer_id=f"CUST-{index:04d}",
            customer_segment=customer_segment,
            processed=random.random() < 0.9,  # 90% processed
            extracted_features=extracted_features,
            impact_score=impact_score,
            created_at=created_at,
            updated_at=created_at + timedelta(hours=random.randint(1, 24))
        )
    
    def generate_feedback_items(self, count: int) -> List[FeedbackItem]:
        """Generate multiple feedback items.
        
        Args:
            count: Number of feedback items to generate
            
        Returns:
            List of generated FeedbackItems
        """
        return [self.generate_feedback_item(i) for i in range(count)]
    
    def generate_feedback_cluster(
        self, feedback_items: List[FeedbackItem], index: int = 0
    ) -> FeedbackCluster:
        """Generate a feedback cluster from feedback items.
        
        Args:
            feedback_items: Feedback items to include in the cluster
            index: Optional index for deterministic generation
            
        Returns:
            Generated FeedbackCluster
        """
        # Extract a name from common words in the feedback
        all_content = " ".join([item.content for item in feedback_items])
        words = all_content.lower().split()
        # Remove common words
        stopwords = {"i", "me", "my", "myself", "we", "our", "ours", "ourselves", 
                     "you", "your", "yours", "yourself", "yourselves", "he", "him", 
                     "his", "himself", "she", "her", "hers", "herself", "it", "its", 
                     "itself", "they", "them", "their", "theirs", "themselves", 
                     "what", "which", "who", "whom", "this", "that", "these", 
                     "those", "am", "is", "are", "was", "were", "be", "been", 
                     "being", "have", "has", "had", "having", "do", "does", "did", 
                     "doing", "a", "an", "the", "and", "but", "if", "or", "because", 
                     "as", "until", "while", "of", "at", "by", "for", "with", 
                     "about", "against", "between", "into", "through", "during", 
                     "before", "after", "above", "below", "to", "from", "up", 
                     "down", "in", "out", "on", "off", "over", "under", "again", 
                     "further", "then", "once", "here", "there", "when", "where", 
                     "why", "how", "all", "any", "both", "each", "few", "more", 
                     "most", "other", "some", "such", "no", "nor", "not", "only", 
                     "own", "same", "so", "than", "too", "very", "s", "t", "can", 
                     "will", "just", "don", "should", "now"}
        filtered_words = [word for word in words if word not in stopwords and len(word) > 3]
        
        # Count word frequencies
        word_counts = {}
        for word in filtered_words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Get most common words
        common_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Create cluster name
        name = " ".join(word for word, _ in common_words).title()
        if not name:
            name = f"Feedback Cluster {index}"
        
        # Get feedback IDs
        feedback_ids = [item.id for item in feedback_items]
        
        # Combine tags from feedback items
        all_tags = {}
        for item in feedback_items:
            for tag in item.tags:
                if tag.name not in all_tags:
                    all_tags[tag.name] = tag
        
        # Get sentiment summaries
        sentiment_counts = {}
        for item in feedback_items:
            if item.sentiment:
                sentiment = item.sentiment
                sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        sentiment_summary = max(sentiment_counts.items(), key=lambda x: x[1])[0] if sentiment_counts else None
        
        # Calculate impact score
        impact_scores = [item.impact_score for item in feedback_items if item.impact_score is not None]
        impact_score = sum(impact_scores) / len(impact_scores) if impact_scores else None
        
        # Create feature requests (30% chance)
        feature_requests = []
        if random.random() < 0.3:
            num_features = random.randint(1, 3)
            for _ in range(num_features):
                feature_requests.append(uuid4())
        
        return FeedbackCluster(
            name=name,
            description=f"Cluster of {len(feedback_ids)} feedback items related to {name.lower()}",
            feedback_ids=feedback_ids,
            tags=list(all_tags.values()),
            central_theme=name,
            sentiment_summary=sentiment_summary,
            volume=len(feedback_ids),
            impact_score=impact_score,
            feature_requests=feature_requests
        )
    
    def generate_feedback_clusters(
        self, feedback_items: List[FeedbackItem], num_clusters: int
    ) -> List[FeedbackCluster]:
        """Generate multiple feedback clusters.
        
        Args:
            feedback_items: Feedback items to distribute among clusters
            num_clusters: Number of clusters to generate
            
        Returns:
            List of generated FeedbackClusters
        """
        # Shuffle feedback items
        shuffled_items = feedback_items.copy()
        random.shuffle(shuffled_items)
        
        # Distribute items among clusters
        clusters = []
        items_per_cluster = len(shuffled_items) // num_clusters
        
        for i in range(num_clusters):
            start_idx = i * items_per_cluster
            end_idx = (i + 1) * items_per_cluster if i < num_clusters - 1 else len(shuffled_items)
            
            cluster_items = shuffled_items[start_idx:end_idx]
            if cluster_items:  # Ensure we have items
                cluster = self.generate_feedback_cluster(cluster_items, i)
                clusters.append(cluster)
        
        return clusters
    
    def generate_strategic_objective(self, index: int = 0) -> StrategicObjective:
        """Generate a random strategic objective.
        
        Args:
            index: Optional index for deterministic generation
            
        Returns:
            Generated StrategicObjective
        """
        template = random.choice(self.objective_templates)
        metric = random.choice(self.metrics)
        value = random.randint(10, 50)
        timeframe = random.choice(self.timeframes)
        unit = random.choice(self.units)
        
        name = template.format(
            metric=metric,
            value=value,
            timeframe=timeframe,
            unit=unit
        )
        
        description = (
            f"Strategic objective to {template.format(metric=metric, value=value, timeframe=timeframe, unit=unit).lower()} "
            f"by implementing new capabilities and optimizing existing processes."
        )
        
        # Generate random metric type
        metric_type = random.choice(list(MetricTypeEnum))
        
        # Generate metric target and current values
        metric_target = random.uniform(100, 1000)
        progress_ratio = random.uniform(0, 1)
        metric_current = metric_target * progress_ratio
        
        # Generate timeframe
        now = datetime.now()
        timeframe_start = now - timedelta(days=random.randint(30, 180))
        timeframe_end = now + timedelta(days=random.randint(30, 365))
        
        # Generate random status and priority
        status = random.choice(list(StatusEnum))
        priority = random.choice(list(PriorityEnum))
        
        # Generate tags
        tags = self.generate_tags(random.randint(1, 3))
        
        # Generate stakeholders (50% chance)
        stakeholder_ids = []
        if random.random() < 0.5:
            num_stakeholders = random.randint(1, 5)
            for _ in range(num_stakeholders):
                stakeholder_ids.append(uuid4())
        
        # Generate features (70% chance)
        feature_ids = []
        if random.random() < 0.7:
            num_features = random.randint(1, 5)
            for _ in range(num_features):
                feature_ids.append(uuid4())
        
        # Generate parent ID (30% chance for non-root objectives)
        parent_id = uuid4() if random.random() < 0.3 else None
        
        # Generate child IDs (40% chance)
        child_ids = []
        if random.random() < 0.4:
            num_children = random.randint(1, 3)
            for _ in range(num_children):
                child_ids.append(uuid4())
        
        return StrategicObjective(
            name=name,
            description=description,
            parent_id=parent_id,
            child_ids=child_ids,
            metric_type=metric_type,
            metric_target=metric_target,
            metric_current=metric_current,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
            status=status,
            priority=priority,
            stakeholder_ids=stakeholder_ids,
            feature_ids=feature_ids,
            tags=tags,
            created_at=timeframe_start,
            updated_at=now - timedelta(days=random.randint(0, 30))
        )
    
    def generate_strategic_objectives(self, count: int) -> List[StrategicObjective]:
        """Generate multiple strategic objectives.
        
        Args:
            count: Number of strategic objectives to generate
            
        Returns:
            List of generated StrategicObjectives
        """
        return [self.generate_strategic_objective(i) for i in range(count)]
    
    def generate_feature(self, index: int = 0) -> Feature:
        """Generate a random feature.
        
        Args:
            index: Optional index for deterministic generation
            
        Returns:
            Generated Feature
        """
        feature = random.choice(self.features).title()
        name = f"{feature} {index}"
        
        aspect = random.choice(self.aspects)
        task = random.choice(self.tasks)
        
        description = f"A feature for {task} with improved {aspect}."
        
        # Generate random status
        status = random.choice(list(StatusEnum))
        
        # Generate effort and value estimates
        effort_estimate = random.uniform(1, 10)
        value_estimate = random.uniform(1, 10)
        
        # Generate priority score (80% chance)
        priority_score = None
        priority_method = None
        if random.random() < 0.8:
            priority_score = random.uniform(0, 1)
            priority_methods = ["rice", "value_effort", "weighted", "kano", "custom"]
            priority_method = random.choice(priority_methods)
        
        # Generate tags
        tags = self.generate_tags(random.randint(1, 3))
        
        # Generate strategic objectives (60% chance)
        objective_ids = []
        if random.random() < 0.6:
            num_objectives = random.randint(1, 3)
            for _ in range(num_objectives):
                objective_ids.append(uuid4())
        
        # Generate feedback (70% chance)
        feedback_ids = []
        if random.random() < 0.7:
            num_feedback = random.randint(1, 10)
            for _ in range(num_feedback):
                feedback_ids.append(uuid4())
        
        # Generate feedback clusters (50% chance)
        feedback_cluster_ids = []
        if random.random() < 0.5:
            num_clusters = random.randint(1, 3)
            for _ in range(num_clusters):
                feedback_cluster_ids.append(uuid4())
        
        # Generate stakeholders (60% chance)
        stakeholder_ids = []
        if random.random() < 0.6:
            num_stakeholders = random.randint(1, 5)
            for _ in range(num_stakeholders):
                stakeholder_ids.append(uuid4())
        
        # Generate dependencies (30% chance)
        dependencies = []
        if random.random() < 0.3:
            num_dependencies = random.randint(1, 3)
            for _ in range(num_dependencies):
                dependencies.append(uuid4())
        
        # Generate Kano category (50% chance)
        kano_categories = ["basic", "performance", "excitement", "indifferent", "reverse"]
        kano_category = random.choice(kano_categories) if random.random() < 0.5 else None
        
        # Generate technical debt impact (40% chance)
        technical_debt_impact = random.uniform(0, 1) if random.random() < 0.4 else None
        
        # Generate risk level (60% chance)
        risk_level = random.uniform(0, 1) if random.random() < 0.6 else None
        
        # Generate implementation notes (30% chance)
        implementation_notes = None
        if random.random() < 0.3:
            implementation_notes = (
                f"Implement using the new {random.choice(self.aspects)} framework. "
                f"Coordinate with the team working on {random.choice(self.features)}."
            )
        
        # Generate creation and update dates
        now = datetime.now()
        created_at = now - timedelta(days=random.randint(30, 365))
        updated_at = created_at + timedelta(days=random.randint(1, 30))
        
        return Feature(
            name=name,
            description=description,
            status=status,
            effort_estimate=effort_estimate,
            value_estimate=value_estimate,
            priority_score=priority_score,
            priority_method=priority_method,
            objective_ids=objective_ids,
            feedback_ids=feedback_ids,
            feedback_cluster_ids=feedback_cluster_ids,
            stakeholder_ids=stakeholder_ids,
            tags=tags,
            dependencies=dependencies,
            kano_category=kano_category,
            technical_debt_impact=technical_debt_impact,
            risk_level=risk_level,
            implementation_notes=implementation_notes,
            created_at=created_at,
            updated_at=updated_at
        )
    
    def generate_features(self, count: int) -> List[Feature]:
        """Generate multiple features.
        
        Args:
            count: Number of features to generate
            
        Returns:
            List of generated Features
        """
        return [self.generate_feature(i) for i in range(count)]
    
    def generate_decision(self, index: int = 0) -> Decision:
        """Generate a random decision.
        
        Args:
            index: Optional index for deterministic generation
            
        Returns:
            Generated Decision
        """
        template = random.choice(self.decision_templates)
        action = random.choice(self.decision_actions)
        subject = random.choice(self.decision_subjects)
        reason = random.choice(self.decision_reasons)
        
        title = template.format(
            action=action,
            subject=subject,
            reason=reason
        )
        
        description = f"Decision regarding the {subject} and how we should {action} it."
        
        context = (
            f"The {subject} has been a key area of focus for our product strategy. "
            f"We've observed increasing {reason} which necessitates action. "
            f"The team has been investigating options for how to address this effectively."
        )
        
        rationale = (
            f"After evaluating multiple approaches, we've decided to {action} the {subject} "
            f"because it addresses the {reason} most effectively while balancing resource constraints "
            f"and strategic priorities. This approach provides the best value for our customers "
            f"while maintaining alignment with our product roadmap."
        )
        
        # Generate alternatives
        num_alternatives = random.randint(1, 3)
        alternatives = []
        for i in range(num_alternatives):
            alt_action = random.choice([a for a in self.decision_actions if a != action])
            alt_reason = random.choice(self.decision_reasons)
            alternatives.append(f"Alternative {i+1}: {alt_action} the {subject} to address {alt_reason}")
        
        # Generate decision date
        now = datetime.now()
        decision_date = now - timedelta(days=random.randint(1, 180))
        
        # Generate decided by (stakeholders)
        num_deciders = random.randint(1, 3)
        decided_by = []
        for _ in range(num_deciders):
            decided_by.append(uuid4())
        
        # Generate stakeholder input (40% chance)
        stakeholder_input = {}
        if random.random() < 0.4:
            num_inputs = random.randint(1, 5)
            for _ in range(num_inputs):
                stakeholder_id = uuid4()
                input_text = f"I {random.choice(['support', 'have concerns about', 'am neutral about'])} this decision because of its impact on {random.choice(self.aspects)}."
                stakeholder_input[stakeholder_id] = input_text
        
        # Generate feature IDs (60% chance)
        feature_ids = []
        if random.random() < 0.6:
            num_features = random.randint(1, 3)
            for _ in range(num_features):
                feature_ids.append(uuid4())
        
        # Generate objective IDs (50% chance)
        objective_ids = []
        if random.random() < 0.5:
            num_objectives = random.randint(1, 2)
            for _ in range(num_objectives):
                objective_ids.append(uuid4())
        
        # Generate supporting data (30% chance)
        supporting_data = []
        if random.random() < 0.3:
            num_data = random.randint(1, 3)
            for i in range(num_data):
                supporting_data.append(f"Data point {i+1}: Analysis of {random.choice(self.aspects)} metrics")
        
        # Generate outcome notes and date (70% chance)
        outcome_notes = None
        outcome_date = None
        if random.random() < 0.7:
            outcome_result = random.choice(["successful", "partially successful", "unsuccessful"])
            outcome_notes = f"Implementation was {outcome_result}. The {subject} now {random.choice(['meets', 'partially meets', 'fails to meet'])} our expectations."
            outcome_date = decision_date + timedelta(days=random.randint(14, 90))
        
        # Generate retrospective (50% chance if there's an outcome)
        retrospective = None
        if outcome_notes and random.random() < 0.5:
            retrospective = f"In retrospect, the decision to {action} the {subject} was {random.choice(['the right choice', 'partly effective', 'more challenging than expected'])}. Next time we should {random.choice(['involve more stakeholders', 'gather more data', 'allocate more resources', 'plan for more testing'])}."
        
        # Generate tags
        tags = self.generate_tags(random.randint(1, 3))
        
        return Decision(
            title=title,
            description=description,
            context=context,
            rationale=rationale,
            alternatives=alternatives,
            decision_date=decision_date,
            decided_by=decided_by,
            stakeholder_input=stakeholder_input,
            feature_ids=feature_ids,
            objective_ids=objective_ids,
            supporting_data=supporting_data,
            outcome_notes=outcome_notes,
            outcome_date=outcome_date,
            retrospective=retrospective,
            tags=tags,
            created_at=decision_date,
            updated_at=outcome_date or decision_date
        )
    
    def generate_decisions(self, count: int) -> List[Decision]:
        """Generate multiple decisions.
        
        Args:
            count: Number of decisions to generate
            
        Returns:
            List of generated Decisions
        """
        return [self.generate_decision(i) for i in range(count)]
    
    def generate_stakeholder(self, index: int = 0) -> Stakeholder:
        """Generate a random stakeholder.
        
        Args:
            index: Optional index for deterministic generation
            
        Returns:
            Generated Stakeholder
        """
        template = random.choice(self.stakeholder_templates)
        name = random.choice(self.stakeholder_names)
        organization = random.choice(self.organizations)
        role = random.choice(list(StakeholderRoleEnum))
        
        # Generate influence level
        influence = random.choice(list(InfluenceEnum))
        
        # Generate email (80% chance)
        email = None
        if random.random() < 0.8:
            first_name, last_name = name.split(" ", 1)
            email = f"{first_name.lower()}.{last_name.lower()}@{organization.lower().replace(' ', '')}.com"
        
        # Generate alignment (60% chance)
        alignment = random.uniform(0, 1) if random.random() < 0.6 else None
        
        # Generate key concerns
        num_concerns = random.randint(1, 3)
        key_concerns = []
        for _ in range(num_concerns):
            concern = f"{random.choice(self.aspects)} in the {random.choice(self.features)}"
            key_concerns.append(concern)
        
        # Generate feature preferences
        num_features = random.randint(0, 5)
        feature_preferences = {}
        for _ in range(num_features):
            feature_id = uuid4()
            preference = random.uniform(0, 1)
            feature_preferences[feature_id] = preference
        
        # Generate objective alignment
        num_objectives = random.randint(0, 3)
        objective_alignment = {}
        for _ in range(num_objectives):
            objective_id = uuid4()
            alignment_value = random.uniform(0, 1)
            objective_alignment[objective_id] = alignment_value
        
        # Generate communication preferences (40% chance)
        communication_preferences = None
        if random.random() < 0.4:
            frequency = random.choice(["weekly", "biweekly", "monthly", "quarterly"])
            method = random.choice(["email", "meetings", "calls", "reports"])
            communication_preferences = f"Prefers {frequency} {method} for updates."
        
        # Generate engagement history
        num_engagements = random.randint(0, 5)
        engagement_history = []
        now = datetime.now()
        
        for i in range(num_engagements):
            days_ago = random.randint(1, 180)
            date = now - timedelta(days=days_ago)
            date_str = date.strftime("%Y-%m-%d %H:%M")
            
            engagement_type = random.choice(["Meeting", "Email", "Call", "Workshop", "Review"])
            engagement = f"[{date_str}] {engagement_type}: Discussed {random.choice(self.features)} and {random.choice(self.aspects)}"
            engagement_history.append(engagement)
        
        # Sort engagements by date (newest last)
        engagement_history.sort()
        
        # Generate notes (30% chance)
        notes = None
        if random.random() < 0.3:
            notes = f"Internal champion for {random.choice(self.features)}. Has strong opinions about {random.choice(self.aspects)}."
        
        return Stakeholder(
            name=name,
            role=role,
            organization=organization,
            email=email,
            influence=influence,
            alignment=alignment,
            key_concerns=key_concerns,
            feature_preferences=feature_preferences,
            objective_alignment=objective_alignment,
            communication_preferences=communication_preferences,
            engagement_history=engagement_history,
            notes=notes,
            created_at=now - timedelta(days=random.randint(30, 365)),
            updated_at=now - timedelta(days=random.randint(0, 30))
        )
    
    def generate_stakeholders(self, count: int) -> List[Stakeholder]:
        """Generate multiple stakeholders.
        
        Args:
            count: Number of stakeholders to generate
            
        Returns:
            List of generated Stakeholders
        """
        return [self.generate_stakeholder(i) for i in range(count)]
    
    def generate_stakeholder_perspective(
        self, stakeholder_id: UUID, index: int = 0
    ) -> StakeholderPerspective:
        """Generate a random stakeholder perspective.
        
        Args:
            stakeholder_id: ID of the stakeholder
            index: Optional index for deterministic generation
            
        Returns:
            Generated StakeholderPerspective
        """
        template = random.choice(self.perspective_templates)
        topic = random.choice(self.perspective_topics)
        aspect = random.choice(self.aspects)
        action = random.choice(self.perspective_actions)
        reason = random.choice(self.perspective_reasons)
        
        perspective_text = template.format(
            topic=topic,
            aspect=aspect,
            action=action,
            reason=reason
        )
        
        # Generate random sentiment with weights
        sentiment_weights = {
            SentimentEnum.VERY_NEGATIVE: 0.1,
            SentimentEnum.NEGATIVE: 0.2,
            SentimentEnum.NEUTRAL: 0.4,
            SentimentEnum.POSITIVE: 0.2,
            SentimentEnum.VERY_POSITIVE: 0.1
        }
        sentiment = random.choices(
            list(sentiment_weights.keys()),
            weights=list(sentiment_weights.values())
        )[0]
        
        # Generate random date
        now = datetime.now()
        date_recorded = now - timedelta(days=random.randint(1, 90))
        
        # Generate context (50% chance)
        context = None
        if random.random() < 0.5:
            context_templates = [
                "Shared during {event_type} on {feature}",
                "Feedback provided during {event_type}",
                "Comment made while discussing {feature}",
                "Response to question about {feature} during {event_type}",
                "Mentioned in follow-up to {event_type} about {feature}"
            ]
            event_types = ["meeting", "workshop", "review", "interview", "survey", "call", "email thread"]
            feature = random.choice(self.features)
            event_type = random.choice(event_types)
            
            context = random.choice(context_templates).format(
                event_type=event_type,
                feature=feature
            )
        
        # Generate related feature IDs (70% chance)
        related_feature_ids = []
        if random.random() < 0.7:
            num_features = random.randint(1, 2)
            for _ in range(num_features):
                related_feature_ids.append(uuid4())
        
        # Generate related objective IDs (50% chance)
        related_objective_ids = []
        if random.random() < 0.5:
            num_objectives = random.randint(1, 2)
            for _ in range(num_objectives):
                related_objective_ids.append(uuid4())
        
        return StakeholderPerspective(
            stakeholder_id=stakeholder_id,
            topic=topic,
            perspective=perspective_text,
            sentiment=sentiment,
            date_recorded=date_recorded,
            context=context,
            related_feature_ids=related_feature_ids,
            related_objective_ids=related_objective_ids,
            created_at=date_recorded,
            updated_at=date_recorded
        )
    
    def generate_stakeholder_perspectives(
        self, stakeholders: List[Stakeholder], avg_perspectives_per_stakeholder: float = 2.0
    ) -> List[StakeholderPerspective]:
        """Generate perspectives for multiple stakeholders.
        
        Args:
            stakeholders: List of stakeholders
            avg_perspectives_per_stakeholder: Average number of perspectives per stakeholder
            
        Returns:
            List of generated StakeholderPerspectives
        """
        perspectives = []
        
        for i, stakeholder in enumerate(stakeholders):
            # Determine number of perspectives for this stakeholder
            # Use Poisson distribution around the average
            num_perspectives = max(0, int(random.expovariate(1/avg_perspectives_per_stakeholder)))
            
            for j in range(num_perspectives):
                perspective = self.generate_stakeholder_perspective(stakeholder.id, i * 10 + j)
                perspectives.append(perspective)
        
        return perspectives
    
    def generate_competitor(self, index: int = 0) -> Competitor:
        """Generate a random competitor.
        
        Args:
            index: Optional index for deterministic generation
            
        Returns:
            Generated Competitor
        """
        template = random.choice(self.competitor_templates)
        name = random.choice(self.competitor_names)
        tagline = random.choice(self.competitor_taglines)
        
        # Format name and tagline
        formatted_name = template.format(name=name, tagline=tagline)
        
        # Generate description (70% chance)
        description = None
        if random.random() < 0.7:
            description = f"{name} provides {random.choice(self.features)} solutions with a focus on {random.choice(self.aspects)}. They primarily target {random.choice(self.market_segments)} customers."
        
        # Generate website (90% chance)
        website = None
        if random.random() < 0.9:
            website = f"https://www.{name.lower().replace(' ', '')}.com"
        
        # Generate market share (60% chance)
        market_share = random.uniform(1, 30) if random.random() < 0.6 else None
        
        # Generate pricing model and details
        pricing_model = random.choice(self.pricing_models)
        
        pricing_details = None
        if random.random() < 0.7:
            tiers = ["Basic", "Pro", "Enterprise"]
            prices = [f"${random.randint(10, 50)}/user/month", f"${random.randint(30, 100)}/user/month", "Custom pricing"]
            
            pricing_details = "; ".join([
                f"{tier}: {price}" for tier, price in zip(tiers, prices)
            ])
        
        # Generate target segments
        num_segments = random.randint(1, 3)
        target_segments = random.sample(self.market_segments, num_segments)
        
        # Generate strengths
        num_strengths = random.randint(2, 5)
        strengths = random.sample(self.competitor_strengths, num_strengths)
        
        # Generate weaknesses
        num_weaknesses = random.randint(2, 5)
        weaknesses = random.sample(self.competitor_weaknesses, num_weaknesses)
        
        # Generate feature comparison
        num_features = random.randint(5, 15)
        feature_comparison = {}
        our_features = random.sample(self.features, num_features)
        
        for feature in our_features:
            # 70% chance the competitor has each feature
            has_feature = random.random() < 0.7
            feature_comparison[feature] = has_feature
        
        # Generate detailed comparisons (30% chance)
        detailed_comparisons = {}
        if random.random() < 0.3:
            num_detailed = random.randint(1, 3)
            detailed_features = random.sample(our_features, min(num_detailed, len(our_features)))
            
            for feature in detailed_features:
                comparison = f"Their {feature} is {random.choice(['better', 'worse', 'similar'])} than ours, with {random.choice(['more', 'less', 'similar'])} {random.choice(self.aspects)}."
                detailed_comparisons[feature] = comparison
        
        # Generate threat level (80% chance)
        threat_level = random.uniform(0, 1) if random.random() < 0.8 else None
        
        # Generate notes (40% chance)
        notes = None
        if random.random() < 0.4:
            notes = f"Recently {random.choice(['expanded into', 'acquired a company in', 'partnered with a leader in'])} the {random.choice(self.market_segments)} market. Watch their {random.choice(self.features)} development."
        
        # Generate tags
        tags = self.generate_tags(random.randint(1, 3))
        
        # Generate creation and update dates
        now = datetime.now()
        created_at = now - timedelta(days=random.randint(30, 365))
        updated_at = now - timedelta(days=random.randint(0, 30))
        
        return Competitor(
            name=formatted_name,
            description=description,
            website=website,
            market_share=market_share,
            pricing_model=pricing_model,
            pricing_details=pricing_details,
            target_segments=target_segments,
            strengths=strengths,
            weaknesses=weaknesses,
            feature_comparison=feature_comparison,
            detailed_comparisons=detailed_comparisons,
            threat_level=threat_level,
            notes=notes,
            tags=tags,
            created_at=created_at,
            updated_at=updated_at
        )
    
    def generate_competitors(self, count: int) -> List[Competitor]:
        """Generate multiple competitors.
        
        Args:
            count: Number of competitors to generate
            
        Returns:
            List of generated Competitors
        """
        return [self.generate_competitor(i) for i in range(count)]