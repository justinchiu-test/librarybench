"""
Data Scientist pipeline CLI modules.
"""
# Expose core functionalities and persona-specific modules
from .commands import main
from .config_parser import parse_config_files
from .config_schema import generate_schema
from .config_validator import validate_config
from .di import init_di, inject
from .i18n import load_translations
from .publish import publish_package
from .scaffold import gen_scaffold
from .secrets import manage_secrets
from .signals import handle_signals, _get_registered
from .help_formatter import format_help
from .version import get_version, bump_version, VERSION_FILE