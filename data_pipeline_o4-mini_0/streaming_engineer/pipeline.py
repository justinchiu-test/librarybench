from backpressure_control import BackpressureControl
from memory_usage_control import MemoryUsageControl
from monitoring_metrics import MonitoringMetrics
from real_time_logging import get_logger
from dynamic_reconfiguration import DynamicReconfiguration

class Pipeline:
    def __init__(self):
        self.stages = []
        self.metrics = MonitoringMetrics()
        self.logger = get_logger('Pipeline')
        self.backpressure = None
        self.memory_control = None
        self.reconfig = DynamicReconfiguration()

    def add_stage(self, stage):
        self.stages.append(stage)

    def set_backpressure(self, backpressure_control):
        self.backpressure = backpressure_control

    def set_memory_control(self, memory_control):
        self.memory_control = memory_control

    def run(self, data_iterable):
        output = []
        queue = []
        for item in data_iterable:
            queue.append(item)
            if self.backpressure:
                self.backpressure.check()
            data = queue.pop(0)
            processed = data
            for stage in self.stages:
                self.logger.info(f'Processing item {processed} in stage {stage.name}')
                processed = stage.process(processed)
                self.metrics.inc_counter(f'{stage.name}_processed')
                if self.memory_control:
                    processed_list = self.memory_control.check_and_spill(len(str(processed).encode()), [processed])
                    if not processed_list:
                        processed = None
                    else:
                        processed = processed_list[0]
                if processed is None:
                    break
            if processed is not None:
                output.append(processed)
        return output

    def update_config(self, new_config):
        self.reconfig.update_config(new_config)
