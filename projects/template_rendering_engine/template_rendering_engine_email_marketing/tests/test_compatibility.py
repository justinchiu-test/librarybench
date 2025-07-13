"""Tests for email client compatibility validation."""

from pytemplate.compatibility import EmailClientValidator


class TestEmailClientValidator:
    """Test email client compatibility validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = EmailClientValidator()

    def test_outlook_unsupported_elements(self):
        """Test detection of Outlook unsupported elements."""
        html = """
        <html>
        <body>
            <video src="video.mp4"></video>
            <svg width="100" height="100"></svg>
            <form action="/submit">
                <input type="text">
            </form>
        </body>
        </html>
        """

        issues = self.validator.validate(html, target_clients=["outlook"])

        element_issues = [i for i in issues if i.element in ["video", "svg", "form"]]
        assert len(element_issues) == 3
        assert all(i.severity == "error" for i in element_issues)
        assert all(i.client == "Outlook" for i in element_issues)

    def test_outlook_unsupported_css(self):
        """Test detection of Outlook unsupported CSS."""
        html = """
        <html>
        <body>
            <div style="position: absolute; float: left;">Content</div>
            <p style="display: flex; transform: rotate(45deg);">Text</p>
        </body>
        </html>
        """

        issues = self.validator.validate(html, target_clients=["outlook"])

        css_issues = [i for i in issues if "CSS:" in i.element]
        assert len(css_issues) >= 4
        assert any("position" in i.element for i in css_issues)
        assert any("float" in i.element for i in css_issues)
        assert any("flex" in i.element for i in css_issues)
        assert any("transform" in i.element for i in css_issues)

    def test_gmail_style_tag_warning(self):
        """Test Gmail style tag warning."""
        html = """
        <html>
        <head>
            <style>
                p { color: red; }
            </style>
        </head>
        <body>
            <p>Test</p>
        </body>
        </html>
        """

        issues = self.validator.validate(html, target_clients=["gmail"])

        style_issues = [i for i in issues if i.element == "style"]
        assert len(style_issues) == 1
        assert style_issues[0].severity == "warning"
        assert "stripped" in style_issues[0].description.lower()

    def test_width_recommendations(self):
        """Test table width recommendations."""
        html = """
        <html>
        <body>
            <table width="800">
                <tr><td>Wide table</td></tr>
            </table>
            <table width="500">
                <tr><td>Normal table</td></tr>
            </table>
        </body>
        </html>
        """

        issues = self.validator.validate(html, target_clients=["outlook"])

        width_issues = [i for i in issues if "width" in i.description.lower()]
        assert len(width_issues) == 1
        assert "800px exceeds recommended 600px" in width_issues[0].description

    def test_general_best_practices(self):
        """Test general email best practices validation."""
        html = """
        <html>
        <body>
            <script>alert('test');</script>
            <link rel="stylesheet" href="styles.css">
            <img src="image.jpg">
        </body>
        </html>
        """

        issues = self.validator.validate(html)

        # Filter for general practice issues only
        general_issues = [i for i in issues if i.client == "General"]

        # JavaScript not supported
        script_issues = [i for i in general_issues if i.element == "script"]
        assert len(script_issues) == 1
        assert script_issues[0].severity == "error"

        # External stylesheets not supported
        link_issues = [i for i in general_issues if i.element == "link"]
        assert len(link_issues) == 1
        assert link_issues[0].severity == "error"

        # Missing alt text
        img_issues = [
            i for i in general_issues if i.element == "img" and "alt" in i.description
        ]
        assert len(img_issues) == 1
        assert img_issues[0].severity == "warning"

    def test_missing_doctype(self):
        """Test missing DOCTYPE warning."""
        html = """
        <html>
        <body>
            <p>No doctype</p>
        </body>
        </html>
        """

        issues = self.validator.validate(html)

        doctype_issues = [i for i in issues if i.element == "DOCTYPE"]
        assert len(doctype_issues) == 1
        assert doctype_issues[0].severity == "warning"

    def test_partial_css_support(self):
        """Test detection of partially supported CSS."""
        html = """
        <html>
        <body>
            <div style="margin: 10px; padding: 20px;">
                Content with margin and padding
            </div>
        </body>
        </html>
        """

        issues = self.validator.validate(html, target_clients=["outlook"])

        partial_issues = [
            i for i in issues if i.severity == "warning" and "CSS:" in i.element
        ]
        assert any("margin" in i.element for i in partial_issues)
        assert any("padding" in i.element for i in partial_issues)

    def test_get_supported_css(self):
        """Test getting supported CSS for a client."""
        outlook_css = self.validator.get_supported_css("outlook")

        assert "background-color" in outlook_css
        assert "color" in outlook_css
        assert "font-size" in outlook_css
        assert "position" not in outlook_css
        assert "float" not in outlook_css

    def test_multiple_clients(self):
        """Test validation against multiple clients."""
        html = """
        <html>
        <head>
            <style>p { color: red; }</style>
        </head>
        <body>
            <div style="position: relative;">
                <video src="test.mp4"></video>
            </div>
        </body>
        </html>
        """

        issues = self.validator.validate(html, target_clients=["outlook", "gmail"])

        # Should have issues from both clients
        outlook_issues = [i for i in issues if i.client == "Outlook"]
        gmail_issues = [i for i in issues if i.client == "Gmail"]

        assert len(outlook_issues) > 0
        assert len(gmail_issues) > 0

    def test_unknown_client(self):
        """Test handling of unknown client."""
        html = "<p>Test</p>"

        # Should not raise error, just skip unknown client
        issues = self.validator.validate(html, target_clients=["unknown_client"])

        # Should still get general validation
        assert isinstance(issues, list)
