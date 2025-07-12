"""Tests for CSS inliner functionality."""

from pytemplate.css_inliner import CSSInliner
from bs4 import BeautifulSoup


class TestCSSInliner:
    """Test CSS inlining functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.inliner = CSSInliner()

    def test_basic_inline_conversion(self):
        """Test basic CSS to inline style conversion."""
        html = """
        <html>
        <head>
            <style>
                p { color: red; font-size: 16px; }
                .highlight { background-color: yellow; }
            </style>
        </head>
        <body>
            <p>Test paragraph</p>
            <p class="highlight">Highlighted paragraph</p>
        </body>
        </html>
        """

        result = self.inliner.inline_css(html, preserve_media_queries=False)

        assert 'style="color: red; font-size: 16px"' in result
        assert 'style="color: red; font-size: 16px; background-color: yellow"' in result
        assert "<style>" not in result

    def test_preserve_media_queries(self):
        """Test preservation of media queries."""
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
            <p>Responsive paragraph</p>
        </body>
        </html>
        """

        result = self.inliner.inline_css(html, preserve_media_queries=True)

        assert 'style="color: blue"' in result
        assert "@media (max-width: 600px)" in result
        assert "<style>" in result

    def test_specificity_ordering(self):
        """Test CSS specificity is respected."""
        html = """
        <html>
        <head>
            <style>
                p { color: red; }
                .blue { color: blue; }
                #special { color: green; }
            </style>
        </head>
        <body>
            <p>Normal paragraph</p>
            <p class="blue">Blue paragraph</p>
            <p id="special" class="blue">Special paragraph</p>
        </body>
        </html>
        """

        result = self.inliner.inline_css(html)

        assert '<p style="color: red">Normal paragraph</p>' in result
        assert '<p class="blue" style="color: blue">Blue paragraph</p>' in result
        assert (
            '<p class="blue" id="special" style="color: green">Special paragraph</p>'
            in result
        )

    def test_existing_inline_styles(self):
        """Test merging with existing inline styles."""
        html = """
        <html>
        <head>
            <style>
                p { color: red; }
            </style>
        </head>
        <body>
            <p style="font-weight: bold;">Bold paragraph</p>
        </body>
        </html>
        """

        result = self.inliner.inline_css(html)

        assert "font-weight: bold" in result
        assert "color: red" in result

    def test_complex_selectors(self):
        """Test handling of complex CSS selectors."""
        html = """
        <html>
        <head>
            <style>
                table td { padding: 10px; }
                .container > p { margin: 20px; }
                a:hover { color: red; }
            </style>
        </head>
        <body>
            <table>
                <tr>
                    <td>Cell content</td>
                </tr>
            </table>
            <div class="container">
                <p>Container paragraph</p>
            </div>
            <a href="#">Link</a>
        </body>
        </html>
        """

        result = self.inliner.inline_css(html)

        assert 'style="padding: 10px"' in result
        assert 'style="margin: 20px"' in result

    def test_invalid_css_handling(self):
        """Test handling of invalid CSS."""
        html = """
        <html>
        <head>
            <style>
                p { color: red;; invalid-property: value; }
                .broken { }
            </style>
        </head>
        <body>
            <p>Test paragraph</p>
        </body>
        </html>
        """

        # Should not raise exception
        result = self.inliner.inline_css(html)
        assert "<p" in result

    def test_empty_html(self):
        """Test handling of empty HTML."""
        result = self.inliner.inline_css("")
        assert result == ""

    def test_no_style_tags(self):
        """Test HTML without style tags."""
        html = "<p>No styles here</p>"
        result = self.inliner.inline_css(html)
        assert result == "<p>No styles here</p>"

    def test_multiple_style_tags(self):
        """Test handling of multiple style tags."""
        html = """
        <html>
        <head>
            <style>p { color: red; }</style>
            <style>p { font-size: 14px; }</style>
        </head>
        <body><p>Text</p></body>
        </html>
        """
        
        result = self.inliner.inline_css(html)
        soup = BeautifulSoup(result, "html.parser")
        p_tag = soup.find("p")
        assert "color: red" in p_tag.get("style", "")
        assert "font-size: 14px" in p_tag.get("style", "")

    def test_pseudo_selector_handling(self):
        """Test that pseudo selectors are ignored."""
        html = """
        <style>
        a:hover { color: blue; }
        a { color: red; }
        </style>
        <a href="#">Link</a>
        """
        
        result = self.inliner.inline_css(html)
        soup = BeautifulSoup(result, "html.parser")
        a_tag = soup.find("a")
        # Only non-pseudo selector should be applied
        assert a_tag.get("style") == "color: red"
