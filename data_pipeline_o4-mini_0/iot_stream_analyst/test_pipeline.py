from streamkit.pipeline import Pipeline

class StageAdd:
    def __init__(self, add):
        self.add = add
    def process(self, record):
        return record + self.add

class StageFilter:
    def process(self, record):
        if record % 2 == 0:
            return record
        return None

def test_pipeline_composition():
    p = Pipeline()
    p.add_stage(StageAdd(1))
    p.add_stage(StageFilter())
    result = p.process([1,2,3])
    # [1+1=2,2+1=3,3+1=4] then filter evens -> [2,4]
    assert result == [2,4]
