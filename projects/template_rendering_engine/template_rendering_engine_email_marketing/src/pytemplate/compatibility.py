"""Email client compatibility validation."""

from typing import Dict, List, Optional, Set
from bs4 import BeautifulSoup, Tag
from pydantic import BaseModel, Field


class CompatibilityIssue(BaseModel):
    """Represents a compatibility issue found in email HTML."""

    severity: str = Field(description="Issue severity: error, warning, info")
    client: str = Field(description="Affected email client")
    element: Optional[str] = Field(
        default=None, description="HTML element or CSS property"
    )
    description: str = Field(description="Description of the issue")
    suggestion: Optional[str] = Field(default=None, description="Suggested fix")
    line_number: Optional[int] = Field(
        default=None, description="Line number if available"
    )


class EmailClientRules(BaseModel):
    """Rules for a specific email client."""

    name: str = Field(description="Email client name")
    unsupported_elements: Set[str] = Field(
        default_factory=set, description="Unsupported HTML elements"
    )
    unsupported_css: Set[str] = Field(
        default_factory=set, description="Unsupported CSS properties"
    )
    partial_support_css: Dict[str, str] = Field(
        default_factory=dict, description="CSS with partial support"
    )
    max_width: Optional[int] = Field(
        default=None, description="Maximum recommended width"
    )
    special_rules: Dict[str, str] = Field(
        default_factory=dict, description="Special validation rules"
    )


