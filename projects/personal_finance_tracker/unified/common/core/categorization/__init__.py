"""Categorization framework shared across implementations."""

from common.core.categorization.rule import (
    Rule,
    TextMatchRule,
    TransactionRule,
    CompositeRule,
    ValueThresholdRule,
)

from common.core.categorization.categorizer import (
    BaseCategorizer,
    CategorizationResult,
    AuditRecord,
)

from common.core.categorization.transaction_categorizer import (
    TransactionCategorizer,
    MixedUseItem,
)

from common.core.categorization.investment_categorizer import (
    InvestmentCategorizer,
    ScreeningResult,
)

__all__ = [
    # Rule models
    "Rule",
    "TextMatchRule",
    "TransactionRule",
    "CompositeRule",
    "ValueThresholdRule",
    
    # Base categorization
    "BaseCategorizer",
    "CategorizationResult",
    "AuditRecord",
    
    # Transaction categorization
    "TransactionCategorizer",
    "MixedUseItem",
    
    # Investment categorization
    "InvestmentCategorizer",
    "ScreeningResult",
]