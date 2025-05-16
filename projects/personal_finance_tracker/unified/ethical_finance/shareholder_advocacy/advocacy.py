"""Shareholder advocacy tracker for monitoring corporate governance."""

from typing import Dict, List, Optional, Any, Tuple
from datetime import date, datetime
from uuid import UUID, uuid4
import time
from dataclasses import dataclass
from pydantic import BaseModel, Field, validator

# Import from common library
from common.core.analysis.analyzer import BaseAnalyzer, AnalysisParameters, AnalysisResult
from common.core.utils.performance import Timer
from common.core.utils.cache_utils import memoize

from ethical_finance.models import Investment, Portfolio, ShareholderResolution


class VotingAnalysisResult(AnalysisResult):
    """Result of analyzing voting patterns for a company or resolution."""
    
    total_resolutions: int
    category_breakdown: Dict[str, int] = Field(default_factory=dict)
    passing_rate: float
    management_support_rate: float
    key_findings: List[str] = Field(default_factory=list)
    
    @classmethod
    def from_analysis(cls, 
                    entity_id: str,
                    entity_type: str,
                    total_resolutions: int,
                    category_breakdown: Dict[str, int],
                    passing_rate: float,
                    management_support_rate: float,
                    key_findings: List[str],
                    supporting_data: Dict[str, Any],
                    processing_time_ms: float = 0) -> "VotingAnalysisResult":
        """Create a VotingAnalysisResult from analysis data."""
        return cls(
            id=uuid4(),
            subject_id=entity_id,
            subject_type=entity_type,
            analysis_type="voting_analysis",
            analysis_date=datetime.now(),
            processing_time_ms=processing_time_ms,
            result_summary={
                "total_resolutions": total_resolutions,
                "passing_rate": passing_rate,
                "management_support_rate": management_support_rate
            },
            detailed_results={
                "category_breakdown": category_breakdown,
                "key_findings": key_findings,
                "supporting_data": supporting_data
            },
            total_resolutions=total_resolutions,
            category_breakdown=category_breakdown,
            passing_rate=passing_rate,
            management_support_rate=management_support_rate,
            key_findings=key_findings
        )


class VotingRecommendation(BaseModel):
    """Recommendation for how to vote on a shareholder resolution."""
    
    resolution_id: str
    company_id: str
    recommendation: str  # "for", "against", "abstain"
    confidence: float  # 0.0 to 1.0
    rationale: str
    alignment_score: float  # How well aligned with values (-1.0 to 1.0)
    
    @validator('recommendation')
    def validate_recommendation(cls, v):
        """Validate recommendation value."""
        valid_values = ["for", "against", "abstain"]
        if v not in valid_values:
            raise ValueError(f"Recommendation must be one of: {', '.join(valid_values)}")
        return v
    
    @validator('confidence')
    def validate_confidence(cls, v):
        """Validate confidence is between 0.0 and 1.0."""
        if v < 0.0 or v > 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v
    
    @validator('alignment_score')
    def validate_alignment_score(cls, v):
        """Validate alignment score is between -1.0 and 1.0."""
        if v < -1.0 or v > 1.0:
            raise ValueError("Alignment score must be between -1.0 and 1.0")
        return v


