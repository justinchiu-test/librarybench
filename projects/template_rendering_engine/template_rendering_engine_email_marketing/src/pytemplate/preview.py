"""Preview renderer for multiple email clients."""

from typing import Dict, List, Optional
from bs4 import BeautifulSoup, Tag
from pydantic import BaseModel, Field
import re


class EmailClientProfile(BaseModel):
    """Profile defining how an email client renders HTML."""

    name: str = Field(description="Email client name")
    viewport_width: int = Field(default=600, description="Default viewport width")
    strips_classes: bool = Field(
        default=False, description="Whether client strips CSS classes"
    )
    strips_ids: bool = Field(
        default=False, description="Whether client strips element IDs"
    )
    strips_styles: bool = Field(
        default=False, description="Whether client strips style tags"
    )
    modifies_links: bool = Field(
        default=False, description="Whether client modifies links"
    )
    supports_media_queries: bool = Field(
        default=True, description="Media query support"
    )
    css_prefix: Optional[str] = Field(
        default=None, description="CSS prefix added by client"
    )
    max_width_enforced: Optional[int] = Field(
        default=None, description="Maximum width enforced"
    )
    dark_mode_support: bool = Field(default=False, description="Dark mode support")


class PreviewResult(BaseModel):
    """Result of email preview rendering."""

    client: str = Field(description="Email client name")
    html: str = Field(description="Rendered HTML preview")
    warnings: List[str] = Field(default_factory=list, description="Rendering warnings")
    viewport_width: int = Field(description="Viewport width used")
    modifications_applied: List[str] = Field(
        default_factory=list, description="Modifications applied"
    )


