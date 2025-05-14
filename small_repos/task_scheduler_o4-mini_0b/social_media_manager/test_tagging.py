from postscheduler.tagging import add_tag

def test_add_tag():
    task = {"name": "post1"}
    res = add_tag(task, "SpringSale")
    assert "tags" in res
    assert "SpringSale" in res["tags"]
    # adding another
    res = add_tag(task, "video")
    assert res["tags"] == ["SpringSale", "video"]
