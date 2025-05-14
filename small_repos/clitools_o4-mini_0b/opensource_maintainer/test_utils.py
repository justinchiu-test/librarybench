import re
from osscli.utils import compute_default
def test_compute_defaults():
    assert compute_default("build_dir") == "build"
    docs = compute_default("docs_dir")
    assert re.match(r"docs_\d{8}", docs)
    token = compute_default("token")
    assert isinstance(token, str) and len(token) == 16
    assert compute_default("other") is None
