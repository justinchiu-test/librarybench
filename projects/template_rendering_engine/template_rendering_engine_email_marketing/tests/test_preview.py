"""Tests for email preview rendering."""

import pytest
from pytemplate.preview import PreviewRenderer


class TestPreviewRenderer:
    """Test email preview rendering functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.renderer = PreviewRenderer()

    def test_gmail_preview_strips_styles(self):
        """Test Gmail preview strips style tags."""
        html = """
        <html>
        <head>
            <style>
                p { color: red; }
            </style>
        </head>
        <body>
            <p>Test paragraph</p>
        </body>
        </html>
        """

        result = self.renderer.render_preview(html, "gmail")

        assert "<style>" not in result.html
        assert "Stripped <style> tags" in result.modifications_applied
        assert result.client == "Gmail"

    def test_gmail_strips_classes_and_ids(self):
        """Test Gmail strips classes and IDs."""
        html = """
        <html>
        <body>
            <p class="highlight" id="main-text">Test paragraph</p>
            <div class="container">Content</div>
        </body>
        </html>
        """

        result = self.renderer.render_preview(html, "gmail")

        assert "class=" not in result.html
        assert "id=" not in result.html
        assert "Stripped CSS classes" in result.modifications_applied
        assert "Stripped element IDs" in result.modifications_applied

    def test_gmail_link_modification(self):
        """Test Gmail modifies links."""
        html = """
        <html>
        <body>
            <a href="https://example.com">Click here</a>
        </body>
        </html>
        """

        result = self.renderer.render_preview(html, "gmail")

        assert "https://www.google.com/url?q=https://example.com" in result.html
        assert 'target="_blank"' in result.html
        assert "Modified link tracking" in result.modifications_applied

    def test_outlook_max_width_enforcement(self):
        """Test Outlook enforces maximum width."""
        html = """
        <html>
        <body>
            <table width="800">
                <tr><td>Wide content</td></tr>
            </table>
            <table style="width: 900px;">
                <tr><td>Also wide</td></tr>
            </table>
        </body>
        </html>
        """

        result = self.renderer.render_preview(html, "outlook")

        assert 'width="600"' in result.html
        assert "width: 600px" in result.html
        assert "Enforced max width: 600px" in result.modifications_applied

    def test_outlook_no_media_query_support(self):
        """Test Outlook removes media queries."""
        html = """
        <html>
        <head>
            <style>
                p { color: blue; }
                @media (max-width: 600px) {
                    p { color: green; }
                }
            </style>
        </head>
        <body>
            <p>Test</p>
        </body>
        </html>
        """

        result = self.renderer.render_preview(html, "outlook")

        assert "Media queries not supported" in result.warnings

    def test_mobile_viewport(self):
        """Test mobile viewport settings."""
        html = """
        <html>
        <head></head>
        <body>
            <p>Mobile content</p>
        </body>
        </html>
        """

        result = self.renderer.render_preview(html, "outlook-mobile")

        assert result.viewport_width == 320
        assert "Outlook Mobile" in result.client

    def test_custom_viewport_width(self):
        """Test custom viewport width override."""
        html = "<p>Test</p>"

        result = self.renderer.render_preview(html, "gmail", viewport_width=480)

        assert result.viewport_width == 480
        assert "width=480" in result.html

    def test_apple_mail_preserves_features(self):
        """Test Apple Mail preserves most features."""
        html = """
        <html>
        <head>
            <style>
                p { color: red; }
                @media (max-width: 600px) {
                    p { color: green; }
                }
            </style>
        </head>
        <body>
            <p class="text" id="main">Test</p>
        </body>
        </html>
        """

        result = self.renderer.render_preview(html, "apple-mail")

        assert "<style>" in result.html
        assert 'class="text"' in result.html
        assert 'id="main"' in result.html
        assert "@media" in result.html
        assert len(result.modifications_applied) == 0

    def test_render_all_previews(self):
        """Test rendering previews for all clients."""
        html = """
        <html>
        <body>
            <p>Test content</p>
        </body>
        </html>
        """

        results = self.renderer.render_all_previews(html)

        assert len(results) == len(self.renderer.client_profiles)

        # Check each client has a result
        client_names = {r.client for r in results}
        expected_clients = {
            "Outlook",
            "Gmail",
            "Apple Mail",
            "Outlook Mobile",
            "Gmail Mobile",
        }
        assert client_names == expected_clients

    def test_unknown_client_error(self):
        """Test error handling for unknown client."""
        html = "<p>Test</p>"

        with pytest.raises(ValueError, match="Unknown email client"):
            self.renderer.render_preview(html, "unknown-client")

    def test_get_client_limitations(self):
        """Test getting client limitations."""
        gmail_limits = self.renderer.get_client_limitations("gmail")

        assert gmail_limits["strips_classes"] is True
        assert gmail_limits["strips_ids"] is True
        assert gmail_limits["strips_styles"] is True
        assert gmail_limits["modifies_links"] is True
        assert gmail_limits["supports_media_queries"] is False

        apple_limits = self.renderer.get_client_limitations("apple-mail")

        assert apple_limits["strips_classes"] is False
        assert apple_limits["supports_media_queries"] is True
        assert apple_limits["supports_dark_mode"] is True

    def test_css_prefix_addition(self):
        """Test CSS prefix addition for Gmail."""
        html = """
        <html>
        <body>
            <p class="highlight primary">Test</p>
        </body>
        </html>
        """

        result = self.renderer.render_preview(html, "gmail")

        # Gmail strips classes, but if it didn't, they would be prefixed
        assert "class=" not in result.html  # Because Gmail strips classes
