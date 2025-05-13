from pipeline.core import Pipeline, Stage

class AddStage(Stage):
    def process(self, records):
        return [r+10 for r in records]

class MultStage(Stage):
    def process(self, records):
        return [r*2 for r in records]

def test_pipeline_sequential():
    p = Pipeline()
    p.add_stage(AddStage())
    p.add_stage(MultStage())
    out = p.run([1,2,3])
    assert out == [ (x+10)*2 for x in [1,2,3] ]

def test_pipeline_parallel():
    p = Pipeline(parallel=True, concurrency=2)
    p.add_stage(AddStage())
    p.add_stage(MultStage())
    out = p.run_async([1,2,3,4])
    assert sorted(out) == sorted([ (x+10)*2 for x in [1,2,3,4] ])