class ShareholderAdvocacyTracker(BaseAnalyzer[ShareholderResolution, VotingAnalysisResult]):
    """Tracks and analyzes shareholder resolutions and voting patterns."""
    
    def __init__(self, value_priorities: Dict[str, float] = None):
        """Initialize with optional value priorities for voting recommendations.
        
        Args:
            value_priorities: Dict mapping issue categories to importance weights (0.0-1.0)
        """
        super().__init__()
        self.value_priorities = value_priorities or {
            "environmental": 0.4,
            "social": 0.3,
            "governance": 0.3,
            "climate": 0.5,
            "human_rights": 0.5,
            "diversity": 0.4,
            "executive_compensation": 0.3,
            "political_spending": 0.2,
            "tax_transparency": 0.2
        }
    
    def analyze(
        self, subject: ShareholderResolution, parameters: Optional[AnalysisParameters] = None
    ) -> VotingAnalysisResult:
        """
        Analyze a single shareholder resolution.
        
        Args:
            subject: The shareholder resolution to analyze
            parameters: Optional parameters to configure the analysis
            
        Returns:
            Analysis result for the resolution
        """
        # For single resolution analysis, we can use the entity_id and a basic result
        with Timer("analyze_single_resolution") as timer:
            alignment_score = self._calculate_value_alignment(subject)
            
            # For a single resolution, we just create a simple result
            return VotingAnalysisResult.from_analysis(
                entity_id=subject.resolution_id,
                entity_type="resolution",
                total_resolutions=1,
                category_breakdown={subject.category: 1},
                passing_rate=1.0 if subject.outcome == "passed" else 0.0,
                management_support_rate=1.0 if subject.company_recommendation == "for" else 0.0,
                key_findings=[f"Resolution alignment score: {alignment_score:.2f}"],
                supporting_data={"resolution": subject.dict()},
                processing_time_ms=timer.elapsed_milliseconds
            )
    
    @memoize
    def analyze_company_voting_record(
        self, 
        company_id: str, 
        resolutions: List[ShareholderResolution]
    ) -> VotingAnalysisResult:
        """Analyze voting patterns for a specific company.
        
        Args:
            company_id: ID of the company to analyze
            resolutions: List of all shareholder resolutions
            
        Returns:
            VotingAnalysisResult containing the analysis
        """
        # Use the Timer utility from common library
        with Timer("analyze_company_voting_record") as timer:
            # Check for a cached result first
            cached_result = self._get_from_cache(f"company_{company_id}")
            if cached_result:
                return cached_result
                
            # Filter resolutions for this company
            company_resolutions = [r for r in resolutions if r.company_id == company_id]
            
            if not company_resolutions:
                result = VotingAnalysisResult.from_analysis(
                    entity_id=company_id,
                    entity_type="company",
                    total_resolutions=0,
                    category_breakdown={},
                    passing_rate=0.0,
                    management_support_rate=0.0,
                    key_findings=["No resolutions found for this company"],
                    supporting_data={},
                    processing_time_ms=timer.elapsed_milliseconds
                )
                
                # Cache the result
                self._save_to_cache(f"company_{company_id}", result)
                
                return result
        
        # Count resolutions by category
        category_breakdown = {}
        for resolution in company_resolutions:
            category = resolution.category
            if category in category_breakdown:
                category_breakdown[category] += 1
            else:
                category_breakdown[category] = 1
        
        # Calculate passing rate
        voted_resolutions = [r for r in company_resolutions if r.outcome in ["passed", "failed"]]
        passed_resolutions = [r for r in voted_resolutions if r.outcome == "passed"]
        passing_rate = len(passed_resolutions) / len(voted_resolutions) if voted_resolutions else 0.0
        
        # Calculate management support rate
        resolutions_with_recommendation = [r for r in company_resolutions if r.company_recommendation]
        management_support_count = sum(1 for r in resolutions_with_recommendation 
                                     if r.company_recommendation == "for")
        management_support_rate = (management_support_count / len(resolutions_with_recommendation) 
                                  if resolutions_with_recommendation else 0.0)
        
        # Analyze voting patterns by category
        category_passing_rates = {}
        for category, count in category_breakdown.items():
            category_resolutions = [r for r in voted_resolutions if r.category == category]
            if category_resolutions:
                passed_in_category = sum(1 for r in category_resolutions if r.outcome == "passed")
                category_passing_rates[category] = passed_in_category / len(category_resolutions)
            else:
                category_passing_rates[category] = 0.0
        
        # Generate key findings
        key_findings = []
        
        # Overall voting patterns
        if passing_rate > 0.5:
            key_findings.append(f"High passing rate ({passing_rate:.1%}) of shareholder resolutions")
        elif passing_rate < 0.2:
            key_findings.append(f"Low passing rate ({passing_rate:.1%}) of shareholder resolutions")
        
        # Management support
        if management_support_rate < 0.1:
            key_findings.append("Management rarely supports shareholder resolutions")
        elif management_support_rate > 0.4:
            key_findings.append("Management frequently supports shareholder resolutions")
        
        # Category-specific findings
        for category, rate in category_passing_rates.items():
            count = category_breakdown[category]
            if count >= 3:  # Only for categories with sufficient data
                if rate > 0.7:
                    key_findings.append(f"Strong shareholder support for {category} resolutions ({rate:.1%} pass rate)")
                elif rate < 0.3:
                    key_findings.append(f"Weak shareholder support for {category} resolutions ({rate:.1%} pass rate)")
        
        # Compile supporting data
        supporting_data = {
            "resolutions": company_resolutions,
            "category_passing_rates": category_passing_rates,
            "recent_trends": self._analyze_trends(company_resolutions),
            "years_covered": sorted(set(r.year for r in company_resolutions))
        }
        
        result = VotingAnalysisResult.from_analysis(
            entity_id=company_id,
            entity_type="company",
            total_resolutions=len(company_resolutions),
            category_breakdown=category_breakdown,
            passing_rate=passing_rate,
            management_support_rate=management_support_rate,
            key_findings=key_findings,
            supporting_data=supporting_data,
            processing_time_ms=timer.elapsed_milliseconds
        )
        
        # Cache the result
        self._save_to_cache(f"company_{company_id}", result)
        
        return result
    
    @memoize
    def analyze_issue_voting_patterns(
        self, 
        issue_category: str,
        resolutions: List[ShareholderResolution]
    ) -> VotingAnalysisResult:
        """Analyze voting patterns for a specific ESG issue category.
        
        Args:
            issue_category: Category to analyze
            resolutions: List of all shareholder resolutions
            
        Returns:
            VotingAnalysisResult containing the analysis
        """
        # Use the Timer utility from common library
        with Timer("analyze_issue_voting_patterns") as timer:
            # Check for a cached result first
            cached_result = self._get_from_cache(f"category_{issue_category}")
            if cached_result:
                return cached_result
                
            # Filter resolutions for this category
            category_resolutions = [r for r in resolutions 
                                if r.category == issue_category or r.subcategory == issue_category]
            
            if not category_resolutions:
                result = VotingAnalysisResult.from_analysis(
                    entity_id=issue_category,
                    entity_type="resolution_category",
                    total_resolutions=0,
                    category_breakdown={},
                    passing_rate=0.0,
                    management_support_rate=0.0,
                    key_findings=[f"No resolutions found for category '{issue_category}'"],
                    supporting_data={},
                    processing_time_ms=timer.elapsed_milliseconds
                )
                
                # Cache the result
                self._save_to_cache(f"category_{issue_category}", result)
                
                return result
        
        # Count resolutions by company
        company_breakdown = {}
        for resolution in category_resolutions:
            company_id = resolution.company_id
            if company_id in company_breakdown:
                company_breakdown[company_id] += 1
            else:
                company_breakdown[company_id] = 1
        
        # Calculate passing rate
        voted_resolutions = [r for r in category_resolutions if r.outcome in ["passed", "failed"]]
        passed_resolutions = [r for r in voted_resolutions if r.outcome == "passed"]
        passing_rate = len(passed_resolutions) / len(voted_resolutions) if voted_resolutions else 0.0
        
        # Calculate management support rate
        resolutions_with_recommendation = [r for r in category_resolutions if r.company_recommendation]
        management_support_count = sum(1 for r in resolutions_with_recommendation 
                                     if r.company_recommendation == "for")
        management_support_rate = (management_support_count / len(resolutions_with_recommendation) 
                                  if resolutions_with_recommendation else 0.0)
        
        # Analyze by subcategory if main category
        subcategory_breakdown = {}
        for resolution in category_resolutions:
            if resolution.subcategory:
                subcategory = resolution.subcategory
                if subcategory in subcategory_breakdown:
                    subcategory_breakdown[subcategory] += 1
                else:
                    subcategory_breakdown[subcategory] = 1
        
        # Generate key findings
        key_findings = []
        
        # Overall voting patterns
        key_findings.append(f"Overall passing rate for {issue_category} resolutions: {passing_rate:.1%}")
        
        # Management support
        key_findings.append(f"Management support rate: {management_support_rate:.1%}")
        
        # Companies with most resolutions
        if company_breakdown:
            top_companies = sorted(company_breakdown.items(), key=lambda x: x[1], reverse=True)[:3]
            if top_companies:
                company_list = ", ".join(f"{company} ({count})" for company, count in top_companies)
                key_findings.append(f"Companies with most {issue_category} resolutions: {company_list}")
        
        # Subcategory findings
        if subcategory_breakdown:
            top_subcategories = sorted(subcategory_breakdown.items(), key=lambda x: x[1], reverse=True)[:3]
            if top_subcategories:
                subcategory_list = ", ".join(f"{subcat} ({count})" for subcat, count in top_subcategories)
                key_findings.append(f"Most common subcategories: {subcategory_list}")
        
        # Compile supporting data
        supporting_data = {
            "resolutions": category_resolutions,
            "company_breakdown": company_breakdown,
            "subcategory_breakdown": subcategory_breakdown,
            "recent_trends": self._analyze_trends(category_resolutions),
            "years_covered": sorted(set(r.year for r in category_resolutions))
        }
        
        result = VotingAnalysisResult.from_analysis(
            entity_id=issue_category,
            entity_type="resolution_category",
            total_resolutions=len(category_resolutions),
            category_breakdown=subcategory_breakdown,
            passing_rate=passing_rate,
            management_support_rate=management_support_rate,
            key_findings=key_findings,
            supporting_data=supporting_data,
            processing_time_ms=timer.elapsed_milliseconds
        )
        
        # Cache the result
        self._save_to_cache(f"category_{issue_category}", result)
        
        return result
    
    @memoize
    def generate_voting_recommendations(
        self, 
        upcoming_resolutions: List[ShareholderResolution],
        past_resolutions: List[ShareholderResolution]
    ) -> Dict[str, VotingRecommendation]:
        """Generate voting recommendations for upcoming shareholder resolutions.
        
        Args:
            upcoming_resolutions: List of upcoming resolutions
            past_resolutions: List of past resolutions for reference
            
        Returns:
            Dict mapping resolution IDs to VotingRecommendation objects
        """
        with Timer("generate_voting_recommendations") as timer:
            # Check for a cached result first
            cache_key = f"recommendations_{hash(tuple(r.resolution_id for r in upcoming_resolutions))}"
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                return cached_result
                
            recommendations = {}
            
            for resolution in upcoming_resolutions:
                # Calculate alignment score based on value priorities
                alignment_score = self._calculate_value_alignment(resolution)
                
                # Find similar past resolutions
                similar_resolutions = self._find_similar_resolutions(resolution, past_resolutions)
                
                # Determine recommendation based on alignment score
                if alignment_score > 0.3:
                    recommendation = "for"
                    confidence = min(0.9, 0.5 + alignment_score / 2)
                    rationale = f"Resolution aligns with values priorities (score: {alignment_score:.2f})"
                elif alignment_score < -0.3:
                    recommendation = "against"
                    confidence = min(0.9, 0.5 + abs(alignment_score) / 2)
                    rationale = f"Resolution conflicts with values priorities (score: {alignment_score:.2f})"
                else:
                    recommendation = "abstain"
                    confidence = max(0.5, 1 - abs(alignment_score) * 2)
                    rationale = f"Resolution has neutral alignment with values (score: {alignment_score:.2f})"
                
                # Adjust based on similar resolutions
                if similar_resolutions:
                    passed_count = sum(1 for r in similar_resolutions if r.outcome == "passed")
                    passed_rate = passed_count / len(similar_resolutions)
                    
                    if passed_rate > 0.7 and recommendation != "for":
                        confidence *= 0.8  # Reduce confidence if similar resolutions usually pass
                        rationale += f" (Note: {passed_rate:.0%} of similar resolutions have passed)"
                    elif passed_rate < 0.3 and recommendation == "for":
                        confidence *= 0.8  # Reduce confidence if similar resolutions rarely pass
                        rationale += f" (Note: Only {passed_rate:.0%} of similar resolutions have passed)"
                
                recommendations[resolution.resolution_id] = VotingRecommendation(
                    resolution_id=resolution.resolution_id,
                    company_id=resolution.company_id,
                    recommendation=recommendation,
                    confidence=confidence,
                    rationale=rationale,
                    alignment_score=alignment_score
                )
            
            # Cache the result
            self._save_to_cache(cache_key, recommendations)
            
            return recommendations
    
    @memoize
    def identify_engagement_opportunities(
        self,
        portfolio: Portfolio,
        past_resolutions: List[ShareholderResolution],
        threshold: float = 0.4
    ) -> List[Dict[str, Any]]:
        """Identify opportunities for shareholder engagement based on portfolio holdings.
        
        Args:
            portfolio: Portfolio containing investments
            past_resolutions: List of past shareholder resolutions
            threshold: Minimum alignment threshold for opportunity identification
            
        Returns:
            List of engagement opportunities with details
        """
        with Timer("identify_engagement_opportunities") as timer:
            # Check for a cached result
            cache_key = f"opportunities_{portfolio.id}_{threshold}"
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                return cached_result
                
            opportunities = []
            
            # Get companies in the portfolio
            portfolio_companies = set(holding.investment_id for holding in portfolio.holdings)
            
            # Group past resolutions by company
            company_resolutions = {}
            for resolution in past_resolutions:
                if resolution.company_id not in company_resolutions:
                    company_resolutions[resolution.company_id] = []
                company_resolutions[resolution.company_id].append(resolution)
            
            # Analyze each company in the portfolio
            for company_id in portfolio_companies:
                if company_id not in company_resolutions:
                    continue
                    
                company_res = company_resolutions[company_id]
                
                # Analyze by category
                category_stats = {}
                for resolution in company_res:
                    category = resolution.category
                    if category not in category_stats:
                        category_stats[category] = {"total": 0, "passed": 0, "alignment_sum": 0}
                    
                    category_stats[category]["total"] += 1
                    if resolution.outcome == "passed":
                        category_stats[category]["passed"] += 1
                    
                    alignment = self._calculate_value_alignment(resolution)
                    category_stats[category]["alignment_sum"] += alignment
                
                # Calculate average alignment and identify low-passing, high-alignment areas
                for category, stats in category_stats.items():
                    if stats["total"] >= 2:  # Only consider categories with sufficient data
                        avg_alignment = stats["alignment_sum"] / stats["total"]
                        passing_rate = stats["passed"] / stats["total"]
                        
                        # Opportunity if high alignment but low passing rate
                        if avg_alignment > threshold and passing_rate < 0.5:
                            opportunities.append({
                                "company_id": company_id,
                                "category": category,
                                "alignment_score": avg_alignment,
                                "passing_rate": passing_rate,
                                "resolution_count": stats["total"],
                                "opportunity_type": "support_aligned_resolutions",
                                "priority": avg_alignment * (1 - passing_rate)  # Higher for better alignment and lower passing
                            })
            
            # Sort opportunities by priority
            opportunities.sort(key=lambda x: x["priority"], reverse=True)
            
            # Cache the result
            self._save_to_cache(cache_key, opportunities)
            
            return opportunities
    
    @memoize
    def _calculate_value_alignment(self, resolution: ShareholderResolution) -> float:
        """Calculate how well a resolution aligns with value priorities.
        
        Args:
            resolution: The shareholder resolution to evaluate
            
        Returns:
            Alignment score from -1.0 (conflicts) to 1.0 (aligns)
        """
        with Timer("calculate_value_alignment") as timer:
            # Default neutral alignment
            alignment = 0.0
            
            # Check category alignment
            category = resolution.category
            subcategory = resolution.subcategory
            
            # Apply category weight if available
            if category in self.value_priorities:
                base_weight = self.value_priorities[category]
                alignment += base_weight / 2  # Initial alignment based on category
            
            # Apply subcategory weight if available
            if subcategory in self.value_priorities:
                subcat_weight = self.value_priorities[subcategory]
                alignment += subcat_weight / 2  # Additional alignment based on subcategory
            
            # Modify based on resolution title keywords
            title_lower = resolution.title.lower()
            
            # Positive alignment keywords
            positive_keywords = ["sustainability", "renewable", "diversity", "climate", "human rights", 
                                "transparency", "ethical", "community", "responsibility"]
            for keyword in positive_keywords:
                if keyword in title_lower:
                    alignment += 0.1
                    break  # Only apply once for positive keywords
            
            # Negative alignment keywords
            negative_keywords = ["deregulation", "compensation increase", "anti-regulation",
                                "political spending", "lobbying against"]
            for keyword in negative_keywords:
                if keyword in title_lower:
                    alignment -= 0.1
                    break  # Only apply once for negative keywords
            
            # Cap at -1.0 to 1.0
            return max(-1.0, min(1.0, alignment))
    
    @memoize
    def _find_similar_resolutions(
        self, 
        resolution: ShareholderResolution,
        past_resolutions: List[ShareholderResolution]
    ) -> List[ShareholderResolution]:
        """Find past resolutions similar to the given resolution.
        
        Args:
            resolution: The resolution to find similar ones for
            past_resolutions: List of past resolutions to search through
            
        Returns:
            List of similar past resolutions
        """
        with Timer("find_similar_resolutions") as timer:
            similar = []
            
            # Find resolutions with the same company and category
            for past in past_resolutions:
                if (past.company_id == resolution.company_id and 
                    past.category == resolution.category and
                    past.outcome in ["passed", "failed"]):
                    
                    # If subcategory matches, it's definitely similar
                    if past.subcategory and past.subcategory == resolution.subcategory:
                        similar.append(past)
                    # Otherwise check the title for keyword overlap
                    else:
                        current_keywords = set(resolution.title.lower().split())
                        past_keywords = set(past.title.lower().split())
                        
                        # If sufficient keyword overlap, consider it similar
                        if len(current_keywords.intersection(past_keywords)) >= 3:
                            similar.append(past)
            
            return similar
    
    @memoize
    def _analyze_trends(self, resolutions: List[ShareholderResolution]) -> Dict[str, Any]:
        """Analyze trends in resolutions over time.
        
        Args:
            resolutions: List of resolutions to analyze
            
        Returns:
            Dict containing trend analysis results
        """
        with Timer("analyze_trends") as timer:
            if not resolutions:
                return {"trend": "insufficient_data"}
                
            # Group by year
            by_year = {}
            for resolution in resolutions:
                year = resolution.year
                if year not in by_year:
                    by_year[year] = []
                by_year[year].append(resolution)
            
            # If only one year, no trend to analyze
            if len(by_year) < 2:
                return {"trend": "insufficient_data"}
            
            # Calculate passing rate by year
            passing_rates = {}
            for year, year_resolutions in by_year.items():
                voted = [r for r in year_resolutions if r.outcome in ["passed", "failed"]]
                if voted:
                    passing_rates[year] = sum(1 for r in voted if r.outcome == "passed") / len(voted)
                else:
                    passing_rates[year] = 0.0
            
            # Determine trend direction
            years = sorted(passing_rates.keys())
            if len(years) >= 2:
                first_year = years[0]
                last_year = years[-1]
                
                if passing_rates[last_year] > passing_rates[first_year] + 0.1:
                    trend = "increasing_support"
                elif passing_rates[first_year] > passing_rates[last_year] + 0.1:
                    trend = "decreasing_support"
                else:
                    trend = "stable_support"
            else:
                trend = "insufficient_data"
            
            return {
                "trend": trend,
                "passing_rates_by_year": passing_rates,
                "resolutions_by_year": {year: len(resolutions) for year, resolutions in by_year.items()}
            }