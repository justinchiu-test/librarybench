from .monitor import MonitoringMetrics
from .logging import RealTimeLogger
from .checkpoint import CheckpointManager
from .plugins import PluginManager
from .backpressure import BackpressureController

class Stage:
    name = None
    def __call__(self, data, context):
        raise NotImplementedError

class Pipeline:
    def __init__(self):
        self.stages = []
        self.context = {
            'metrics': MonitoringMetrics(),
            'logger': RealTimeLogger(),
            'checkpoint': CheckpointManager(),
            'plugins': PluginManager(),
            'backpressure': BackpressureController()
        }
    def add_stage(self, stage):
        self.stages.append(stage)
    def remove_stage(self, stage_name):
        self.stages = [s for s in self.stages if getattr(s, 'name', None) != stage_name]
    def run(self, data):
        current = data
        for stage in self.stages:
            self.context['logger'].log({'stage_start': stage.name})
            try:
                current = stage(current, self.context)
            except Exception:
                if 'error_handler_fallback' in self.context:
                    current = self.context['error_handler_fallback'](current, self.context)
                else:
                    raise
            self.context['logger'].log({'stage_end': stage.name})
        return current
