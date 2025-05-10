from osscli.publish_package import publish_package
def test_publish_package():
    out = publish_package(to_pypi=False, to_github=True)
    assert out == {"pypi": False, "github": True}
