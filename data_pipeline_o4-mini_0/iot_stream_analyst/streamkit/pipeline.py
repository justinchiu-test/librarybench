class Pipeline:
    def __init__(self):
        self.stages = []

    def add_stage(self, stage):
        self.stages.append(stage)

    def process(self, records):
        data = list(records)
        for stage in self.stages:
            new_data = []
            for record in data:
                out = stage.process(record)
                if out is not None:
                    new_data.append(out)
            data = new_data
        return data
