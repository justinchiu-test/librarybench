from adapters.ops_engineer.cli_toolkit.publisher import publish_package

def test_publish_success():
    assert publish_package("dist/mypkg.whl") is True

def test_publish_failure():
    assert publish_package("") is False