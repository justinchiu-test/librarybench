"""
Data scientist datapipeline CLI toolkit.
Provides data pipeline-specific CLI tools and extensions.
"""

# Import core components to make them accessible through the persona namespace
from ....core.config.parser import ConfigParser
from ....core.config.schema import ConfigSchema
from ....core.config.validator import ConfigValidator
from ....core.commands.registry import CommandRegistry, Command, CommandGroup
from ....core.commands.help import HelpFormatter, FormatStyle
from ....core.infra.di import DependencyInjector, inject
from ....core.infra.secrets import SecretManager
from ....core.infra.signals import SignalHandler
from ....core.i18n.manager import I18nManager
from ....core.dev.version import VersionManager, Version
from ....core.dev.scaffold import Scaffolder
from ....core.dev.publish import Publisher

# Import persona-specific components
from .config_parser import DataPipelineConfigParser
from .commands import register_datapipeline_commands

# Version of the data_scientist package
__version__ = "1.0.0"