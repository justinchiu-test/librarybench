"""Link tracking and UTM parameter injection."""

from typing import Dict, List, Optional
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from bs4 import BeautifulSoup, Tag
from pydantic import BaseModel, Field
import hashlib


class UTMParams(BaseModel):
    """UTM tracking parameters."""

    utm_source: str = Field(description="Traffic source (e.g., newsletter)")
    utm_medium: str = Field(description="Marketing medium (e.g., email)")
    utm_campaign: str = Field(description="Campaign name")
    utm_term: Optional[str] = Field(default=None, description="Campaign term")
    utm_content: Optional[str] = Field(default=None, description="Content identifier")


class LinkTrackingConfig(BaseModel):
    """Configuration for link tracking."""

    tracking_domain: Optional[str] = Field(
        default=None, description="Tracking redirect domain"
    )
    utm_params: Optional[UTMParams] = Field(
        default=None, description="Default UTM parameters"
    )
    track_all_links: bool = Field(
        default=True, description="Track all links by default"
    )
    exclude_domains: List[str] = Field(
        default_factory=list, description="Domains to exclude from tracking"
    )
    hash_urls: bool = Field(default=False, description="Hash URLs for security")
    preserve_anchors: bool = Field(default=True, description="Preserve URL anchors")


class TrackedLink(BaseModel):
    """Information about a tracked link."""

    original_url: str = Field(description="Original URL")
    tracked_url: str = Field(description="URL with tracking")
    link_id: str = Field(description="Unique link identifier")
    link_text: str = Field(description="Link text content")
    element_context: str = Field(description="Context where link appears")


class LinkTracker:
    """Handles link tracking and UTM parameter injection."""

    def __init__(self, config: Optional[LinkTrackingConfig] = None) -> None:
        self.config = config or LinkTrackingConfig()
        self.tracked_links: List[TrackedLink] = []
        self.last_utm_params: Optional[UTMParams] = None

    def track_links(self, html: str, custom_utm: Optional[UTMParams] = None) -> str:
        """
        Add tracking to all links in HTML.

        Args:
            html: HTML content with links
            custom_utm: Custom UTM parameters to override defaults

        Returns:
            HTML with tracked links
        """
        soup = BeautifulSoup(html, "html.parser")
        self.tracked_links = []

        # Get UTM parameters to use
        utm_params = custom_utm or self.config.utm_params
        self.last_utm_params = utm_params

        # Process all links
        for link in soup.find_all("a", href=True):
            if isinstance(link, Tag):
                original_url = link["href"]

                # Check if we should track this link
                if self._should_track_link(original_url):
                    tracked_url = self._create_tracked_url(
                        original_url, utm_params, link_element=link
                    )

                    # Store tracking information
                    self.tracked_links.append(
                        TrackedLink(
                            original_url=original_url,
                            tracked_url=tracked_url,
                            link_id=self._generate_link_id(original_url),
                            link_text=link.get_text(strip=True),
                            element_context=self._get_element_context(link),
                        )
                    )

                    # Update the link
                    link["href"] = tracked_url

        return str(soup)

    def _should_track_link(self, url: str) -> bool:
        """Determine if a link should be tracked."""
        if not self.config.track_all_links:
            return False

        # Skip non-HTTP URLs
        if not url.startswith(("http://", "https://")):
            return False

        # Check excluded domains
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        for excluded in self.config.exclude_domains:
            if excluded.lower() in domain:
                return False

        return True

    def _create_tracked_url(
        self,
        url: str,
        utm_params: Optional[UTMParams],
        link_element: Optional[Tag] = None,
    ) -> str:
        """Create a tracked version of a URL."""
        if self.config.tracking_domain:
            # Use redirect tracking
            return self._create_redirect_url(url, utm_params)
        else:
            # Add UTM parameters directly
            return self._add_utm_params(url, utm_params, link_element)

    def _create_redirect_url(self, url: str, utm_params: Optional[UTMParams]) -> str:
        """Create a tracking redirect URL."""
        tracking_domain = self.config.tracking_domain.rstrip("/")

        # Encode the destination URL
        if self.config.hash_urls:
            url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
            redirect_url = f"{tracking_domain}/track/{url_hash}"
        else:
            # Simple encoding
            from urllib.parse import quote

            redirect_url = f"{tracking_domain}/track?url={quote(url, safe='')}"

        # Add UTM parameters to redirect URL if provided
        if utm_params:
            redirect_url = self._add_utm_params(redirect_url, utm_params)

        return redirect_url

    def _add_utm_params(
        self,
        url: str,
        utm_params: Optional[UTMParams],
        link_element: Optional[Tag] = None,
    ) -> str:
        """Add UTM parameters to a URL."""
        if not utm_params:
            return url

        parsed = urlparse(url)
        query_params = parse_qs(parsed.query, keep_blank_values=True)

        # Add UTM parameters
        utm_dict = utm_params.model_dump(exclude_none=True)

        # Add dynamic content identifier if element provided and utm_content is None or empty
        if link_element and utm_params.utm_content is None:
            utm_dict["utm_content"] = self._generate_content_id(link_element)

        # Merge with existing parameters
        for key, value in utm_dict.items():
            if key.startswith("utm_"):
                query_params[key] = [value]

        # Rebuild URL
        new_query = urlencode(query_params, doseq=True)

        # Preserve anchor if configured
        anchor = parsed.fragment if self.config.preserve_anchors else ""

        return urlunparse(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                anchor,
            )
        )

    def _generate_link_id(self, url: str) -> str:
        """Generate unique ID for a link."""
        return hashlib.md5(url.encode()).hexdigest()[:8]

    def _generate_content_id(self, link_element: Tag) -> str:
        """Generate content ID based on link context."""
        # Try to find meaningful context
        # Check link's own classes first
        link_classes = link_element.get("class", [])
        if "button" in link_classes:
            return "cta_button"

        parent = link_element.parent

        if parent:
            # Check for common patterns
            if parent.name == "td" and "button" in parent.get("class", []):
                return "cta_button"
            elif parent.name in ["h1", "h2", "h3"]:
                return f"header_{parent.name}"
            elif "footer" in str(parent.get("class", [])):
                return "footer_link"

        # Default based on link text
        link_text = link_element.get_text(strip=True).lower()
        if any(word in link_text for word in ["buy", "shop", "order"]):
            return "shop_link"
        elif any(word in link_text for word in ["learn", "read", "more"]):
            return "content_link"

        return "general_link"

    def _get_element_context(self, link_element: Tag) -> str:
        """Get context description for a link element."""
        contexts = []

        # Check link classes
        if link_element.get("class"):
            contexts.append(f"classes: {' '.join(link_element['class'])}")

        # Check parent context
        parent = link_element.parent
        if parent:
            contexts.append(f"parent: {parent.name}")
            if parent.get("class"):
                contexts.append(f"parent_classes: {' '.join(parent['class'])}")

        return "; ".join(contexts) if contexts else "no_context"

    def get_tracking_report(self) -> Dict[str, any]:
        """Get report of all tracked links."""
        return {
            "total_links": len(self.tracked_links),
            "tracked_links": [link.model_dump() for link in self.tracked_links],
            "tracking_config": {
                "tracking_domain": self.config.tracking_domain,
                "utm_params": self.last_utm_params.model_dump()
                if self.last_utm_params
                else None,
                "excluded_domains": self.config.exclude_domains,
            },
        }

    def create_link_map(self) -> Dict[str, str]:
        """Create mapping of link IDs to original URLs."""
        return {link.link_id: link.original_url for link in self.tracked_links}
