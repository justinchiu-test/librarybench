"""Portfolio analysis utilities shared across implementations."""

import time
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID

import numpy as np
from pydantic import BaseModel, Field

from common.core.analysis.analyzer import BaseAnalyzer, AnalysisResult, AnalysisParameters
from common.core.models.investment import Portfolio, InvestmentHolding, Investment


class PortfolioAnalysisParameters(AnalysisParameters):
    """
    Parameters for portfolio analysis.
    
    Used to configure portfolio analysis options and settings.
    """
    
    include_sector_breakdown: bool = True
    include_esg_analysis: bool = True
    include_performance_metrics: bool = True
    compare_to_benchmark: bool = False
    benchmark_id: Optional[str] = None
    risk_free_rate: float = 0.02  # For Sharpe ratio calculation


class PortfolioBreakdown(BaseModel):
    """
    Breakdown of a portfolio by different dimensions.
    
    Used for analyzing portfolio composition and diversity.
    """
    
    by_sector: Dict[str, float] = Field(default_factory=dict)
    by_industry: Dict[str, float] = Field(default_factory=dict)
    by_market_cap: Dict[str, float] = Field(default_factory=dict)
    by_esg_rating: Dict[str, float] = Field(default_factory=dict)
    by_region: Dict[str, float] = Field(default_factory=dict)
    concentration_metrics: Dict[str, float] = Field(default_factory=dict)


class PortfolioPerformance(BaseModel):
    """
    Performance metrics for a portfolio.
    
    Used for analyzing historical and risk-adjusted returns.
    """
    
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    alpha: Optional[float] = None
    beta: Optional[float] = None
    correlation_to_benchmark: Optional[float] = None


class PortfolioESGMetrics(BaseModel):
    """
    ESG metrics for a portfolio.
    
    Used for analyzing environmental, social, and governance characteristics.
    """
    
    overall_esg_score: float
    environmental_score: float
    social_score: float
    governance_score: float
    carbon_footprint: float
    renewable_energy_exposure: float
    diversity_score: float
    controversy_exposure: float
    impact_metrics: Dict[str, float] = Field(default_factory=dict)


class PortfolioAnalysisResult(AnalysisResult):
    """
    Result of a portfolio analysis operation.
    
    Provides detailed information about portfolio composition and performance.
    """
    
    breakdown: PortfolioBreakdown
    performance: Optional[PortfolioPerformance] = None
    esg_metrics: Optional[PortfolioESGMetrics] = None
    diversification_score: float
    risk_exposure: Dict[str, float] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)


