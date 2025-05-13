from .plugin_system import PluginSystem

class Pipeline:
    def __init__(self, stages=None):
        self.stages = stages or []
        self.errors = []

    def add_stage(self, stage):
        self.stages.append(stage)
        return self

    def __add__(self, other):
        return Pipeline(self.stages + other.stages)

    def run(self, input_data=None):
        # Determine initial records
        if self.stages and hasattr(self.stages[0], 'read'):
            records = self.stages[0].read()
            start = 1
        else:
            records = iter(input_data or [])
            start = 0
        # Process through stages
        for stage in self.stages[start:]:
            if hasattr(stage, 'process'):
                new_records = []
                for record in records:
                    try:
                        result = stage.process(record)
                        if result is not None:
                            new_records.append(result)
                    except Exception as e:
                        self.errors.append((stage, record, e))
                records = new_records
            elif hasattr(stage, 'write'):
                for record in records:
                    try:
                        stage.write(record)
                    except Exception as e:
                        self.errors.append((stage, record, e))
                return
        # If no sink, return remaining records
        return list(records)
