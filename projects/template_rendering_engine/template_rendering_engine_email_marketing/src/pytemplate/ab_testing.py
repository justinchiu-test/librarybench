"""A/B test variant generator for email campaigns."""

from typing import Any, Dict, List
from pydantic import BaseModel, Field
from copy import deepcopy
import itertools


class VariantElement(BaseModel):
    """Definition of an element that can vary in A/B tests."""

    name: str = Field(description="Name of the variant element")
    path: str = Field(description="Path to the element in template structure")
    variants: List[Any] = Field(description="List of variant values")
    element_type: str = Field(
        default="content", description="Type: content, subject, cta, etc."
    )


class ABTestConfig(BaseModel):
    """Configuration for A/B test generation."""

    test_name: str = Field(description="Name of the A/B test")
    variant_elements: List[VariantElement] = Field(description="Elements to vary")
    control_group_size: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Size of control group"
    )
    generate_all_combinations: bool = Field(
        default=False, description="Generate all possible combinations"
    )


class EmailVariant(BaseModel):
    """A single email variant with metadata."""

    variant_id: str = Field(description="Unique identifier for the variant")
    variant_name: str = Field(description="Human-readable name")
    subject: str = Field(description="Email subject line")
    content: str = Field(description="Email HTML content")
    variant_attributes: Dict[str, Any] = Field(
        description="Attributes that define this variant"
    )
    is_control: bool = Field(
        default=False, description="Whether this is the control variant"
    )


class ABTestGenerator:
    """Generator for creating A/B test variants from templates."""

    def generate_variants(
        self, base_template: Dict[str, Any], config: ABTestConfig
    ) -> List[EmailVariant]:
        """
        Generate email variants based on configuration.

        Args:
            base_template: Base template structure with subject and content
            config: A/B test configuration

        Returns:
            List of email variants
        """
        variants = []

        # Create control variant
        control_variant = self._create_variant(
            base_template,
            variant_id=f"{config.test_name}_control",
            variant_name="Control",
            variant_attributes={},
            is_control=True,
        )
        variants.append(control_variant)

        # Generate test variants
        if config.generate_all_combinations:
            variants.extend(self._generate_all_combinations(base_template, config))
        else:
            variants.extend(self._generate_individual_variants(base_template, config))

        return variants

    def _create_variant(
        self,
        template: Dict[str, Any],
        variant_id: str,
        variant_name: str,
        variant_attributes: Dict[str, Any],
        is_control: bool = False,
    ) -> EmailVariant:
        """Create a single email variant."""
        return EmailVariant(
            variant_id=variant_id,
            variant_name=variant_name,
            subject=template.get("subject", ""),
            content=template.get("content", ""),
            variant_attributes=variant_attributes,
            is_control=is_control,
        )

    def _generate_individual_variants(
        self, base_template: Dict[str, Any], config: ABTestConfig
    ) -> List[EmailVariant]:
        """Generate individual variants for each variant element."""
        variants = []

        for element in config.variant_elements:
            for idx, variant_value in enumerate(element.variants):
                # Create a copy of the template
                variant_template = deepcopy(base_template)

                # Apply the variant
                self._apply_variant_to_template(
                    variant_template, element.path, variant_value
                )

                # Create variant metadata
                variant_id = f"{config.test_name}_{element.name}_v{idx + 1}"
                variant_name = f"{element.name} - Variant {idx + 1}"
                variant_attributes = {
                    element.name: variant_value,
                    "variant_type": element.element_type,
                }

                variant = self._create_variant(
                    variant_template,
                    variant_id=variant_id,
                    variant_name=variant_name,
                    variant_attributes=variant_attributes,
                )

                variants.append(variant)

        return variants

    def _generate_all_combinations(
        self, base_template: Dict[str, Any], config: ABTestConfig
    ) -> List[EmailVariant]:
        """Generate all possible combinations of variants."""
        variants = []

        # Get all variant values for each element
        element_variants = []
        element_names = []

        for element in config.variant_elements:
            element_variants.append(element.variants)
            element_names.append(element.name)

        # Generate all combinations
        for idx, combination in enumerate(itertools.product(*element_variants)):
            variant_template = deepcopy(base_template)
            variant_attributes = {}

            # Apply all variants in this combination
            for element, value in zip(config.variant_elements, combination):
                self._apply_variant_to_template(variant_template, element.path, value)
                variant_attributes[element.name] = value

            # Create variant
            variant_id = f"{config.test_name}_combo_v{idx + 1}"
            variant_name = f"Combination {idx + 1}"

            variant = self._create_variant(
                variant_template,
                variant_id=variant_id,
                variant_name=variant_name,
                variant_attributes=variant_attributes,
            )

            variants.append(variant)

        return variants

    def _apply_variant_to_template(
        self, template: Dict[str, Any], path: str, value: Any
    ) -> None:
        """Apply a variant value to the template at the specified path."""
        keys = path.split(".")
        current = template

        # Navigate to the parent of the target
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Set the value
        if keys:
            current[keys[-1]] = value

    def split_recipients(
        self, recipients: List[str], variants: List[EmailVariant]
    ) -> Dict[str, List[str]]:
        """
        Split recipients among variants for testing.

        Args:
            recipients: List of recipient email addresses
            variants: List of email variants

        Returns:
            Dictionary mapping variant IDs to recipient lists
        """
        assignments = {}
        total_recipients = len(recipients)

        # Calculate recipients per variant
        recipients_per_variant = total_recipients // len(variants)
        remainder = total_recipients % len(variants)

        start_idx = 0
        for idx, variant in enumerate(variants):
            # Add extra recipient to early variants to handle remainder
            count = recipients_per_variant + (1 if idx < remainder else 0)
            end_idx = start_idx + count

            assignments[variant.variant_id] = recipients[start_idx:end_idx]
            start_idx = end_idx

        return assignments