class PreviewRenderer:
    """Renders email previews simulating different email clients."""

    def __init__(self) -> None:
        self.client_profiles = self._initialize_client_profiles()

    def _initialize_client_profiles(self) -> Dict[str, EmailClientProfile]:
        """Initialize email client rendering profiles."""
        return {
            "outlook": EmailClientProfile(
                name="Outlook",
                viewport_width=600,
                strips_classes=False,
                strips_ids=False,
                strips_styles=False,
                modifies_links=False,
                supports_media_queries=False,
                max_width_enforced=600,
                dark_mode_support=False,
            ),
            "gmail": EmailClientProfile(
                name="Gmail",
                viewport_width=600,
                strips_classes=True,
                strips_ids=True,
                strips_styles=True,
                modifies_links=True,
                supports_media_queries=False,
                css_prefix="gmail",
                dark_mode_support=False,
            ),
            "apple-mail": EmailClientProfile(
                name="Apple Mail",
                viewport_width=600,
                strips_classes=False,
                strips_ids=False,
                strips_styles=False,
                modifies_links=False,
                supports_media_queries=True,
                dark_mode_support=True,
            ),
            "outlook-mobile": EmailClientProfile(
                name="Outlook Mobile",
                viewport_width=320,
                strips_classes=False,
                strips_ids=False,
                strips_styles=False,
                modifies_links=False,
                supports_media_queries=True,
                max_width_enforced=320,
                dark_mode_support=True,
            ),
            "gmail-mobile": EmailClientProfile(
                name="Gmail Mobile",
                viewport_width=320,
                strips_classes=True,
                strips_ids=True,
                strips_styles=True,
                modifies_links=True,
                supports_media_queries=False,
                css_prefix="gmail",
                dark_mode_support=False,
            ),
        }

    def render_preview(
        self, html: str, client: str, viewport_width: Optional[int] = None
    ) -> PreviewResult:
        """
        Render email preview for specific client.

        Args:
            html: Email HTML content
            client: Email client name
            viewport_width: Override viewport width

        Returns:
            Preview result with rendered HTML and metadata
        """
        if client not in self.client_profiles:
            raise ValueError(f"Unknown email client: {client}")

        profile = self.client_profiles[client]
        soup = BeautifulSoup(html, "html.parser")

        warnings = []
        modifications = []

        # Apply client-specific modifications
        if profile.strips_styles:
            self._strip_style_tags(soup)
            modifications.append("Stripped <style> tags")

        if profile.strips_classes:
            self._strip_classes(soup)
            modifications.append("Stripped CSS classes")

        if profile.strips_ids:
            self._strip_ids(soup)
            modifications.append("Stripped element IDs")

        if profile.modifies_links:
            self._modify_links(soup, profile)
            modifications.append("Modified link tracking")

        if profile.css_prefix:
            self._add_css_prefix(soup, profile.css_prefix)
            modifications.append(f"Added {profile.css_prefix} CSS prefix")

        if not profile.supports_media_queries:
            self._remove_media_queries(soup)
            warnings.append("Media queries not supported")

        if profile.max_width_enforced:
            self._enforce_max_width(soup, profile.max_width_enforced)
            modifications.append(f"Enforced max width: {profile.max_width_enforced}px")

        # Set viewport width
        used_viewport = viewport_width or profile.viewport_width
        self._apply_viewport_styles(soup, used_viewport)

        return PreviewResult(
            client=profile.name,
            html=str(soup),
            warnings=warnings,
            viewport_width=used_viewport,
            modifications_applied=modifications,
        )

    def render_all_previews(self, html: str) -> List[PreviewResult]:
        """Render previews for all supported clients."""
        results = []

        for client_name in self.client_profiles:
            result = self.render_preview(html, client_name)
            results.append(result)

        return results

    def _strip_style_tags(self, soup: BeautifulSoup) -> None:
        """Remove all style tags."""
        for style in soup.find_all("style"):
            style.decompose()

    def _strip_classes(self, soup: BeautifulSoup) -> None:
        """Remove all CSS classes."""
        for element in soup.find_all(class_=True):
            if isinstance(element, Tag):
                del element["class"]

    def _strip_ids(self, soup: BeautifulSoup) -> None:
        """Remove all element IDs."""
        for element in soup.find_all(id=True):
            if isinstance(element, Tag):
                del element["id"]

    def _modify_links(self, soup: BeautifulSoup, profile: EmailClientProfile) -> None:
        """Simulate link modification by email client."""
        for link in soup.find_all("a", href=True):
            if isinstance(link, Tag):
                original_href = link["href"]
                # Simulate Gmail-style link tracking
                if profile.css_prefix == "gmail":
                    link["href"] = f"https://www.google.com/url?q={original_href}"
                    link["target"] = "_blank"

    def _add_css_prefix(self, soup: BeautifulSoup, prefix: str) -> None:
        """Add client-specific CSS prefix to elements."""
        for element in soup.find_all():
            if isinstance(element, Tag) and element.get("class"):
                classes = element["class"]
                prefixed_classes = [f"{prefix}_{cls}" for cls in classes]
                element["class"] = prefixed_classes

    def _remove_media_queries(self, soup: BeautifulSoup) -> None:
        """Remove media queries from style tags."""
        for style in soup.find_all("style"):
            if style.string:
                # Remove @media blocks
                cleaned_css = re.sub(
                    r"@media[^{]+\{[^{}]*\{[^}]*\}[^}]*\}",
                    "",
                    style.string,
                    flags=re.DOTALL,
                )
                style.string = cleaned_css

    def _enforce_max_width(self, soup: BeautifulSoup, max_width: int) -> None:
        """Enforce maximum width on tables and containers."""
        # Find main containers
        for table in soup.find_all("table"):
            if isinstance(table, Tag):
                width = table.get("width")
                if width:
                    if width.isdigit() and int(width) > max_width:
                        table["width"] = str(max_width)
                    elif width.endswith("%"):
                        table["width"] = "100%"

                # Also check style attribute
                style = table.get("style", "")
                if "width" in style:
                    # Simple width replacement
                    style = re.sub(r"width:\s*\d+px", f"width: {max_width}px", style)
                    table["style"] = style

    def _apply_viewport_styles(self, soup: BeautifulSoup, viewport_width: int) -> None:
        """Apply viewport-specific styles."""
        # Add viewport meta tag if missing
        head = soup.find("head")
        if not head:
            # Create head if missing
            head = soup.new_tag("head")
            if soup.html:
                soup.html.insert(0, head)
            else:
                soup.insert(0, head)

        if not soup.find("meta", {"name": "viewport"}):
            viewport_meta = soup.new_tag(
                "meta",
                attrs={
                    "name": "viewport",
                    "content": f"width={viewport_width}, initial-scale=1.0",
                },
            )
            head.append(viewport_meta)

    def get_client_limitations(self, client: str) -> Dict[str, bool]:
        """Get limitations for a specific email client."""
        if client not in self.client_profiles:
            return {}

        profile = self.client_profiles[client]

        return {
            "strips_classes": profile.strips_classes,
            "strips_ids": profile.strips_ids,
            "strips_styles": profile.strips_styles,
            "modifies_links": profile.modifies_links,
            "supports_media_queries": profile.supports_media_queries,
            "has_max_width": profile.max_width_enforced is not None,
            "supports_dark_mode": profile.dark_mode_support,
        }
