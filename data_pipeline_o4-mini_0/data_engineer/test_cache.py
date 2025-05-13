from pipeline.cache import CachingStage

def test_caching_stage():
    stage = CachingStage(lambda r: r)
    data = [1,2,1,3,2]
    out = stage.process(data)
    assert out == [1,2,1,3,2]
