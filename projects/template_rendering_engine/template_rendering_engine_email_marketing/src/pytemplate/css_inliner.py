"""CSS Inliner for email-safe HTML generation."""

import re
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup, Tag
import cssutils
from cssutils import css
import logging

cssutils.log.setLevel(logging.ERROR)


class CSSInliner:
    """Converts CSS styles to inline styles for email compatibility."""

    def __init__(self) -> None:
        self.parser = cssutils.CSSParser()

    def inline_css(self, html: str, preserve_media_queries: bool = True) -> str:
        """
        Convert CSS to inline styles while optionally preserving media queries.

        Args:
            html: HTML content with style tags or linked stylesheets
            preserve_media_queries: Whether to preserve media queries in style tag

        Returns:
            HTML with inlined CSS
        """
        soup = BeautifulSoup(html, "html.parser")

        # Extract all CSS rules
        css_rules = self._extract_css_rules(soup)

        # Apply CSS rules to elements
        self._apply_css_rules(soup, css_rules)

        # Handle media queries if needed
        if preserve_media_queries:
            self._preserve_media_queries(soup, css_rules)

        # Remove processed style tags
        for style_tag in soup.find_all("style"):
            if not preserve_media_queries or not self._has_media_queries(
                style_tag.string
            ):
                style_tag.decompose()

        return str(soup)

    def _extract_css_rules(
        self, soup: BeautifulSoup
    ) -> List[Tuple[str, Dict[str, str], int]]:
        """Extract CSS rules from style tags."""
        rules = []

        for style_tag in soup.find_all("style"):
            if style_tag.string:
                try:
                    stylesheet = self.parser.parseString(style_tag.string)
                    for rule in stylesheet:
                        if isinstance(rule, css.CSSStyleRule):
                            selector = rule.selectorText
                            styles = self._parse_style_declaration(rule.style)
                            specificity = self._calculate_specificity(selector)
                            rules.append((selector, styles, specificity))
                except Exception:
                    # Skip invalid CSS
                    pass

        # Sort by specificity (higher specificity last to override)
        rules.sort(key=lambda x: x[2])

        return rules

    def _parse_style_declaration(
        self, style: css.CSSStyleDeclaration
    ) -> Dict[str, str]:
        """Parse CSS style declaration into a dictionary."""
        styles = {}
        for prop in style:
            styles[prop.name] = prop.value
        return styles

    def _calculate_specificity(self, selector: str) -> int:
        """Calculate CSS selector specificity for proper cascade ordering."""
        # Simplified specificity calculation
        id_count = selector.count("#")
        class_count = selector.count(".") + selector.count("[") + selector.count(":")
        element_count = len(
            re.findall(r"\b[a-zA-Z]+\b", selector.replace(".", " ").replace("#", " "))
        )

        return (id_count * 100) + (class_count * 10) + element_count

    def _apply_css_rules(
        self, soup: BeautifulSoup, rules: List[Tuple[str, Dict[str, str], int]]
    ) -> None:
        """Apply CSS rules to matching elements."""
        # Track styles for each element to handle specificity correctly
        element_styles = {}

        for selector, styles, specificity in rules:
            try:
                # Handle basic selectors
                elements = soup.select(selector)
                for element in elements:
                    if isinstance(element, Tag):
                        # Create a unique key for the element
                        elem_id = id(element)
                        if elem_id not in element_styles:
                            element_styles[elem_id] = {"element": element, "rules": []}

                        # Add this rule with its specificity
                        element_styles[elem_id]["rules"].append((styles, specificity))
            except Exception:
                # Skip invalid selectors
                pass

        # Apply accumulated styles to elements
        for elem_data in element_styles.values():
            element = elem_data["element"]
            # Sort rules by specificity
            elem_data["rules"].sort(key=lambda x: x[1])

            # Apply styles in order of specificity
            final_styles = self._parse_inline_style(element.get("style", ""))
            for styles, _ in elem_data["rules"]:
                final_styles.update(styles)

            element["style"] = self._build_style_string(final_styles)

    def _parse_inline_style(self, style_string: str) -> Dict[str, str]:
        """Parse inline style string into dictionary."""
        styles = {}
        if style_string:
            for declaration in style_string.split(";"):
                if ":" in declaration:
                    prop, value = declaration.split(":", 1)
                    styles[prop.strip()] = value.strip()
        return styles

    def _build_style_string(self, styles: Dict[str, str]) -> str:
        """Build inline style string from dictionary."""
        return "; ".join(f"{prop}: {value}" for prop, value in styles.items())

    def _has_media_queries(self, css_text: Optional[str]) -> bool:
        """Check if CSS contains media queries."""
        return bool(css_text and "@media" in css_text)

    def _preserve_media_queries(
        self, soup: BeautifulSoup, rules: List[Tuple[str, Dict[str, str], int]]
    ) -> None:
        """Preserve media queries in a separate style tag."""
        media_queries = []

        for style_tag in soup.find_all("style"):
            if style_tag.string and "@media" in style_tag.string:
                # Extract media queries
                media_query_pattern = r"@media[^{]+\{[^{}]*\{[^}]*\}[^}]*\}"
                matches = re.findall(media_query_pattern, style_tag.string, re.DOTALL)
                media_queries.extend(matches)

        if media_queries:
            # Create new style tag with only media queries
            new_style = soup.new_tag("style")
            new_style.string = "\n".join(media_queries)
            if soup.head:
                soup.head.append(new_style)
            else:
                soup.insert(0, new_style)
