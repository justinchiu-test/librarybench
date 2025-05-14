from template_engine import TemplateEngine

def test_render_stream(tmp_path):
    tpl = tmp_path / "stream.html"
    tpl.write_text("{% for i in nums %}{{ i }},{% endfor %}")
    engine = TemplateEngine(str(tmp_path))
    nums = list(range(100))
    stream = engine.render_stream("stream.html", nums=nums)
    assert hasattr(stream, '__iter__')
    data = "".join(stream)
    expected = ",".join(str(i) for i in nums) + ","
    assert data == expected
