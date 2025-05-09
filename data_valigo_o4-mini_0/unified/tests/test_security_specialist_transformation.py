import pytest
from security_specialist.securedata.transformation import TransformationPipeline

def test_pipeline():
    pipeline = TransformationPipeline()
    pipeline.add(lambda x: x.strip())
    pipeline.add(lambda x: x.lower())
    assert pipeline.process('  Hello ') == 'hello'
