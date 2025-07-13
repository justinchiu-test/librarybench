"""Plain text version generator from HTML templates."""

from typing import Optional
import html2text
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field


class PlainTextConfig(BaseModel):
    """Configuration for plain text generation."""

    body_width: int = Field(default=70, description="Maximum line width")
    ignore_links: bool = Field(default=False, description="Ignore links in output")
    ignore_images: bool = Field(default=False, description="Ignore images in output")
    ignore_emphasis: bool = Field(
        default=False, description="Ignore bold/italic formatting"
    )
    links_each_paragraph: bool = Field(
        default=False, description="Put links after each paragraph"
    )
    unicode_snob: bool = Field(
        default=False, description="Use unicode for special characters"
    )
    wrap_links: bool = Field(default=True, description="Wrap long URLs")
    pad_tables: bool = Field(default=True, description="Pad table cells for alignment")
    default_image_alt: str = Field(
        default="[Image]", description="Default alt text for images"
    )
    emphasis_mark: str = Field(default="*", description="Mark for emphasis")
    strong_mark: str = Field(default="**", description="Mark for strong emphasis")


class PlainTextGenerator:
    """Generates plain text versions of HTML emails."""

    def __init__(self, config: Optional[PlainTextConfig] = None) -> None:
        self.config = config or PlainTextConfig()
        self._setup_converter()

    def _setup_converter(self) -> None:
        """Setup html2text converter with configuration."""
        self.converter = html2text.HTML2Text()

        # Apply configuration
        self.converter.body_width = self.config.body_width
        self.converter.ignore_links = self.config.ignore_links
        self.converter.ignore_images = self.config.ignore_images
        self.converter.ignore_emphasis = self.config.ignore_emphasis
        self.converter.links_each_paragraph = self.config.links_each_paragraph
        self.converter.unicode_snob = self.config.unicode_snob
        self.converter.wrap_links = self.config.wrap_links
        self.converter.pad_tables = self.config.pad_tables
        self.converter.default_image_alt = self.config.default_image_alt
        self.converter.emphasis_mark = self.config.emphasis_mark
        self.converter.strong_mark = self.config.strong_mark

    def generate_plain_text(self, html: str, preprocess: bool = True) -> str:
        """
        Generate plain text version from HTML.

        Args:
            html: HTML content
            preprocess: Whether to preprocess HTML for better conversion

        Returns:
            Plain text version
        """
        if preprocess:
            html = self._preprocess_html(html)

        # Convert to plain text
        text = self.converter.handle(html)

        # Post-process the text
        text = self._postprocess_text(text)

        return text

    def _preprocess_html(self, html: str) -> str:
        """Preprocess HTML for better plain text conversion."""
        soup = BeautifulSoup(html, "html.parser")

        # Add spacing around block elements
        block_elements = ["div", "p", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote"]
        for tag_name in block_elements:
            for element in soup.find_all(tag_name):
                # Add newline before and after for better spacing
                if element.string:
                    element.insert_before("\n")
                    element.insert_after("\n")

        # Handle preheader text
        preheader = soup.find("div", {"class": "preheader"})
        if preheader:
            # Move preheader to top
            preheader.extract()
            if soup.body:
                soup.body.insert(0, preheader)
                soup.body.insert(1, soup.new_tag("hr"))

        # Improve table handling
        for table in soup.find_all("table"):
            # Add visual separator
            table.insert_before("\n")
            table.insert_after("\n")

        # Handle buttons/CTAs
        for link in soup.find_all("a", {"class": lambda x: x and "button" in x}):
            if link.string:
                # Make buttons more prominent
                link.string = f"[ {link.string.upper()} ]"

        return str(soup)

    def _postprocess_text(self, text: str) -> str:
        """Post-process generated plain text."""
        lines = text.split("\n")
        processed_lines = []

        # Remove excessive blank lines
        prev_blank = False
        for line in lines:
            is_blank = not line.strip()

            if is_blank and prev_blank:
                continue  # Skip multiple blank lines

            processed_lines.append(line)
            prev_blank = is_blank

        # Join and clean up
        text = "\n".join(processed_lines)

        # Ensure consistent line endings
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # Trim trailing whitespace from each line
        lines = [line.rstrip() for line in text.split("\n")]
        text = "\n".join(lines)

        # Ensure text ends with single newline
        text = text.rstrip() + "\n"

        return text

    def generate_with_header_footer(
        self, html: str, header: Optional[str] = None, footer: Optional[str] = None
    ) -> str:
        """
        Generate plain text with optional header and footer.

        Args:
            html: HTML content
            header: Optional header text
            footer: Optional footer text

        Returns:
            Plain text with header and footer
        """
        parts = []

        if header:
            parts.append(header)
            parts.append("=" * self.config.body_width)
            parts.append("")

        # Generate main content
        main_text = self.generate_plain_text(html)
        parts.append(main_text)

        if footer:
            parts.append("")
            parts.append("-" * self.config.body_width)
            parts.append(footer)

        return "\n".join(parts)

    def extract_links(self, html: str) -> list[tuple[str, str]]:
        """
        Extract all links from HTML for reference.

        Returns:
            List of (text, url) tuples
        """
        soup = BeautifulSoup(html, "html.parser")
        links = []

        for link in soup.find_all("a", href=True):
            text = link.get_text(strip=True)
            url = link["href"]
            links.append((text, url))

        return links

    def create_link_reference(self, links: list[tuple[str, str]]) -> str:
        """
        Create a formatted link reference section.

        Args:
            links: List of (text, url) tuples

        Returns:
            Formatted link reference
        """
        if not links:
            return ""

        reference = ["", "Links:", "-" * 40]

        for i, (text, url) in enumerate(links, 1):
            reference.append(f"[{i}] {text}")
            reference.append(f"    {url}")
            reference.append("")

        return "\n".join(reference)
