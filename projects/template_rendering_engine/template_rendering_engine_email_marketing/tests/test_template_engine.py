"""Tests for the main template engine."""

import time
from pytemplate.template_engine import (
    TemplateEngine,
    EmailTemplate,
    RenderConfig,
)
from pytemplate.ab_testing import ABTestConfig, VariantElement
from pytemplate.link_tracking import UTMParams


class TestTemplateEngine:
    """Test the main template engine functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = TemplateEngine()

    def test_basic_email_rendering(self):
        """Test basic email rendering with personalization."""
        template = EmailTemplate(
            subject="Hello {{name}}!",
            content="""
            <html>
            <head>
                <style>
                    p { color: blue; }
                </style>
            </head>
            <body>
                <p>Welcome {{name}}, thanks for joining {{company}}!</p>
            </body>
            </html>
            """,
        )

        recipient_data = {"name": "John Doe", "company": "Acme Corp"}

        result = self.engine.render_email(template, recipient_data)

        assert result.subject == "Hello John Doe!"
        assert "Welcome John Doe" in result.html
        assert "thanks for joining Acme Corp" in result.html
        assert 'style="color: blue"' in result.html  # CSS should be inlined
        assert result.plain_text is not None
        assert "Welcome John Doe" in result.plain_text

    def test_render_with_utm_tracking(self):
        """Test rendering with UTM link tracking."""
        template = EmailTemplate(
            subject="Check out our sale",
            content="""
            <html>
            <body>
                <a href="https://example.com/products">Shop Now</a>
                <a href="https://example.com/deals">View Deals</a>
            </body>
            </html>
            """,
        )

        utm_params = UTMParams(
            utm_source="email", utm_medium="newsletter", utm_campaign="summer_sale"
        )

        result = self.engine.render_email(template, {}, utm_params=utm_params)

        assert "utm_source=email" in result.html
        assert "utm_medium=newsletter" in result.html
        assert "utm_campaign=summer_sale" in result.html
        assert len(result.tracked_links) == 2

    def test_render_with_preheader(self):
        """Test rendering with preheader text."""
        template = EmailTemplate(
            subject="Newsletter",
            content="<html><body><p>Main content</p></body></html>",
            preheader="Don't miss our special offers {{name|default:}}",
        )

        result = self.engine.render_email(template, {"name": "Alice"})

        assert '<div class="preheader"' in result.html
        assert "Don't miss our special offers Alice" in result.html
        assert "display: none" in result.html

    def test_compatibility_validation(self):
        """Test email compatibility validation."""
        template = EmailTemplate(
            subject="Test",
            content="""
            <html>
            <body>
                <video src="video.mp4"></video>
                <div style="position: absolute;">Content</div>
                <script>alert('test');</script>
            </body>
            </html>
            """,
        )

        config = RenderConfig(
            validate_compatibility=True, target_clients=["outlook", "gmail"]
        )

        result = self.engine.render_email(template, {}, config=config)

        assert len(result.compatibility_issues) > 0

        # Check for specific issues
        issues_text = str([i.description for i in result.compatibility_issues])
        assert "video" in issues_text.lower()
        assert "position" in issues_text.lower()
        assert "script" in issues_text.lower()

    def test_bulk_rendering(self):
        """Test bulk email rendering."""
        template = EmailTemplate(
            subject="Hello {{name}}", content="<p>Welcome {{name}} from {{city}}</p>"
        )

        recipients_data = [
            {"name": "Alice", "city": "New York"},
            {"name": "Bob", "city": "London"},
            {"name": "Charlie", "city": "Tokyo"},
        ]

        results = self.engine.render_bulk(template, recipients_data)

        assert len(results) == 3
        assert results[0].subject == "Hello Alice"
        assert "Welcome Alice from New York" in results[0].html
        assert results[1].subject == "Hello Bob"
        assert "Welcome Bob from London" in results[1].html
        assert results[2].subject == "Hello Charlie"
        assert "Welcome Charlie from Tokyo" in results[2].html

    def test_ab_test_rendering(self):
        """Test A/B test variant rendering."""
        base_template = {
            "subject": "Original Subject",
            "content": "<p>Original content with {{name}}</p>",
        }

        ab_config = ABTestConfig(
            test_name="subject_test",
            variant_elements=[
                VariantElement(
                    name="subject_line",
                    path="subject",
                    variants=["New Subject A", "New Subject B"],
                )
            ],
        )

        recipient_data = {"name": "Test User"}

        results = self.engine.render_ab_test(base_template, ab_config, recipient_data)

        assert len(results) == 3  # Control + 2 variants

        # Check control
        assert results[0].variant_id == "subject_test_control"
        assert results[0].subject == "Original Subject"

        # Check variants
        assert results[1].subject == "New Subject A"
        assert results[2].subject == "New Subject B"

        # Check personalization works in all variants
        for result in results:
            assert "Test User" in result.html

    def test_preview_generation(self):
        """Test preview generation for different clients."""
        template = EmailTemplate(
            subject="Preview Test",
            content="""
            <html>
            <head>
                <style>p { color: red; }</style>
            </head>
            <body>
                <p class="text">Hello {{name}}</p>
            </body>
            </html>
            """,
        )

        sample_data = {"name": "Preview User"}

        previews = self.engine.generate_previews(
            template, sample_data, clients=["gmail", "outlook"]
        )

        assert len(previews) == 2

        # Gmail preview should strip styles and classes
        gmail_preview = next(p for p in previews if p.client == "Gmail")
        assert "<style>" not in gmail_preview.html
        assert "class=" not in gmail_preview.html

        # Outlook preview should preserve most features
        outlook_preview = next(p for p in previews if p.client == "Outlook")
        assert "Hello Preview User" in outlook_preview.html

    def test_template_validation(self):
        """Test template validation."""
        template = EmailTemplate(
            subject="Order {{order.id}} - {{order.status|default:pending}}",
            content="""
            <p>Hi {{customer.name}},</p>
            <p>Your order total is ${{order.total|default:0}}</p>
            <p>Shipping to: {{shipping.address}}</p>
            """,
        )

        sample_data = {
            "customer": {"name": "John"},
            "order": {"id": "12345", "total": 99.99},
            # Note: missing shipping.address
        }

        validation = self.engine.validate_template(template, sample_data)

        # Check token extraction
        assert "order.id" in validation["tokens"]["subject"]
        assert "customer.name" in validation["tokens"]["content"]
        assert "shipping.address" in validation["tokens"]["content"]

        # Check validation results
        assert validation["validation"]["subject"]["order.id"] is True
        assert (
            validation["validation"]["subject"]["order.status"] is True
        )  # Has default
        assert validation["validation"]["content"]["customer.name"] is True
        assert validation["validation"]["content"]["shipping.address"] is False

        # Should render successfully despite missing data (due to defaults)
        assert validation["render_test"]["success"] is True

    def test_render_config_options(self):
        """Test various render configuration options."""
        template = EmailTemplate(
            subject="Test",
            content="""
            <html>
            <head>
                <style>
                    p { color: red; }
                    @media (max-width: 600px) {
                        p { color: blue; }
                    }
                </style>
            </head>
            <body>
                <p>Test content</p>
                <a href="https://example.com">Link</a>
            </body>
            </html>
            """,
        )

        # Test with CSS inlining disabled
        config1 = RenderConfig(inline_css=False)
        result1 = self.engine.render_email(template, {}, config=config1)
        assert "<style>" in result1.html

        # Test with link tracking disabled
        config2 = RenderConfig(track_links=False)
        result2 = self.engine.render_email(template, {}, config=config2)
        assert "utm_" not in result2.html
        assert len(result2.tracked_links) == 0

        # Test with plain text disabled
        config3 = RenderConfig(generate_plain_text=False)
        result3 = self.engine.render_email(template, {}, config=config3)
        assert result3.plain_text is None

        # Test with media query preservation disabled
        config4 = RenderConfig(preserve_media_queries=False)
        result4 = self.engine.render_email(template, {}, config=config4)
        assert "@media" not in result4.html

    def test_render_performance(self):
        """Test rendering performance meets requirements."""
        template = EmailTemplate(
            subject="Hello {{name}}",
            content="""
            <html>
            <head>
                <style>
                    body { font-family: Arial; }
                    p { color: #333; margin: 10px 0; }
                </style>
            </head>
            <body>
                <h1>Welcome {{name}}!</h1>
                <p>Thank you for joining {{company}}.</p>
                <p>Your account type is: {{account.type|default:basic}}</p>
                <a href="https://example.com/activate">Activate Account</a>
            </body>
            </html>
            """,
        )

        # Generate data for 10,000 recipients
        recipients_data = [
            {
                "name": f"User {i}",
                "company": "Test Corp",
                "account": {"type": "premium" if i % 2 == 0 else "basic"},
            }
            for i in range(10000)
        ]

        start_time = time.time()
        results = self.engine.render_bulk(template, recipients_data)
        end_time = time.time()

        # Should process 10,000 emails in under 60 seconds
        processing_time = end_time - start_time
        assert processing_time < 60
        assert len(results) == 10000

        # Verify first and last results
        assert results[0].subject == "Hello User 0"
        assert "premium" in results[0].html
        assert results[-1].subject == "Hello User 9999"
        assert "basic" in results[-1].html

    def test_error_handling_invalid_html(self):
        """Test handling of invalid HTML in template."""
        template = EmailTemplate(
            subject="Test",
            content="<p>Unclosed paragraph <div>Nested",  # Invalid HTML
        )
        
        recipient_data = {"name": "Test User"}
        
        # Should still process without throwing error
        result = self.engine.render_email(template, recipient_data)
        assert result.subject == "Test"
        assert result.html  # Should have some output

    def test_empty_recipient_data(self):
        """Test rendering with empty recipient data."""
        template = EmailTemplate(
            subject="Hello {{name|default:Guest}}",
            content="<p>Welcome {{name|default:Guest}}!</p>",
        )
        
        result = self.engine.render_email(template, {})
        assert result.subject == "Hello Guest"
        assert "Welcome Guest!" in result.html

    def test_large_css_processing(self):
        """Test processing of large CSS content."""
        # Generate large CSS with many rules
        css_rules = []
        for i in range(100):
            css_rules.append(f".class{i} {{ color: #{i:06x}; font-size: {i}px; }}")
        
        template = EmailTemplate(
            subject="Test",
            content='<style>' + "\n".join(css_rules) + '</style><p class="class50">Test</p>',
        )
        
        result = self.engine.render_email(template, {})
        assert 'color: #000032' in result.html  # class50 color
        assert 'font-size: 50px' in result.html

    def test_complex_personalization_with_tracking(self):
        """Test complex personalization with link tracking."""
        template = EmailTemplate(
            subject="{{user.name}}, check out {{product.name}}!",
            content="""
            <p>Hi {{user.name|default:Friend}},</p>
            <p>We think you'll love {{product.name}} at {{product.price}}!</p>
            <a href="https://shop.example.com/product/{{product.id}}">Buy Now</a>
            <p>Your account status: {{user.account.status|default:Active}}</p>
            """,
        )
        
        recipient_data = {
            "user": {
                "name": "Alice",
                "account": {"status": "Premium"}
            },
            "product": {
                "id": "12345",
                "name": "Widget Pro",
                "price": "$99.99"
            }
        }
        
        utm_params = UTMParams(
            utm_source="email",
            utm_medium="promo",
            utm_campaign="widget_launch"
        )
        
        result = self.engine.render_email(template, recipient_data, utm_params=utm_params)
        
        # Check personalization
        assert result.subject == "Alice, check out Widget Pro!"
        assert "Hi Alice," in result.html
        assert "Widget Pro at $99.99" in result.html
        assert "Your account status: Premium" in result.html
        
        # Check link tracking
        assert "utm_source=email" in result.html
        assert "utm_medium=promo" in result.html
        assert "utm_campaign=widget_launch" in result.html
        assert "product/12345" in result.html
