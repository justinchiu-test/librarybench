"""Tests for A/B testing functionality."""

from pytemplate.ab_testing import (
    ABTestGenerator,
    ABTestConfig,
    VariantElement,
    EmailVariant,
)


class TestABTestGenerator:
    """Test A/B test variant generation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = ABTestGenerator()

    def test_control_variant_creation(self):
        """Test that control variant is always created."""
        base_template = {
            "subject": "Original Subject",
            "content": "<p>Original content</p>",
        }

        config = ABTestConfig(test_name="test1", variant_elements=[])

        variants = self.generator.generate_variants(base_template, config)

        assert len(variants) == 1
        assert variants[0].is_control
        assert variants[0].variant_id == "test1_control"
        assert variants[0].subject == "Original Subject"

    def test_individual_variants(self):
        """Test individual variant generation."""
        base_template = {
            "subject": "Original Subject",
            "content": "<p>Original content</p>",
        }

        config = ABTestConfig(
            test_name="subject_test",
            variant_elements=[
                VariantElement(
                    name="subject_line",
                    path="subject",
                    variants=["New Subject A", "New Subject B"],
                    element_type="subject",
                )
            ],
        )

        variants = self.generator.generate_variants(base_template, config)

        assert len(variants) == 3  # Control + 2 variants
        assert variants[0].is_control
        assert variants[1].subject == "New Subject A"
        assert variants[2].subject == "New Subject B"
        assert variants[1].variant_attributes["subject_line"] == "New Subject A"

    def test_multiple_elements(self):
        """Test multiple variant elements."""
        base_template = {
            "subject": "Original Subject",
            "content": "<p>Original content</p>",
            "cta": {"text": "Click Here", "color": "blue"},
        }

        config = ABTestConfig(
            test_name="multi_test",
            variant_elements=[
                VariantElement(
                    name="subject", path="subject", variants=["Subject A", "Subject B"]
                ),
                VariantElement(
                    name="cta_color", path="cta.color", variants=["red", "green"]
                ),
            ],
        )

        variants = self.generator.generate_variants(base_template, config)

        assert len(variants) == 5  # Control + 2 + 2

        # Check individual variants
        cta_variants = [v for v in variants if "cta_color" in v.variant_attributes]
        assert len(cta_variants) == 2
        assert any(v.variant_attributes["cta_color"] == "red" for v in cta_variants)
        assert any(v.variant_attributes["cta_color"] == "green" for v in cta_variants)

    def test_all_combinations(self):
        """Test generation of all combinations."""
        base_template = {"subject": "Original", "content": "Original"}

        config = ABTestConfig(
            test_name="combo_test",
            variant_elements=[
                VariantElement(name="subject", path="subject", variants=["A", "B"]),
                VariantElement(name="content", path="content", variants=["X", "Y"]),
            ],
            generate_all_combinations=True,
        )

        variants = self.generator.generate_variants(base_template, config)

        # Control + 4 combinations (2x2)
        assert len(variants) == 5

        # Check all combinations exist
        combinations = [
            (v.variant_attributes.get("subject"), v.variant_attributes.get("content"))
            for v in variants
            if not v.is_control
        ]

        expected = [("A", "X"), ("A", "Y"), ("B", "X"), ("B", "Y")]
        assert sorted(combinations) == sorted(expected)

    def test_split_recipients(self):
        """Test recipient splitting among variants."""
        recipients = [f"user{i}@example.com" for i in range(100)]

        variants = [
            EmailVariant(
                variant_id=f"variant_{i}",
                variant_name=f"Variant {i}",
                subject="Test",
                content="Test",
                variant_attributes={},
            )
            for i in range(4)
        ]

        assignments = self.generator.split_recipients(recipients, variants)

        # Check all recipients are assigned
        total_assigned = sum(len(v) for v in assignments.values())
        assert total_assigned == 100

        # Check distribution is roughly even
        for variant in variants:
            assert 24 <= len(assignments[variant.variant_id]) <= 26

    def test_nested_path_application(self):
        """Test applying variants to nested paths."""
        base_template = {"meta": {"campaign": {"name": "Original Campaign"}}}

        config = ABTestConfig(
            test_name="nested_test",
            variant_elements=[
                VariantElement(
                    name="campaign_name",
                    path="meta.campaign.name",
                    variants=["New Campaign A", "New Campaign B"],
                )
            ],
        )

        variants = self.generator.generate_variants(base_template, config)

        assert len(variants) == 3
        assert variants[1].variant_attributes["campaign_name"] == "New Campaign A"
        # Verify the nested structure is preserved in variant
        # (actual verification would happen in template rendering)

    def test_empty_variants_list(self):
        """Test handling of empty variants list."""
        base_template = {"subject": "Test", "content": "Test"}

        config = ABTestConfig(
            test_name="empty_test",
            variant_elements=[
                VariantElement(name="subject", path="subject", variants=[])
            ],
        )

        variants = self.generator.generate_variants(base_template, config)

        # Should only have control
        assert len(variants) == 1
        assert variants[0].is_control

    def test_variant_metadata(self):
        """Test variant metadata is properly set."""
        base_template = {"subject": "Test", "content": "Test"}

        config = ABTestConfig(
            test_name="metadata_test",
            variant_elements=[
                VariantElement(
                    name="cta_button",
                    path="cta",
                    variants=["Buy Now", "Shop Today"],
                    element_type="cta",
                )
            ],
        )

        variants = self.generator.generate_variants(base_template, config)

        # Check non-control variants
        for variant in variants[1:]:
            assert variant.variant_id.startswith("metadata_test_")
            assert "cta_button" in variant.variant_attributes
            assert variant.variant_attributes.get("variant_type") == "cta"
