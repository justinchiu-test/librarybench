"""PyTemplate - Email Template Rendering Engine for Marketing Campaigns."""

from .css_inliner import CSSInliner
from .personalization import PersonalizationEngine
from .ab_testing import ABTestGenerator
from .compatibility import EmailClientValidator
from .preview import PreviewRenderer
from .text_generator import PlainTextGenerator
from .link_tracking import LinkTracker
from .template_engine import TemplateEngine, EmailTemplate, RenderConfig, RenderedEmail

__version__ = "0.1.0"

__all__ = [
    "CSSInliner",
    "PersonalizationEngine",
    "ABTestGenerator",
    "EmailClientValidator",
    "PreviewRenderer",
    "PlainTextGenerator",
    "LinkTracker",
    "TemplateEngine",
    "EmailTemplate",
    "RenderConfig",
    "RenderedEmail",
]