class EmailClientValidator:
    """Validates HTML for email client compatibility."""

    def __init__(self) -> None:
        self.clients = self._initialize_client_rules()

    def _initialize_client_rules(self) -> Dict[str, EmailClientRules]:
        """Initialize email client compatibility rules."""
        return {
            "outlook": EmailClientRules(
                name="Outlook",
                unsupported_elements={"video", "audio", "canvas", "svg", "form"},
                unsupported_css={
                    "position",
                    "float",
                    "clear",
                    "transform",
                    "animation",
                    "flex",
                    "grid",
                    "calc",
                    "min-width",
                    "max-width",
                    "min-height",
                    "max-height",
                    "overflow",
                },
                partial_support_css={
                    "margin": "May not work on all elements",
                    "padding": "Use with caution on <p> and <div>",
                    "background-image": "May not display in some versions",
                },
                max_width=600,
                special_rules={
                    "vml": "Use VML for background images",
                    "conditional": "Use conditional comments for Outlook-specific code",
                },
            ),
            "gmail": EmailClientRules(
                name="Gmail",
                unsupported_elements={"form", "script"},
                unsupported_css={
                    "position",
                    "float",
                    "clear",
                    "transform",
                    "animation",
                    "transition",
                    "calc",
                },
                partial_support_css={
                    "class": "Classes may be stripped in some views",
                    "id": "IDs may be modified",
                    "media-query": "Not supported in GANGA (Gmail mobile)",
                },
                max_width=600,
                special_rules={
                    "embedded-css": "CSS must be inlined for best support",
                    "attribute-selectors": "Not supported",
                },
            ),
            "apple-mail": EmailClientRules(
                name="Apple Mail",
                unsupported_elements={"form"},
                unsupported_css={"filter"},
                partial_support_css={
                    "border-radius": "Supported but may render differently",
                    "box-shadow": "Supported with -webkit- prefix",
                },
                max_width=None,
                special_rules={
                    "webkit-prefix": "Use -webkit- prefix for some CSS3 properties",
                    "dark-mode": "Supports dark mode media queries",
                },
            ),
        }

    def validate(
        self, html: str, target_clients: Optional[List[str]] = None
    ) -> List[CompatibilityIssue]:
        """
        Validate HTML for email client compatibility.

        Args:
            html: HTML content to validate
            target_clients: List of client names to validate against (default: all)

        Returns:
            List of compatibility issues found
        """
        issues = []
        soup = BeautifulSoup(html, "html.parser")

        # Select target clients
        clients_to_check = target_clients or list(self.clients.keys())

        for client_name in clients_to_check:
            if client_name in self.clients:
                client_rules = self.clients[client_name]
                issues.extend(self._validate_client(soup, client_rules))

        # General email best practices
        issues.extend(self._validate_general_practices(soup))

        return issues

    def _validate_client(
        self, soup: BeautifulSoup, rules: EmailClientRules
    ) -> List[CompatibilityIssue]:
        """Validate against specific client rules."""
        issues = []

        # Check unsupported elements
        for element_name in rules.unsupported_elements:
            elements = soup.find_all(element_name)
            for element in elements:
                issues.append(
                    CompatibilityIssue(
                        severity="error",
                        client=rules.name,
                        element=element_name,
                        description=f"<{element_name}> element is not supported",
                        suggestion=f"Remove <{element_name}> or use alternative approach",
                    )
                )

        # Check CSS properties
        for element in soup.find_all(style=True):
            if isinstance(element, Tag):
                style = element.get("style", "")
                issues.extend(self._validate_inline_css(style, rules))

        # Check style tags if Gmail
        if rules.name == "Gmail" and soup.find_all("style"):
            issues.append(
                CompatibilityIssue(
                    severity="warning",
                    client=rules.name,
                    element="style",
                    description="<style> tags may be stripped in some Gmail views",
                    suggestion="Inline all CSS for maximum compatibility",
                )
            )

        # Check width
        if rules.max_width:
            tables = soup.find_all("table")
            for table in tables:
                if isinstance(table, Tag):
                    width = table.get("width")
                    if width and width.isdigit() and int(width) > rules.max_width:
                        issues.append(
                            CompatibilityIssue(
                                severity="warning",
                                client=rules.name,
                                element="table",
                                description=f"Table width {width}px exceeds recommended {rules.max_width}px",
                                suggestion=f"Use maximum width of {rules.max_width}px",
                            )
                        )

        return issues

    def _validate_inline_css(
        self, style: str, rules: EmailClientRules
    ) -> List[CompatibilityIssue]:
        """Validate inline CSS against client rules."""
        issues = []

        # Parse CSS properties
        properties = {}
        for declaration in style.split(";"):
            if ":" in declaration:
                prop, value = declaration.split(":", 1)
                properties[prop.strip().lower()] = value.strip()

        # Check unsupported properties
        for prop, value in properties.items():
            if prop in rules.unsupported_css:
                issues.append(
                    CompatibilityIssue(
                        severity="error",
                        client=rules.name,
                        element=f"CSS: {prop}",
                        description=f'CSS property "{prop}" is not supported',
                        suggestion=f'Remove "{prop}" or use alternative approach',
                    )
                )
            elif prop in rules.partial_support_css:
                issues.append(
                    CompatibilityIssue(
                        severity="warning",
                        client=rules.name,
                        element=f"CSS: {prop}",
                        description=f'CSS property "{prop}" has limited support',
                        suggestion=rules.partial_support_css[prop],
                    )
                )

            # Special checks for specific property values
            if (
                prop == "display"
                and value in ["flex", "grid"]
                and value in rules.unsupported_css
            ):
                issues.append(
                    CompatibilityIssue(
                        severity="error",
                        client=rules.name,
                        element=f"CSS: {value}",
                        description=f'CSS display value "{value}" is not supported',
                        suggestion=f"Use table-based layout instead of {value}",
                    )
                )

        return issues

    def _validate_general_practices(
        self, soup: BeautifulSoup
    ) -> List[CompatibilityIssue]:
        """Validate general email best practices."""
        issues = []

        # Check for doctype
        if not soup.find(
            string=lambda text: isinstance(text, str) and "DOCTYPE" in text
        ):
            issues.append(
                CompatibilityIssue(
                    severity="warning",
                    client="General",
                    element="DOCTYPE",
                    description="Missing DOCTYPE declaration",
                    suggestion="Add <!DOCTYPE html> for better rendering",
                )
            )

        # Check for meta viewport
        viewport = soup.find("meta", attrs={"name": "viewport"})
        if not viewport:
            issues.append(
                CompatibilityIssue(
                    severity="info",
                    client="General",
                    element="meta viewport",
                    description="Missing viewport meta tag",
                    suggestion='Add <meta name="viewport" content="width=device-width, initial-scale=1.0">',
                )
            )

        # Check for alt text on images
        images = soup.find_all("img")
        for img in images:
            if isinstance(img, Tag) and not img.get("alt"):
                issues.append(
                    CompatibilityIssue(
                        severity="warning",
                        client="General",
                        element="img",
                        description="Image missing alt text",
                        suggestion="Add alt attribute to all images for accessibility",
                    )
                )

        # Check for JavaScript
        if soup.find_all("script"):
            issues.append(
                CompatibilityIssue(
                    severity="error",
                    client="General",
                    element="script",
                    description="JavaScript is not supported in emails",
                    suggestion="Remove all <script> tags",
                )
            )

        # Check for external CSS
        link_tags = soup.find_all("link", rel="stylesheet")
        if link_tags:
            issues.append(
                CompatibilityIssue(
                    severity="error",
                    client="General",
                    element="link",
                    description="External stylesheets are not supported",
                    suggestion="Inline all CSS styles",
                )
            )

        return issues

    def get_supported_css(self, client: str) -> Set[str]:
        """Get list of supported CSS properties for a client."""
        if client not in self.clients:
            return set()

        all_css = {
            "background-color",
            "color",
            "font-family",
            "font-size",
            "font-weight",
            "text-align",
            "text-decoration",
            "line-height",
            "border",
            "padding",
            "margin",
            "width",
            "height",
        }

        return all_css - self.clients[client].unsupported_css
