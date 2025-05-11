import pytest
from unified.src.security_specialist import TransformationPipeline

def test_pipeline():
    pipeline = TransformationPipeline()
    pipeline.add(lambda x: x.strip())
    pipeline.add(lambda x: x.lower())
    assert pipeline.process('  Hello ') == 'hello'
