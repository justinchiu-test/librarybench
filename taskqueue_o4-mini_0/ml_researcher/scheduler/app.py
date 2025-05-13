from .api import RestAPI
from .control import ConcurrencyControl
from .backends import LocalRunner
from .metrics import MetricsExporter
from .config import ConfigManager
from .plugins import PluginRegistry
from .auth import RoleBasedAccessControl
from .dag import visualize
from .dlq import DeadLetterQueue
from .cron import CronScheduler

class SchedulerApp:
    def __init__(self):
        self.config = ConfigManager()
        self.control = ConcurrencyControl()
        self.backend = LocalRunner()
        self.metrics = MetricsExporter()
        self.auth = RoleBasedAccessControl()
        self.plugins = PluginRegistry()
        self.dlq = DeadLetterQueue()
        self.cron = CronScheduler()
        self.api = RestAPI(self.control, self.backend, self.metrics, self.auth)
    def visualize_dag(self, nodes, edges):
        return visualize(nodes, edges)
    def reload_config(self, new_config):
        self.config.update(new_config)
