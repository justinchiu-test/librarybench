import pytest
from unified.src.community_plugin_author import TransformationPipeline, mask

def test_transformation_pipeline():
    pipe = TransformationPipeline()
    pipe.add(lambda x: x.strip())
    pipe.add(lambda x: x.lower())
    assert pipe.apply("  Hello ") == "hello"

def test_mask_ssn_and_cc_and_hash():
    s = "123-45-6789"
    assert mask(s, 'ssn') == "***-**-6789"
    cc = "4111-1111-1111-1111"
    assert mask(cc, 'cc').endswith("1111")
    # other
    h = mask("foobar", 'other')
    assert isinstance(h, str) and len(h) == 64
