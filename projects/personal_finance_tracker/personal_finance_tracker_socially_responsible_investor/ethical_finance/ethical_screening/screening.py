"""Ethical screening framework for investment evaluation."""

from typing import Dict, List, Tuple, Any, Optional
import time
from dataclasses import dataclass

from ethical_finance.models import Investment, EthicalCriteria


@dataclass
class ScreeningResult:
    """Result of screening an investment against ethical criteria."""
    
    investment_id: str
    passed: bool
    overall_score: float
    environmental_score: float
    social_score: float
    governance_score: float
    exclusion_flags: List[str]
    inclusion_flags: List[str]
    details: Dict[str, Any]


class EthicalScreener:
    """Evaluates investments against customizable ethical criteria."""
    
    def __init__(self, criteria: EthicalCriteria):
        """Initialize with the given ethical criteria.
        
        Args:
            criteria: The ethical criteria to use for screening
        """
        self.criteria = criteria
    
    def screen_investment(self, investment: Investment) -> ScreeningResult:
        """Screen a single investment against the ethical criteria.
        
        Args:
            investment: The investment to screen
            
        Returns:
            A ScreeningResult with the screening outcome
        """
        # Start timing for performance benchmarking
        start_time = time.time()
        
        # Check for exclusions (immediate disqualification)
        exclusion_flags = self._check_exclusions(investment)
        
        # Check for inclusions (positive attributes)
        inclusion_flags = self._check_inclusions(investment)
        
        # Evaluate environmental criteria
        env_score, env_details = self._evaluate_environmental_criteria(investment)
        
        # Evaluate social criteria
        social_score, social_details = self._evaluate_social_criteria(investment)
        
        # Evaluate governance criteria
        gov_score, gov_details = self._evaluate_governance_criteria(investment)
        
        # Calculate weighted overall score
        overall_score = (
            env_score * self.criteria.environmental["weight"] +
            social_score * self.criteria.social["weight"] +
            gov_score * self.criteria.governance["weight"]
        )
        
        # Determine if the investment passes the screening
        passes = (
            len(exclusion_flags) == 0 and  # No exclusion criteria violated
            overall_score >= self.criteria.min_overall_score
        )
        
        # Compile detailed results
        details = {
            "environmental": env_details,
            "social": social_details,
            "governance": gov_details,
            "processing_time_ms": (time.time() - start_time) * 1000
        }
        
        return ScreeningResult(
            investment_id=investment.id,
            passed=passes,
            overall_score=overall_score,
            environmental_score=env_score,
            social_score=social_score,
            governance_score=gov_score,
            exclusion_flags=exclusion_flags,
            inclusion_flags=inclusion_flags,
            details=details
        )
    
    def screen_investments(self, investments: List[Investment]) -> Dict[str, ScreeningResult]:
        """Screen multiple investments against the ethical criteria.
        
        Args:
            investments: List of investments to screen
            
        Returns:
            Dict mapping investment IDs to their screening results
        """
        start_time = time.time()
        results = {}
        
        for investment in investments:
            results[investment.id] = self.screen_investment(investment)
        
        total_time = time.time() - start_time
        print(f"Screened {len(investments)} investments in {total_time:.2f} seconds")
        
        return results
    
    def _check_exclusions(self, investment: Investment) -> List[str]:
        """Check if the investment violates any exclusion criteria.
        
        Args:
            investment: The investment to check
            
        Returns:
            List of exclusion flags that apply to this investment
        """
        exclusion_flags = []
        
        # Check industry exclusions (from the top-level exclusions list)
        if investment.industry.lower() in [e.lower() for e in self.criteria.exclusions]:
            exclusion_flags.append(f"excluded_industry:{investment.industry}")
        
        # Check sector exclusions
        if investment.sector.lower() in [e.lower() for e in self.criteria.exclusions]:
            exclusion_flags.append(f"excluded_sector:{investment.sector}")
        
        # Check environmental exclusions
        if (self.criteria.environmental.get("exclude_fossil_fuel_production", False) and
                "fossil_fuel_production" in [p.lower() for p in investment.positive_practices + investment.controversies]):
            exclusion_flags.append("fossil_fuel_production")
        
        # Check social exclusions
        if (self.criteria.social.get("exclude_human_rights_violations", False) and
                "human_rights" in [c.lower() for c in investment.controversies]):
            exclusion_flags.append("human_rights_violations")
            
        if (self.criteria.social.get("exclude_weapons_manufacturing", False) and
                "weapons_manufacturing" in [p.lower() for p in investment.positive_practices + investment.controversies]):
            exclusion_flags.append("weapons_manufacturing")
        
        # Check governance exclusions
        if (self.criteria.governance.get("exclude_excessive_executive_compensation", False) and
                "excessive_compensation" in [c.lower() for c in investment.controversies]):
            exclusion_flags.append("excessive_executive_compensation")
        
        return exclusion_flags
    
    def _check_inclusions(self, investment: Investment) -> List[str]:
        """Check if the investment matches any inclusion criteria.
        
        Args:
            investment: The investment to check
            
        Returns:
            List of inclusion flags that apply to this investment
        """
        inclusion_flags = []
        
        # Check industry inclusions
        if investment.industry.lower() in [i.lower() for i in self.criteria.inclusions]:
            inclusion_flags.append(f"preferred_industry:{investment.industry}")
        
        # Check sector inclusions
        if investment.sector.lower() in [i.lower() for i in self.criteria.inclusions]:
            inclusion_flags.append(f"preferred_sector:{investment.sector}")
        
        # Check positive practices
        for practice in investment.positive_practices:
            if practice.lower() in [i.lower() for i in self.criteria.inclusions]:
                inclusion_flags.append(f"positive_practice:{practice}")
        
        return inclusion_flags
    
    def _evaluate_environmental_criteria(self, investment: Investment) -> Tuple[float, Dict[str, Any]]:
        """Evaluate the investment against environmental criteria.
        
        Args:
            investment: The investment to evaluate
            
        Returns:
            Tuple of (score, details) where score is 0-100 and details contains the reasoning
        """
        env_criteria = self.criteria.environmental
        details = {}
        
        # Start with the ESG environmental score
        base_score = investment.esg_ratings.environmental
        details["base_score"] = base_score
        
        # Adjust for carbon footprint
        if "max_carbon_footprint" in env_criteria:
            max_carbon = env_criteria["max_carbon_footprint"]
            if investment.carbon_footprint <= max_carbon:
                carbon_ratio = investment.carbon_footprint / max_carbon
                carbon_score = 100 - (carbon_ratio * 100)
                details["carbon_footprint_score"] = carbon_score
            else:
                # Exceeds maximum carbon footprint
                carbon_penalty = min(30, (investment.carbon_footprint / max_carbon - 1) * 20)
                base_score -= carbon_penalty
                details["carbon_footprint_penalty"] = carbon_penalty
        
        # Adjust for renewable energy use
        if "min_renewable_energy_use" in env_criteria:
            min_renewable = env_criteria["min_renewable_energy_use"]
            if investment.renewable_energy_use >= min_renewable:
                renewable_bonus = (investment.renewable_energy_use - min_renewable) * 50
                base_score += renewable_bonus
                details["renewable_energy_bonus"] = renewable_bonus
            else:
                # Below minimum renewable energy use
                renewable_penalty = min(20, (min_renewable - investment.renewable_energy_use) * 40)
                base_score -= renewable_penalty
                details["renewable_energy_penalty"] = renewable_penalty
        
        # Apply minimum environmental score threshold
        if "min_environmental_score" in env_criteria:
            min_score = env_criteria["min_environmental_score"]
            if base_score < min_score:
                details["below_min_threshold"] = True
        
        # Cap the final score at 100
        final_score = max(0, min(100, base_score))
        details["final_score"] = final_score
        
        return final_score, details
    
    def _evaluate_social_criteria(self, investment: Investment) -> Tuple[float, Dict[str, Any]]:
        """Evaluate the investment against social criteria.
        
        Args:
            investment: The investment to evaluate
            
        Returns:
            Tuple of (score, details) where score is 0-100 and details contains the reasoning
        """
        social_criteria = self.criteria.social
        details = {}
        
        # Start with the ESG social score
        base_score = investment.esg_ratings.social
        details["base_score"] = base_score
        
        # Adjust for diversity score
        if "min_diversity_score" in social_criteria:
            min_diversity = social_criteria["min_diversity_score"]
            if investment.diversity_score >= min_diversity:
                diversity_bonus = (investment.diversity_score - min_diversity) * 50
                base_score += diversity_bonus
                details["diversity_bonus"] = diversity_bonus
            else:
                # Below minimum diversity score
                diversity_penalty = min(20, (min_diversity - investment.diversity_score) * 40)
                base_score -= diversity_penalty
                details["diversity_penalty"] = diversity_penalty
        
        # Adjust for controversies
        controversy_count = len(investment.controversies)
        if controversy_count > 0:
            # More controversies means a larger penalty
            controversy_penalty = min(30, controversy_count * 10)
            base_score -= controversy_penalty
            details["controversy_penalty"] = controversy_penalty
            details["controversies"] = investment.controversies
        
        # Apply minimum social score threshold
        if "min_social_score" in social_criteria:
            min_score = social_criteria["min_social_score"]
            if base_score < min_score:
                details["below_min_threshold"] = True
        
        # Cap the final score at 100
        final_score = max(0, min(100, base_score))
        details["final_score"] = final_score
        
        return final_score, details
    
    def _evaluate_governance_criteria(self, investment: Investment) -> Tuple[float, Dict[str, Any]]:
        """Evaluate the investment against governance criteria.
        
        Args:
            investment: The investment to evaluate
            
        Returns:
            Tuple of (score, details) where score is 0-100 and details contains the reasoning
        """
        gov_criteria = self.criteria.governance
        details = {}
        
        # Start with the ESG governance score
        base_score = investment.esg_ratings.governance
        details["base_score"] = base_score
        
        # Adjust for board independence
        if "min_board_independence" in gov_criteria:
            min_independence = gov_criteria["min_board_independence"]
            if investment.board_independence >= min_independence:
                independence_bonus = (investment.board_independence - min_independence) * 50
                base_score += independence_bonus
                details["board_independence_bonus"] = independence_bonus
            else:
                # Below minimum board independence
                independence_penalty = min(20, (min_independence - investment.board_independence) * 40)
                base_score -= independence_penalty
                details["board_independence_penalty"] = independence_penalty
        
        # Apply minimum governance score threshold
        if "min_governance_score" in gov_criteria:
            min_score = gov_criteria["min_governance_score"]
            if base_score < min_score:
                details["below_min_threshold"] = True
        
        # Cap the final score at 100
        final_score = max(0, min(100, base_score))
        details["final_score"] = final_score
        
        return final_score, details


def create_default_criteria() -> EthicalCriteria:
    """Create a default set of ethical screening criteria.
    
    Returns:
        A default EthicalCriteria object
    """
    return EthicalCriteria(
        criteria_id="default",
        name="Default Ethical Criteria",
        environmental={
            "min_environmental_score": 60,
            "max_carbon_footprint": 50000000,
            "min_renewable_energy_use": 0.5,
            "exclude_fossil_fuel_production": True,
            "weight": 0.4
        },
        social={
            "min_social_score": 65,
            "min_diversity_score": 0.6,
            "exclude_human_rights_violations": True,
            "exclude_weapons_manufacturing": True,
            "weight": 0.3
        },
        governance={
            "min_governance_score": 70,
            "min_board_independence": 0.7,
            "exclude_excessive_executive_compensation": True,
            "weight": 0.3
        },
        exclusions=[
            "tobacco",
            "gambling",
            "adult_entertainment",
            "military_contracting"
        ],
        inclusions=[
            "renewable_energy",
            "sustainable_agriculture",
            "education",
            "healthcare"
        ],
        min_overall_score=65
    )