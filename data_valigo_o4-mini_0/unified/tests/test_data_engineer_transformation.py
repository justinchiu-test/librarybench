import pytest
from data_engineer.dataschema.transformation import TransformationPipeline

def test_pipeline():
    p = TransformationPipeline()
    p.add(lambda x: x.strip())
    p.add(lambda x: x.lower())
    assert p.run('  ABC ') == 'abc'
    with pytest.raises(ValueError):
        p.add(123)
