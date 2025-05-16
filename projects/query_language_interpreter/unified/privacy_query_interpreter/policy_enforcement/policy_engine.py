"""Privacy policy engine implementation using common policy framework."""

from typing import Any, Dict, List, Optional, Set, Tuple
import time

from common.policy.engine import BasePolicyEngine, PolicyViolation
from common.policy.rule import PolicyRule, PermissionRule, RoleRule, SimpleRule
from common.policy.context import PolicyContext

from privacy_query_interpreter.policy_enforcement.policy import (
    DataPolicy,
    PolicyAction,
    PolicySet,
    PolicyType,
    FieldCategory,
)


class PrivacyPolicyEngine(BasePolicyEngine):
    """Privacy-specific policy engine extending the common policy framework."""

    def __init__(
        self,
        policies: Optional[PolicySet] = None,
        field_categories: Optional[Dict[str, List[FieldCategory]]] = None,
    ):
        """Initialize the privacy policy engine.

        Args:
            policies: PolicySet containing data access policies
            field_categories: Optional mapping of field names to categories
        """
        super().__init__()
        self.policy_set = policies or PolicySet(name="Default", policies=[])
        self.field_categories = field_categories or {}

        # Convert privacy policies to common policy rules
        self._convert_policies_to_rules()

    def _convert_policies_to_rules(self) -> None:
        """Convert privacy-specific policies to common policy rules."""
        for policy in self.policy_set.policies:
            if not policy.enabled:
                continue

            # Create rules based on policy type
            if policy.policy_type == PolicyType.FIELD_ACCESS:
                self._create_field_access_rules(policy)
            elif policy.policy_type == PolicyType.DATA_COMBINATION:
                self._create_data_combination_rules(policy)
            elif policy.policy_type == PolicyType.QUERY_SCOPE:
                self._create_query_scope_rules(policy)

    def _create_field_access_rules(self, policy: DataPolicy) -> None:
        """Create field access rules from a policy.

        Args:
            policy: DataPolicy to convert
        """
        if not policy.restricted_fields:
            return

        for field in policy.restricted_fields:
            # Create role-based rule
            if policy.allowed_roles:
                rule_id = f"{policy.id}_role_{field}"
                self.add_rule(
                    RoleRule(
                        rule_id=rule_id,
                        allowed_roles=policy.allowed_roles,
                        description=f"Field '{field}' requires roles: {', '.join(policy.allowed_roles)}",
                        actions=["field_access"],
                        severity="high",
                        require_all=False,
                    )
                )

            # Create purpose-based rule if needed
            if hasattr(policy, 'required_purpose') and policy.required_purpose:
                def check_purpose(context: PolicyContext) -> bool:
                    purpose = context.get("purpose", "")
                    return purpose in policy.required_purpose

                rule_id = f"{policy.id}_purpose_{field}"
                self.add_rule(
                    SimpleRule(
                        rule_id=rule_id,
                        evaluation_func=check_purpose,
                        description=f"Field '{field}' requires purpose: {', '.join(policy.required_purpose)}",
                        actions=["field_access"],
                        severity="medium",
                    )
                )

    def _create_data_combination_rules(self, policy: DataPolicy) -> None:
        """Create data combination rules from a policy.

        Args:
            policy: DataPolicy to convert
        """
        # Create role-based rule
        if policy.allowed_roles:
            rule_id = f"{policy.id}_role"
            self.add_rule(
                RoleRule(
                    rule_id=rule_id,
                    allowed_roles=policy.allowed_roles,
                    description=f"Data combination requires roles: {', '.join(policy.allowed_roles)}",
                    actions=["data_combination"],
                    severity="high",
                    require_all=False,
                )
            )

        # Create purpose-based rule if needed
        if hasattr(policy, 'required_purpose') and policy.required_purpose:
            def check_purpose(context: PolicyContext) -> bool:
                purpose = context.get("purpose", "")
                return purpose in policy.required_purpose

            rule_id = f"{policy.id}_purpose"
            self.add_rule(
                SimpleRule(
                    rule_id=rule_id,
                    evaluation_func=check_purpose,
                    description=f"Data combination requires purpose: {', '.join(policy.required_purpose)}",
                    actions=["data_combination"],
                    severity="medium",
                )
            )

        # Create prohibited combination rule if needed
        if policy.prohibited_combinations:
            def check_combinations(context: PolicyContext) -> bool:
                fields = context.get("fields", [])

                for combo in policy.prohibited_combinations:
                    if all(field in fields for field in combo.fields or []):
                        return False
                return True

            rule_id = f"{policy.id}_prohibited_combinations"
            self.add_rule(
                SimpleRule(
                    rule_id=rule_id,
                    evaluation_func=check_combinations,
                    description="Prohibited field combinations",
                    actions=["data_combination"],
                    severity="high",
                )
            )

    def _create_query_scope_rules(self, policy: DataPolicy) -> None:
        """Create query scope rules from a policy.

        Args:
            policy: DataPolicy to convert
        """
        # Create role-based rule
        if policy.allowed_roles:
            rule_id = f"{policy.id}_role"
            self.add_rule(
                RoleRule(
                    rule_id=rule_id,
                    allowed_roles=policy.allowed_roles,
                    description=f"Query access requires roles: {', '.join(policy.allowed_roles)}",
                    actions=["query_execution"],
                    severity="high",
                    require_all=False,
                )
            )

        # Create purpose-based rule if needed
        if hasattr(policy, 'required_purpose') and policy.required_purpose:
            def check_purpose(context: PolicyContext) -> bool:
                purpose = context.get("purpose", "")
                return purpose in policy.required_purpose

            rule_id = f"{policy.id}_purpose"
            self.add_rule(
                SimpleRule(
                    rule_id=rule_id,
                    evaluation_func=check_purpose,
                    description=f"Query access requires purpose: {', '.join(policy.required_purpose)}",
                    actions=["query_execution"],
                    severity="medium",
                )
            )

        # Create data source rule if needed
        if policy.prohibited_data_sources:
            def check_data_sources(context: PolicyContext) -> bool:
                data_sources = context.get("data_sources", [])

                for ds in data_sources:
                    if ds in policy.prohibited_data_sources:
                        return False
                return True

            rule_id = f"{policy.id}_data_sources"
            self.add_rule(
                SimpleRule(
                    rule_id=rule_id,
                    evaluation_func=check_data_sources,
                    description="Restricted data sources",
                    actions=["query_execution"],
                    severity="high",
                )
            )

        # Create join rule if needed
        if policy.prohibited_joins:
            def check_joins(context: PolicyContext) -> bool:
                joins = context.get("joins", [])

                for j1, j2 in joins:
                    if (j1, j2) in policy.prohibited_joins or (
                        j2,
                        j1,
                    ) in policy.prohibited_joins:
                        return False
                return True

            rule_id = f"{policy.id}_joins"
            self.add_rule(
                SimpleRule(
                    rule_id=rule_id,
                    evaluation_func=check_joins,
                    description="Prohibited joins",
                    actions=["query_execution"],
                    severity="high",
                )
            )

    def enforce_query(
        self,
        query_text: str,
        fields: List[str],
        data_sources: List[str],
        joins: List[Tuple[str, str]],
        user_context: Dict[str, Any],
    ) -> Tuple[bool, PolicyAction, Optional[str]]:
        """Enforce policies for a structured query.

        Args:
            query_text: The query text
            fields: Fields accessed by the query
            data_sources: Data sources accessed
            joins: Table joins being performed
            user_context: User context (roles, purpose, etc.)

        Returns:
            Tuple of (is_allowed, action, reason)
        """
        # Convert to policy context
        context = PolicyContext(
            {
                "query_text": query_text,
                "fields": fields,
                "data_sources": data_sources,
                "joins": joins,
                **user_context,
            }
        )

        # Check policy violations
        violations = self.get_violations("query_execution", context)

        if violations:
            # Return the first violation with its action
            violation = violations[0]
            return (False, PolicyAction.DENY, violation.message)

        return (True, PolicyAction.ALLOW, None)

    def enforce_field_access(
        self, fields: List[str], data_source: str, user_context: Dict[str, Any]
    ) -> Tuple[List[str], List[str], PolicyAction, Optional[str]]:
        """Enforce field-level access policies.

        Args:
            fields: Fields to be accessed
            data_source: Data source being accessed
            user_context: User context (roles, purpose, etc.)

        Returns:
            Tuple of (allowed_fields, denied_fields, action, reason)
        """
        allowed_fields = []
        denied_fields = []

        for field in fields:
            # Create context for this field
            context = PolicyContext(
                {"field": field, "data_source": data_source, **user_context}
            )

            # Check policy violations
            violations = self.get_violations("field_access", context)

            if violations:
                denied_fields.append(field)
            else:
                allowed_fields.append(field)

        # Determine overall action and reason
        if denied_fields:
            return (
                allowed_fields,
                denied_fields,
                PolicyAction.DENY,
                f"Access denied to fields: {', '.join(denied_fields)}",
            )

        return (allowed_fields, [], PolicyAction.ALLOW, None)

    def enforce_data_combination(
        self, fields: List[str], user_context: Dict[str, Any]
    ) -> Tuple[bool, PolicyAction, Optional[str]]:
        """Enforce policies on field combinations.

        Args:
            fields: Fields to be combined
            user_context: User context (roles, purpose, etc.)

        Returns:
            Tuple of (is_allowed, action, reason)
        """
        # Convert to policy context
        context = PolicyContext({"fields": fields, **user_context})

        # Check policy violations
        violations = self.get_violations("data_combination", context)

        if violations:
            # Return the first violation with its action
            violation = violations[0]
            return (False, PolicyAction.DENY, violation.message)

        return (True, PolicyAction.ALLOW, None)

    def add_policy(self, policy: DataPolicy) -> None:
        """Add a policy to the engine.

        Args:
            policy: DataPolicy to add
        """
        self.policy_set.add_policy(policy)

        # Convert the new policy to rules
        if policy.enabled:
            if policy.policy_type == PolicyType.FIELD_ACCESS:
                self._create_field_access_rules(policy)
            elif policy.policy_type == PolicyType.DATA_COMBINATION:
                self._create_data_combination_rules(policy)
            elif policy.policy_type == PolicyType.QUERY_SCOPE:
                self._create_query_scope_rules(policy)

    def load_policies(self, policy_set: PolicySet) -> None:
        """Load a complete policy set.

        Args:
            policy_set: PolicySet to load
        """
        self.policy_set = policy_set

        # Clear existing rules
        self.rules.clear()

        # Convert policies to rules
        self._convert_policies_to_rules()