"""Main template engine integrating all components."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import time

from .css_inliner import CSSInliner
from .personalization import PersonalizationEngine, PersonalizationConfig
from .ab_testing import ABTestGenerator, ABTestConfig
from .compatibility import EmailClientValidator, CompatibilityIssue
from .preview import PreviewRenderer, PreviewResult
from .text_generator import PlainTextGenerator, PlainTextConfig
from .link_tracking import LinkTracker, LinkTrackingConfig, UTMParams


class EmailTemplate(BaseModel):
    """Email template definition."""

    subject: str = Field(description="Email subject line with personalization tokens")
    content: str = Field(description="HTML content with personalization tokens")
    preheader: Optional[str] = Field(default=None, description="Preheader text")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Template metadata"
    )


class RenderConfig(BaseModel):
    """Configuration for rendering emails."""

    inline_css: bool = Field(default=True, description="Inline CSS styles")
    preserve_media_queries: bool = Field(
        default=True, description="Preserve media queries"
    )
    validate_compatibility: bool = Field(
        default=True, description="Run compatibility validation"
    )
    target_clients: List[str] = Field(
        default_factory=list, description="Target email clients"
    )
    generate_plain_text: bool = Field(
        default=True, description="Generate plain text version"
    )
    track_links: bool = Field(default=True, description="Enable link tracking")
    escape_html: bool = Field(
        default=True, description="HTML escape personalized content"
    )


class RenderedEmail(BaseModel):
    """Result of email rendering."""

    html: str = Field(description="Final HTML content")
    plain_text: Optional[str] = Field(default=None, description="Plain text version")
    subject: str = Field(description="Personalized subject")
    compatibility_issues: List[CompatibilityIssue] = Field(default_factory=list)
    tracked_links: List[Dict[str, Any]] = Field(default_factory=list)
    render_time: float = Field(description="Rendering time in seconds")
    variant_id: Optional[str] = Field(default=None, description="A/B test variant ID")


class TemplateEngine:
    """Main engine for rendering email templates."""

    def __init__(
        self,
        personalization_config: Optional[PersonalizationConfig] = None,
        link_tracking_config: Optional[LinkTrackingConfig] = None,
        plain_text_config: Optional[PlainTextConfig] = None,
    ) -> None:
        # Initialize components
        self.css_inliner = CSSInliner()
        self.personalization = PersonalizationEngine(personalization_config)
        self.ab_generator = ABTestGenerator()
        self.validator = EmailClientValidator()
        self.preview_renderer = PreviewRenderer()
        self.text_generator = PlainTextGenerator(plain_text_config)
        self.link_tracker = LinkTracker(link_tracking_config)

    def render_email(
        self,
        template: EmailTemplate,
        recipient_data: Dict[str, Any],
        config: Optional[RenderConfig] = None,
        utm_params: Optional[UTMParams] = None,
    ) -> RenderedEmail:
        """
        Render a single email for a recipient.

        Args:
            template: Email template
            recipient_data: Personalization data for recipient
            config: Render configuration
            utm_params: UTM tracking parameters

        Returns:
            Rendered email
        """
        start_time = time.time()
        config = config or RenderConfig()

        # Personalize content
        html = self.personalization.personalize(template.content, recipient_data)
        subject = self.personalization.personalize(template.subject, recipient_data)

        # Add preheader if provided
        if template.preheader:
            preheader = self.personalization.personalize(
                template.preheader, recipient_data
            )
            html = self._add_preheader(html, preheader)

        # Inline CSS if requested
        if config.inline_css:
            html = self.css_inliner.inline_css(
                html, preserve_media_queries=config.preserve_media_queries
            )

        # Track links if requested
        tracked_links = []
        if config.track_links:
            html = self.link_tracker.track_links(html, utm_params)
            tracked_links = [
                link.model_dump() for link in self.link_tracker.tracked_links
            ]

        # Validate compatibility
        compatibility_issues = []
        if config.validate_compatibility:
            compatibility_issues = self.validator.validate(
                html,
                target_clients=config.target_clients if config.target_clients else None,
            )

        # Generate plain text
        plain_text = None
        if config.generate_plain_text:
            plain_text = self.text_generator.generate_plain_text(html)

        render_time = time.time() - start_time

        return RenderedEmail(
            html=html,
            plain_text=plain_text,
            subject=subject,
            compatibility_issues=compatibility_issues,
            tracked_links=tracked_links,
            render_time=render_time,
        )

    def render_bulk(
        self,
        template: EmailTemplate,
        recipients_data: List[Dict[str, Any]],
        config: Optional[RenderConfig] = None,
        utm_params: Optional[UTMParams] = None,
    ) -> List[RenderedEmail]:
        """
        Render emails for multiple recipients.

        Args:
            template: Email template
            recipients_data: List of personalization data for each recipient
            config: Render configuration
            utm_params: UTM tracking parameters

        Returns:
            List of rendered emails
        """
        rendered_emails = []

        for recipient_data in recipients_data:
            rendered = self.render_email(template, recipient_data, config, utm_params)
            rendered_emails.append(rendered)

        return rendered_emails

    def render_ab_test(
        self,
        base_template: Dict[str, Any],
        ab_config: ABTestConfig,
        recipient_data: Dict[str, Any],
        render_config: Optional[RenderConfig] = None,
        utm_params: Optional[UTMParams] = None,
    ) -> List[RenderedEmail]:
        """
        Render A/B test variants for a recipient.

        Args:
            base_template: Base template structure
            ab_config: A/B test configuration
            recipient_data: Personalization data
            render_config: Render configuration
            utm_params: UTM tracking parameters

        Returns:
            List of rendered variants
        """
        # Generate variants
        variants = self.ab_generator.generate_variants(base_template, ab_config)

        # Render each variant
        rendered_variants = []
        for variant in variants:
            template = EmailTemplate(subject=variant.subject, content=variant.content)

            rendered = self.render_email(
                template, recipient_data, render_config, utm_params
            )
            rendered.variant_id = variant.variant_id
            rendered_variants.append(rendered)

        return rendered_variants

    def generate_previews(
        self,
        template: EmailTemplate,
        sample_data: Dict[str, Any],
        clients: Optional[List[str]] = None,
    ) -> List[PreviewResult]:
        """
        Generate previews for different email clients.

        Args:
            template: Email template
            sample_data: Sample personalization data
            clients: List of clients to preview (default: all)

        Returns:
            List of preview results
        """
        # First render the email with sample data
        rendered = self.render_email(
            template, sample_data, RenderConfig(validate_compatibility=False)
        )

        # Generate previews
        if clients:
            previews = []
            for client in clients:
                preview = self.preview_renderer.render_preview(rendered.html, client)
                previews.append(preview)
            return previews
        else:
            return self.preview_renderer.render_all_previews(rendered.html)

    def validate_template(
        self, template: EmailTemplate, sample_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate a template with sample data.

        Args:
            template: Email template to validate
            sample_data: Sample personalization data

        Returns:
            Validation results
        """
        # Extract and validate personalization tokens
        content_tokens = self.personalization.extract_tokens(template.content)
        subject_tokens = self.personalization.extract_tokens(template.subject)

        all_tokens = {**content_tokens, **subject_tokens}

        # Validate data availability
        content_validation = self.personalization.validate_data(
            template.content, sample_data
        )
        subject_validation = self.personalization.validate_data(
            template.subject, sample_data
        )

        # Try rendering to catch any errors
        try:
            rendered = self.render_email(template, sample_data)
            render_success = True
            render_error = None
        except Exception as e:
            render_success = False
            render_error = str(e)

        return {
            "tokens": {
                "content": content_tokens,
                "subject": subject_tokens,
                "all": all_tokens,
            },
            "validation": {
                "content": content_validation,
                "subject": subject_validation,
            },
            "render_test": {
                "success": render_success,
                "error": render_error,
                "compatibility_issues": rendered.compatibility_issues
                if render_success
                else [],
            },
        }

    def _add_preheader(self, html: str, preheader: str) -> str:
        """Add preheader text to HTML."""
        # Create hidden preheader div
        preheader_html = f"""
        <div class="preheader" style="display: none !important; visibility: hidden; mso-hide: all; font-size: 1px; line-height: 1px; max-height: 0; max-width: 0; opacity: 0; overflow: hidden;">
            {preheader}
        </div>
        """

        # Insert after opening body tag
        if "<body" in html:
            # Find the end of the body tag
            body_start = html.find("<body")
            body_end = html.find(">", body_start)
            return html[: body_end + 1] + preheader_html + html[body_end + 1 :]
        else:
            # Just prepend if no body tag
            return preheader_html + html