class PortfolioAnalyzer(BaseAnalyzer[Portfolio, PortfolioAnalysisResult]):
    """
    Analyzer for investment portfolios.
    
    Used for portfolio composition, performance, and ESG analysis.
    """
    
    def __init__(self, investments: Dict[str, Investment]):
        """
        Initialize with a database of available investments.
        
        Args:
            investments: Dictionary mapping investment IDs to Investment objects
        """
        super().__init__()
        self.investments = investments
    
    def analyze(
        self, portfolio: Portfolio, parameters: Optional[PortfolioAnalysisParameters] = None
    ) -> PortfolioAnalysisResult:
        """
        Analyze a portfolio.
        
        Args:
            portfolio: The portfolio to analyze
            parameters: Optional parameters to configure the analysis
            
        Returns:
            Portfolio analysis result
        """
        # Start timing for performance benchmarking
        start_time = time.time()
        
        # Set default parameters if not provided
        if parameters is None:
            parameters = PortfolioAnalysisParameters()
        
        # Check cache unless details have changed
        cached_result = self._get_from_cache(portfolio.id, parameters)
        if cached_result and cached_result.analysis_date > portfolio.last_updated:
            return cached_result
        
        # Build the portfolio breakdown
        breakdown = self._calculate_portfolio_breakdown(portfolio)
        
        # Calculate performance metrics if requested
        performance = None
        if parameters.include_performance_metrics:
            performance = self._calculate_performance_metrics(
                portfolio, parameters.risk_free_rate, parameters.benchmark_id
            )
        
        # Calculate ESG metrics if requested
        esg_metrics = None
        if parameters.include_esg_analysis:
            esg_metrics = self._calculate_esg_metrics(portfolio)
        
        # Calculate diversification score
        diversification_score = self._calculate_diversification_score(breakdown)
        
        # Identify risk exposures
        risk_exposure = self._identify_risk_exposures(portfolio, breakdown)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            portfolio, breakdown, diversification_score, risk_exposure
        )
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Create the result
        result = PortfolioAnalysisResult(
            id=UUID(),
            subject_id=portfolio.id,
            subject_type="portfolio",
            analysis_type="comprehensive",
            analysis_date=datetime.now(),
            processing_time_ms=processing_time_ms,
            result_summary={
                "total_value": portfolio.total_value,
                "num_holdings": len(portfolio.holdings),
                "diversification_score": diversification_score,
                "top_sector": self._get_top_category(breakdown.by_sector),
                "top_industry": self._get_top_category(breakdown.by_industry),
            },
            detailed_results={
                "holdings": [
                    {
                        "investment_id": h.investment_id,
                        "weight": (h.current_value / portfolio.total_value) if portfolio.total_value > 0 else 0,
                    }
                    for h in portfolio.holdings
                ],
            },
            breakdown=breakdown,
            performance=performance,
            esg_metrics=esg_metrics,
            diversification_score=diversification_score,
            risk_exposure=risk_exposure,
            recommendations=recommendations,
        )
        
        # Save to cache
        self._save_to_cache(portfolio.id, result, parameters)
        
        return result
    
    def _calculate_portfolio_breakdown(self, portfolio: Portfolio) -> PortfolioBreakdown:
        """
        Calculate the breakdown of a portfolio by different dimensions.
        
        Args:
            portfolio: The portfolio to analyze
            
        Returns:
            PortfolioBreakdown with composition details
        """
        # Initialize counters
        by_sector = {}
        by_industry = {}
        by_market_cap = {}
        by_esg_rating = {}
        by_region = {}
        
        # Calculate the weight of each holding
        total_value = portfolio.total_value
        if total_value <= 0:
            # Return empty breakdown for empty portfolio
            return PortfolioBreakdown()
        
        # Analyze each holding
        for holding in portfolio.holdings:
            weight = holding.current_value / total_value
            investment = self.investments.get(holding.investment_id)
            
            if investment:
                # Sector breakdown
                sector = investment.sector
                by_sector[sector] = by_sector.get(sector, 0) + weight
                
                # Industry breakdown
                industry = investment.industry
                by_industry[industry] = by_industry.get(industry, 0) + weight
                
                # Market cap breakdown
                market_cap_category = self._categorize_market_cap(investment.market_cap)
                by_market_cap[market_cap_category] = by_market_cap.get(market_cap_category, 0) + weight
                
                # ESG rating breakdown
                esg_category = self._categorize_esg_rating(investment.esg_ratings.overall)
                by_esg_rating[esg_category] = by_esg_rating.get(esg_category, 0) + weight
                
                # Region breakdown (placeholder - would need region data)
                region = "unknown"
                by_region[region] = by_region.get(region, 0) + weight
        
        # Calculate concentration metrics
        concentration_metrics = {
            "herfindahl_index": self._calculate_herfindahl_index(by_sector),
            "top_5_holdings_weight": self._calculate_top_n_weight(portfolio.holdings, total_value, 5),
            "sector_count": len(by_sector),
            "industry_count": len(by_industry),
        }
        
        return PortfolioBreakdown(
            by_sector=by_sector,
            by_industry=by_industry,
            by_market_cap=by_market_cap,
            by_esg_rating=by_esg_rating,
            by_region=by_region,
            concentration_metrics=concentration_metrics,
        )
    
    def _calculate_performance_metrics(
        self, portfolio: Portfolio, risk_free_rate: float, benchmark_id: Optional[str]
    ) -> PortfolioPerformance:
        """
        Calculate performance metrics for a portfolio.
        
        Args:
            portfolio: The portfolio to analyze
            risk_free_rate: The risk-free rate for Sharpe ratio calculation
            benchmark_id: Optional benchmark portfolio ID for comparison
            
        Returns:
            PortfolioPerformance with performance metrics
        """
        # This would require historical price data, which we don't have.
        # In a real implementation, we would retrieve historical data and calculate returns.
        # For now, we'll use placeholder values.
        
        # Get total return from current data
        total_return = 0.0
        total_investment = 0.0
        
        for holding in portfolio.holdings:
            total_investment += holding.shares * holding.purchase_price
            total_return += holding.shares * (holding.current_price - holding.purchase_price)
        
        return_pct = (total_return / total_investment) if total_investment > 0 else 0.0
        
        # Placeholder values for other metrics
        annualized_return = return_pct  # Simplified
        volatility = 0.15  # Placeholder
        sharpe_ratio = (annualized_return - risk_free_rate) / volatility if volatility > 0 else 0
        max_drawdown = 0.1  # Placeholder
        
        return PortfolioPerformance(
            total_return=return_pct,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
        )
    
    def _calculate_esg_metrics(self, portfolio: Portfolio) -> PortfolioESGMetrics:
        """
        Calculate ESG metrics for a portfolio.
        
        Args:
            portfolio: The portfolio to analyze
            
        Returns:
            PortfolioESGMetrics with ESG characteristics
        """
        # Initialize counters for weighted average calculation
        weighted_env_score = 0.0
        weighted_social_score = 0.0
        weighted_gov_score = 0.0
        weighted_overall_score = 0.0
        weighted_carbon_footprint = 0.0
        weighted_renewable_energy = 0.0
        weighted_diversity = 0.0
        weighted_controversy = 0.0
        
        # Calculate the weight of each holding
        total_value = portfolio.total_value
        if total_value <= 0:
            # Return default metrics for empty portfolio
            return PortfolioESGMetrics(
                overall_esg_score=0.0,
                environmental_score=0.0,
                social_score=0.0,
                governance_score=0.0,
                carbon_footprint=0.0,
                renewable_energy_exposure=0.0,
                diversity_score=0.0,
                controversy_exposure=0.0,
            )
        
        # Calculate weighted ESG metrics
        for holding in portfolio.holdings:
            weight = holding.current_value / total_value
            investment = self.investments.get(holding.investment_id)
            
            if investment:
                weighted_env_score += investment.esg_ratings.environmental * weight
                weighted_social_score += investment.esg_ratings.social * weight
                weighted_gov_score += investment.esg_ratings.governance * weight
                weighted_overall_score += investment.esg_ratings.overall * weight
                weighted_carbon_footprint += investment.carbon_footprint * weight
                weighted_renewable_energy += investment.renewable_energy_use * weight
                weighted_diversity += investment.diversity_score * weight
                weighted_controversy += len(investment.controversies) * weight
        
        return PortfolioESGMetrics(
            overall_esg_score=weighted_overall_score,
            environmental_score=weighted_env_score,
            social_score=weighted_social_score,
            governance_score=weighted_gov_score,
            carbon_footprint=weighted_carbon_footprint,
            renewable_energy_exposure=weighted_renewable_energy,
            diversity_score=weighted_diversity,
            controversy_exposure=weighted_controversy,
            impact_metrics={
                "carbon_reduction": weighted_renewable_energy * 100,
                "social_impact": weighted_social_score,
            },
        )
    
    def _calculate_diversification_score(self, breakdown: PortfolioBreakdown) -> float:
        """
        Calculate a diversification score for a portfolio.
        
        Args:
            breakdown: The portfolio breakdown
            
        Returns:
            Diversification score between 0 and 1
        """
        # Calculate based on Herfindahl index (1 - concentration)
        herfindahl = breakdown.concentration_metrics.get("herfindahl_index", 1.0)
        sector_score = 1.0 - herfindahl
        
        # Adjust based on number of sectors and industries
        sector_count = breakdown.concentration_metrics.get("sector_count", 0)
        industry_count = breakdown.concentration_metrics.get("industry_count", 0)
        
        sector_factor = min(1.0, sector_count / 10)
        industry_factor = min(1.0, industry_count / 20)
        
        # Final score is a weighted average
        return 0.5 * sector_score + 0.3 * sector_factor + 0.2 * industry_factor
    
    def _identify_risk_exposures(
        self, portfolio: Portfolio, breakdown: PortfolioBreakdown
    ) -> Dict[str, float]:
        """
        Identify key risk exposures in a portfolio.
        
        Args:
            portfolio: The portfolio to analyze
            breakdown: The portfolio breakdown
            
        Returns:
            Dictionary mapping risk types to exposure levels
        """
        risk_exposure = {}
        
        # Concentration risk
        top_5_weight = breakdown.concentration_metrics.get("top_5_holdings_weight", 0.0)
        risk_exposure["concentration_risk"] = top_5_weight
        
        # Sector concentration risk
        top_sector = self._get_top_category(breakdown.by_sector)
        top_sector_weight = breakdown.by_sector.get(top_sector, 0.0) if top_sector else 0.0
        risk_exposure["sector_concentration_risk"] = top_sector_weight
        
        # ESG risk
        if "Lowest" in breakdown.by_esg_rating:
            risk_exposure["esg_risk"] = breakdown.by_esg_rating["Lowest"]
        else:
            risk_exposure["esg_risk"] = 0.0
        
        # Market cap risk
        if "Small" in breakdown.by_market_cap:
            risk_exposure["small_cap_risk"] = breakdown.by_market_cap["Small"]
        else:
            risk_exposure["small_cap_risk"] = 0.0
        
        return risk_exposure
    
    def _generate_recommendations(
        self,
        portfolio: Portfolio,
        breakdown: PortfolioBreakdown,
        diversification_score: float,
        risk_exposure: Dict[str, float],
    ) -> List[str]:
        """
        Generate portfolio improvement recommendations.
        
        Args:
            portfolio: The portfolio to analyze
            breakdown: The portfolio breakdown
            diversification_score: The calculated diversification score
            risk_exposure: The identified risk exposures
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Diversification recommendations
        if diversification_score < 0.4:
            recommendations.append(
                "Low diversification detected. Consider adding investments from more sectors."
            )
        elif diversification_score < 0.7:
            recommendations.append(
                "Moderate diversification. Consider reducing exposure to your top sector."
            )
        
        # Concentration risk
        if risk_exposure.get("concentration_risk", 0.0) > 0.6:
            recommendations.append(
                "High concentration in top holdings. Consider rebalancing for better risk management."
            )
        
        # Sector concentration
        if risk_exposure.get("sector_concentration_risk", 0.0) > 0.4:
            top_sector = self._get_top_category(breakdown.by_sector)
            recommendations.append(
                f"High exposure to {top_sector} sector. Consider diversifying into other sectors."
            )
        
        # ESG recommendations
        if risk_exposure.get("esg_risk", 0.0) > 0.2:
            recommendations.append(
                "Significant exposure to low-rated ESG investments. Consider alternatives with better ESG profiles."
            )
        
        return recommendations
    
    def _categorize_market_cap(self, market_cap: float) -> str:
        """
        Categorize an investment by market cap.
        
        Args:
            market_cap: The market capitalization value
            
        Returns:
            Market cap category string
        """
        if market_cap >= 10_000_000_000:
            return "Large"
        elif market_cap >= 2_000_000_000:
            return "Mid"
        else:
            return "Small"
    
    def _categorize_esg_rating(self, rating: int) -> str:
        """
        Categorize an investment by ESG rating.
        
        Args:
            rating: The ESG rating value
            
        Returns:
            ESG rating category string
        """
        if rating >= 80:
            return "Highest"
        elif rating >= 60:
            return "High"
        elif rating >= 40:
            return "Medium"
        elif rating >= 20:
            return "Low"
        else:
            return "Lowest"
    
    def _calculate_herfindahl_index(self, weights: Dict[str, float]) -> float:
        """
        Calculate the Herfindahl index (measure of concentration).
        
        Args:
            weights: Dictionary mapping categories to weights
            
        Returns:
            Herfindahl index value between 0 and 1
        """
        return sum(weight ** 2 for weight in weights.values())
    
    def _calculate_top_n_weight(
        self, holdings: List[InvestmentHolding], total_value: float, n: int
    ) -> float:
        """
        Calculate the weight of the top N holdings.
        
        Args:
            holdings: List of investment holdings
            total_value: Total portfolio value
            n: Number of top holdings to consider
            
        Returns:
            Total weight of top N holdings
        """
        if not holdings or total_value <= 0:
            return 0.0
        
        # Sort holdings by value (descending)
        sorted_holdings = sorted(
            holdings, key=lambda h: h.current_value, reverse=True
        )
        
        # Get the top N holdings
        top_n = sorted_holdings[:min(n, len(sorted_holdings))]
        
        # Calculate their total weight
        top_n_value = sum(h.current_value for h in top_n)
        
        return top_n_value / total_value
    
    def _get_top_category(self, categories: Dict[str, float]) -> Optional[str]:
        """
        Get the top category by weight.
        
        Args:
            categories: Dictionary mapping categories to weights
            
        Returns:
            The top category or None if empty
        """
        if not categories:
            return None
        
        return max(categories.items(), key=lambda x: x[1])[0]