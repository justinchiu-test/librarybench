"""Tests for personalization engine."""

import pytest
from pytemplate.personalization import PersonalizationEngine, PersonalizationConfig


class TestPersonalizationEngine:
    """Test personalization functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = PersonalizationEngine()

    def test_basic_token_replacement(self):
        """Test basic token replacement."""
        template = "Hello {{name}}, welcome to {{company}}!"
        data = {"name": "John Doe", "company": "Acme Corp"}

        result = self.engine.personalize(template, data)
        assert result == "Hello John Doe, welcome to Acme Corp!"

    def test_nested_data_access(self):
        """Test nested data access with dot notation."""
        template = "Hello {{user.name}}, your email is {{user.email}}"
        data = {"user": {"name": "Jane Smith", "email": "jane@example.com"}}

        result = self.engine.personalize(template, data)
        assert result == "Hello Jane Smith, your email is jane@example.com"

    def test_default_values(self):
        """Test default value handling."""
        template = "Hello {{name|default:Guest}}, your balance is {{balance|default:0}}"
        data = {"name": "John"}

        result = self.engine.personalize(template, data)
        assert result == "Hello John, your balance is 0"

    def test_missing_data_with_defaults(self):
        """Test missing data with default values."""
        template = (
            "Welcome {{name|default:Valued Customer}} to {{store|default:our store}}"
        )
        data = {}

        result = self.engine.personalize(template, data)
        assert result == "Welcome Valued Customer to our store"

    def test_html_escaping(self):
        """Test HTML escaping of personalized content."""
        template = "Message: {{message}}"
        data = {"message": "<script>alert('xss')</script>"}

        result = self.engine.personalize(template, data)
        assert "&lt;script&gt;" in result
        assert "<script>" not in result

    def test_html_escaping_disabled(self):
        """Test with HTML escaping disabled."""
        config = PersonalizationConfig(escape_html=False)
        engine = PersonalizationEngine(config)

        template = "Content: {{html_content}}"
        data = {"html_content": "<b>Bold text</b>"}

        result = engine.personalize(template, data)
        assert result == "Content: <b>Bold text</b>"

    def test_extract_tokens(self):
        """Test token extraction from template."""
        template = (
            "Hello {{name|default:Guest}}, you have {{count}} items in {{location}}"
        )

        tokens = self.engine.extract_tokens(template)

        assert "name" in tokens
        assert tokens["name"] == "Guest"
        assert "count" in tokens
        assert tokens["count"] is None
        assert "location" in tokens

    def test_validate_data(self):
        """Test data validation against template."""
        template = "{{name}} has {{credits|default:0}} credits"
        data = {"name": "John"}

        validation = self.engine.validate_data(template, data)

        assert validation["name"] is True
        assert validation["credits"] is True  # Has default

    def test_complex_nested_access(self):
        """Test complex nested data access."""
        template = (
            "Order {{order.id}} - {{order.items.0.name}} ({{order.items.0.quantity}})"
        )
        data = {
            "order": {
                "id": "12345",
                "items": [
                    {"name": "Widget", "quantity": 2},
                    {"name": "Gadget", "quantity": 1},
                ],
            }
        }

        result = self.engine.personalize(template, data)
        assert result == "Order 12345 - Widget (2)"

    def test_strict_mode(self):
        """Test strict mode raises errors on missing data."""
        config = PersonalizationConfig(strict_mode=True)
        engine = PersonalizationEngine(config)

        template = "Hello {{name}}"
        data = {}

        with pytest.raises(ValueError, match="Missing data for token 'name'"):
            engine.personalize(template, data)

    def test_whitespace_handling(self):
        """Test handling of whitespace in tokens."""
        template = "Hello {{ name }} and {{ friend | default: nobody }}"
        data = {"name": "Alice"}

        result = self.engine.personalize(template, data)
        assert result == "Hello Alice and nobody"

    def test_numeric_values(self):
        """Test handling of numeric values."""
        template = "You have {{count}} items worth ${{total}}"
        data = {"count": 5, "total": 99.99}

        result = self.engine.personalize(template, data)
        assert result == "You have 5 items worth $99.99"

    def test_boolean_values(self):
        """Test handling of boolean values."""
        template = "Premium user: {{is_premium}}"
        data = {"is_premium": True}

        result = self.engine.personalize(template, data)
        assert result == "Premium user: True"

    def test_none_values(self):
        """Test handling of None values."""
        template = "Status: {{status|default:Unknown}}"
        data = {"status": None}

        result = self.engine.personalize(template, data)
        assert result == "Status: Unknown"

    def test_list_indexing(self):
        """Test list indexing in personalization."""
        template = "First item: {{items.0}}, Second: {{items.1}}"
        data = {"items": ["apple", "banana", "cherry"]}

        result = self.engine.personalize(template, data)
        assert result == "First item: apple, Second: banana"

    def test_list_index_out_of_bounds(self):
        """Test list index out of bounds with default."""
        template = "Item: {{items.10|default:Not found}}"
        data = {"items": ["apple", "banana"]}

        result = self.engine.personalize(template, data)
        assert result == "Item: Not found"

    def test_empty_token(self):
        """Test handling of empty tokens."""
        template = "Hello {{}} world"
        data = {"name": "John"}

        # Empty token should remain unchanged
        result = self.engine.personalize(template, data)
        assert result == "Hello {{}} world"
