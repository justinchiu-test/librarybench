from configgen import minify

def test_minify_empty():
    assert minify("") == ""
