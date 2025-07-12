"""Tests for plain text generation."""

from pytemplate.text_generator import PlainTextGenerator, PlainTextConfig


class TestPlainTextGenerator:
    """Test plain text generation from HTML."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = PlainTextGenerator()

    def test_basic_html_conversion(self):
        """Test basic HTML to plain text conversion."""
        html = """
        <html>
        <body>
            <h1>Welcome</h1>
            <p>This is a test email.</p>
            <p>Thank you!</p>
        </body>
        </html>
        """

        result = self.generator.generate_plain_text(html)

        assert "Welcome" in result
        assert "This is a test email." in result
        assert "Thank you!" in result
        assert "<h1>" not in result
        assert "<p>" not in result

    def test_link_handling(self):
        """Test link conversion to plain text."""
        html = """
        <html>
        <body>
            <p>Visit our <a href="https://example.com">website</a> for more info.</p>
        </body>
        </html>
        """

        result = self.generator.generate_plain_text(html)

        assert "website" in result
        assert "https://example.com" in result

    def test_ignore_links_option(self):
        """Test ignoring links in output."""
        config = PlainTextConfig(ignore_links=True)
        generator = PlainTextGenerator(config)

        html = '<p>Click <a href="https://example.com">here</a></p>'

        result = generator.generate_plain_text(html)

        assert "here" in result
        assert "https://example.com" not in result

    def test_image_handling(self):
        """Test image alt text handling."""
        html = """
        <html>
        <body>
            <img src="logo.png" alt="Company Logo">
            <img src="banner.jpg">
        </body>
        </html>
        """

        result = self.generator.generate_plain_text(html)

        assert "Company Logo" in result
        assert "\\[Image\\]" in result  # Default for missing alt (escaped in markdown)

    def test_table_formatting(self):
        """Test table conversion to plain text."""
        html = """
        <html>
        <body>
            <table>
                <tr>
                    <td>Name</td>
                    <td>Price</td>
                </tr>
                <tr>
                    <td>Widget</td>
                    <td>$10.00</td>
                </tr>
            </table>
        </body>
        </html>
        """

        result = self.generator.generate_plain_text(html)

        assert "Name" in result
        assert "Price" in result
        assert "Widget" in result
        assert "$10.00" in result

    def test_list_formatting(self):
        """Test list conversion."""
        html = """
        <html>
        <body>
            <ul>
                <li>First item</li>
                <li>Second item</li>
            </ul>
            <ol>
                <li>Step one</li>
                <li>Step two</li>
            </ol>
        </body>
        </html>
        """

        result = self.generator.generate_plain_text(html)

        assert "First item" in result
        assert "Second item" in result
        assert "Step one" in result
        assert "Step two" in result

    def test_emphasis_formatting(self):
        """Test emphasis and strong text."""
        html = """
        <html>
        <body>
            <p>This is <em>emphasized</em> and <strong>strong</strong> text.</p>
        </body>
        </html>
        """

        result = self.generator.generate_plain_text(html)

        assert "*emphasized*" in result
        assert "**strong**" in result

    def test_custom_emphasis_marks(self):
        """Test custom emphasis marks."""
        config = PlainTextConfig(emphasis_mark="_", strong_mark="__")
        generator = PlainTextGenerator(config)

        html = "<p><em>emphasis</em> and <strong>strong</strong></p>"

        result = generator.generate_plain_text(html)

        assert "_emphasis_" in result
        assert "__strong__" in result

    def test_line_width_wrapping(self):
        """Test line width wrapping."""
        config = PlainTextConfig(body_width=40)
        generator = PlainTextGenerator(config)

        html = "<p>This is a very long line that should be wrapped at 40 characters to fit the specified width.</p>"

        result = generator.generate_plain_text(html)

        lines = result.strip().split("\n")
        for line in lines:
            if line.strip():  # Skip empty lines
                assert len(line) <= 40

    def test_preheader_handling(self):
        """Test preheader text handling."""
        html = """
        <html>
        <body>
            <div class="preheader">This is the preheader text</div>
            <h1>Main Content</h1>
            <p>Email body content.</p>
        </body>
        </html>
        """

        result = self.generator.generate_plain_text(html)

        # Preheader should appear at top
        lines = result.strip().split("\n")
        assert "This is the preheader text" in lines[0]

    def test_button_handling(self):
        """Test button/CTA formatting."""
        html = """
        <html>
        <body>
            <a href="#" class="button">Shop Now</a>
        </body>
        </html>
        """

        result = self.generator.generate_plain_text(html)

        assert "[ SHOP NOW ]" in result

    def test_header_footer_addition(self):
        """Test adding header and footer."""
        html = "<p>Main content</p>"
        header = "Company Newsletter"
        footer = "Unsubscribe at example.com/unsub"

        result = self.generator.generate_with_header_footer(html, header, footer)

        assert "Company Newsletter" in result
        assert "=" * 70 in result  # Header separator
        assert "Main content" in result
        assert "-" * 70 in result  # Footer separator
        assert "Unsubscribe" in result

    def test_extract_links(self):
        """Test link extraction."""
        html = """
        <html>
        <body>
            <a href="https://example.com">Homepage</a>
            <a href="https://example.com/products">Products</a>
            <a href="mailto:info@example.com">Contact</a>
        </body>
        </html>
        """

        links = self.generator.extract_links(html)

        assert len(links) == 3
        assert ("Homepage", "https://example.com") in links
        assert ("Products", "https://example.com/products") in links
        assert ("Contact", "mailto:info@example.com") in links

    def test_create_link_reference(self):
        """Test link reference creation."""
        links = [
            ("Homepage", "https://example.com"),
            ("Products", "https://example.com/products"),
        ]

        reference = self.generator.create_link_reference(links)

        assert "Links:" in reference
        assert "[1] Homepage" in reference
        assert "https://example.com" in reference
        assert "[2] Products" in reference
        assert "https://example.com/products" in reference

    def test_whitespace_cleanup(self):
        """Test whitespace and blank line cleanup."""
        html = """
        <html>
        <body>
            <p>First paragraph</p>
            
            
            
            <p>Second paragraph</p>
        </body>
        </html>
        """

        result = self.generator.generate_plain_text(html)

        # Should not have excessive blank lines
        assert "\n\n\n" not in result
        # Should end with single newline
        assert result.endswith("\n")
        assert not result.endswith("\n\n")
